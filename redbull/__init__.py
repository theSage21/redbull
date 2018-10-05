try:
    import bottle
except ImportError:
    bottle = None
try:
    from aiohttp import web as aioweb
except ImportError:
    aioweb = None
from inspect import signature, _empty
from functools import wraps
from typing import get_type_hints
from .doc_html import gen_doc_html


def cors_dict__(origin=None):
    "Generate a CORS header string given the origin"
    origin = '*' if origin is None else origin
    cors_string = 'Origin, Accept , Content-Type, X-Requested-With, X-CSRF-Token'
    CORS_HEADERS = {'Access-Control-Allow-Methods': 'POST, OPTIONS, GET',
                    'Access-Control-Allow-Headers': cors_string,
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Allow-Origin': origin}
    return CORS_HEADERS


def bottleabort__(code=500, text='Unknown Error.'):
    " Aborts execution and causes a HTTP error while adding CORS "
    origin = bottle.request.headers.get('Origin')
    d = cors_dict__(origin)
    raise bottle.HTTPError(code, text, **d)


def bottle_add_cors__(app, allow_credentials=True):
    @app.hook('after_request')
    def add_cors_headers():
        origin = bottle.request.headers.get('Origin')
        d = cors_dict__(origin)
        bottle.response.headers.update(d)

    def docstring_fn(fn, method):
        def newfn():
            return method + '\n' + fn.__doc__
        return newfn

    new_routes = []
    for route in app.routes:
        if route.method != 'OPTIONS':
            new_routes.append((route.rule, docstring_fn(route.callback,
                                                        route.method)))
    for r, fn in new_routes:
        app.route(r, method=['OPTIONS'])(fn)

    return app


class WrongJson(Exception):
    "Wrong JSON was provided"
    pass


class Manager:
    def __init__(self, app=None, *, apiversion='1'):
        if app is None:
            app = bottle.Bottle()
            if bottle is None:
                print('Either provide a framework or install Bottle')

        self.app = app
        if bottle is not None and isinstance(app, bottle.Bottle):
            self.kind = 'bottle'
        elif aioweb is not None and isinstance(app, aioweb.Application):
            self.kind = 'aio'
        else:
            msg = f'Unknown app type {type(app)}'
            raise Exception(msg)
        self.version = str(apiversion)

    def __get_args_from_json(self, json, anno, fsig):
        "Given Json, annotations, and a function signature validate it"
        args = {}
        # Ensure that all expected are provided
        for k, kind in anno.items():
            if k in json:  # They have provided
                if not isinstance(json[k], kind):  # Kind is wrong
                    raise WrongJson(f'Wrong type for "{k}"')
                else:
                    value = json[k]
            elif k in fsig.parameters and fsig.parameters[k].default != _empty:
                # They did not provide and default available
                value = fsig.parameters[k].default
            else:  # They did not provide and no default
                raise WrongJson(f'Please provide "{k}"')
            args[k] = value
        return args

    def __get_routes(self):
        "Return a standard iterator over the routes in the app"
        if self.kind == 'bottle':
            return [(r.rule, r.method, r.callback.__doc__)
                    for r in self.app.routes]
        elif self.kind == 'aio':
            return [(r.resource._path, r.method, r.handler.__doc__)
                    for r in self.app.router.routes()]

    def __add_post(self, route, function):
        if self.kind == 'bottle':
            fn = self.app.post(route)(function)
        elif self.kind == 'aio':
            fn = function  # no wrapping needed
            self.app.router.add_post(route, function)
        return fn

    def __build_wrapper(self, fn, pass_args):
        """
        Given a function, build it's wrapper which
        performs the JSON validation etc.
        """
        if not hasattr(fn, '__kwdefaults__'):
            raise Exception('''
            All defaults must be keyword args.
            Please use fn(_, *, a:int=0, b:int=10) in the definitions
            ''')

        anno = get_type_hints(fn)
        fsig = signature(fn)

        if self.kind == 'bottle':
            @wraps(fn)
            def newfn(*original_a, **original_kw):
                if bottle.request.json is None:
                    bottleabort__(415, 'Expected "application/json"')
                j = bottle.request.json
                try:
                    args = self.__get_args_from_json(j, anno, fsig)
                except WrongJson as e:
                    bottleabort__(400, str(e))
                if pass_args:
                    args['__args__'] = original_a
                    args['__kwargs__'] = original_kw
                ret = fn(**args)
                ret = 'ok' if ret is None else ret
                return ret
        elif self.kind == 'aio':
            @wraps(fn)
            async def newfn(*original_a, **original_kw):
                request = original_a[0]
                if request.content_type != 'application/json':
                    raise aioweb.HTTPUnsupportedMediaType(text='Expected "application/json"')
                j = await request.json()
                try:
                    args = self.__get_args_from_json(j, anno, fsig)
                except WrongJson as e:
                    raise aioweb.HTTPBadRequest(text=str(e))
                if pass_args:
                    args['__args__'] = original_a
                    args['__kwargs__'] = original_kw
                ret = await fn(**args)
                ret = 'ok' if ret is None else ret
                return aioweb.json_response(ret)
        doc = f'''
        {self.__make_uri(fn.__name__)}
        application/json
        ------------------------------

        {anno}

        ------------------------------

        {fn.__doc__}
        '''
        newfn.__doc__ = doc.replace('<', '&lt;').replace('>', '&gt;')
        return newfn

    def __make_uri(self, name):
        "Turn a function name into a URL"
        uri = name.replace('_', '/')
        uri = '/' + self.version + '/' + uri.lstrip('/')
        return uri

    def api(self, *, pass_args=False):
        "Register function as API"
        def api_wrapper(fn):
            uri = self.__make_uri(fn.__name__)
            fn = self.__build_wrapper(fn, pass_args)
            fn = self.__add_post(uri, fn)
            return fn
        return api_wrapper

    def __add_cors(self, **kw):
        if self.kind == 'bottle':
            self.app = bottle_add_cors__(self.app, **kw)
        elif self.kind == 'aio':

            def docfn(doc, method):
                async def fn(request):
                    origin = request.headers.get('Origin')
                    h = cors_dict__(origin)
                    return aioweb.Response(text=f'{method}\n{doc}',
                                           headers=h)
                return fn

            for rule, method, doc in self.__get_routes():
                try:
                    self.app.router.add_route('OPTIONS', rule, docfn(doc, method))
                except RuntimeError:
                    pass
        return self.app

    def __add_docs(self):
        api_list = list(sorted([url for url, method, _ in self.__get_routes()]))
        if self.kind == 'bottle':
            @self.app.get(f'/{self.version}/docs')
            def docs():
                return gen_doc_html(self.version, api_list)
        elif self.kind == 'aio':
            async def docgen(request):
                return aioweb.Response(text=gen_doc_html(self.version, api_list),
                                       content_type='text/html')

            self.app.router.add_get(f'/{self.version}/docs', docgen)

    def finalize(self):
        self.__add_docs()
        self.__add_cors()

    def finalise(self):
        self.finalize()

    def run(self, **kw):
        self.finalize()
        if self.kind == 'bottle':
            self.app.run(**kw)
        elif self.kind == 'aio':
            aioweb.run_app(self.app, **kw)
