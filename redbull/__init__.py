try:
    import bottle
    from bottlecors import add_cors, abort
except ImportError:
    bottle = None
try:
    from aiohttp import web as aioweb
except ImportError:
    aioweb = None
from inspect import signature, _empty
from functools import wraps
from typing import get_type_hints


class WrongJson(Exception):
    pass


class Manager:
    def __init__(self, app, *, apiversion='1'):
        self.app = app
        if bottle is not None and isinstance(app, bottle.Bottle):
            self.kind = 'bottle'
        elif aioweb is not None and isinstance(app, aioweb.Application):
            self.kind = 'aio'
        else:
            raise Exception('Unknown app framework')
        self.version = str(apiversion)

    def __get_args_from_json(self, json, anno, fsig):
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
            fn = function
            self.app.router.add_post(route, function)
        return fn

    def __build_wrapper(self, fn):
        if not hasattr(fn, '__kwdefaults__'):
            raise Exception('''
            All defaults must be keyword args.
            Please use fn(_, *, a:int=0, b:int=10) in the definitions
            ''')

        anno = get_type_hints(fn)
        fsig = signature(fn)

        if self.kind == 'bottle':
            @wraps(fn)
            def newfn():
                if bottle.request.json is None:
                    abort(415, 'Expected "application/json"')
                j = bottle.request.json
                try:
                    args = self.__get_args_from_json(j, anno, fsig)
                except WrongJson as e:
                    abort(400, str(e))
                ret = fn(**args)
                ret = 'ok' if ret is None else ret
                return ret
        elif self.kind == 'aio':
            @wraps(fn)
            async def newfn(request):
                if request.content_type != 'application/json':
                    raise aioweb.HTTPUnsupportedMediaType(text='Expected "application/json"')
                j = await request.json()
                try:
                    args = self.__get_args_from_json(j, anno, fsig)
                except WrongJson as e:
                    raise aioweb.HTTPBadRequest(text=str(e))
                ret = await fn(**args)
                ret = 'ok' if ret is None else ret
                return aioweb.json_response(ret)

        doc = f'''
        POST application/json
        ==============================

        {anno}

        ==============================
        {fn.__doc__}
        '''
        newfn.__doc__ = doc
        return newfn

    def api(self, fn):
        uri = fn.__name__.replace('_', '/')
        uri = '/' + self.version + '/' + uri.lstrip('/')
        fn = self.__build_wrapper(fn)
        fn = self.__add_post(uri, fn)
        return fn

    def add_cors(self, **kw):
        if self.kind == 'bottle':
            self.app = add_cors(self.app, **kw)
        elif self.kind == 'aio':

            def docfn(doc):
                async def fn(request):
                    return aioweb.Response(text=doc)
                return fn

            for rule, method, doc in self.__get_routes():
                self.app.router.add_route('OPTIONS', rule, docfn(doc))

        for rule, method, _ in self.__get_routes():
            print(method, rule)

        return self.app
