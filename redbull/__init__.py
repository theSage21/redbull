import bottle
from inspect import signature, _empty
from functools import wraps
from typing import get_type_hints
from bottlecors import add_cors, abort


class Manager:
    def __init__(self, bottleapp, *, apiversion='1'):
        self.app = bottleapp
        self.version = str(apiversion)

    def __create_protected_function(self, fn):
        if not hasattr(fn, '__kwdefaults__'):
            raise Exception('''
            All defaults must be keyword args.
            Please use fn(_, *, a:int=0, b:int=10) in the definitions
            ''')

        anno = get_type_hints(fn)
        print(anno)
        fsig = signature(fn)

        @wraps(fn)
        def newfn():
            if not hasattr(bottle.request, 'json'):
                abort(415, 'Expected "application/json"')
            j = bottle.request.json
            args = {}
            # Ensure that all expected are provided
            for k, kind in anno.items():
                if k in j:  # They have provided
                    if not isinstance(j[k], kind):  # Kind is wrong
                        abort(400, f'Wrong type for "{k}"')
                    else:
                        value = j[k]
                elif k in fsig.parameters and fsig.parameters[k].default != _empty:
                    # They did not provide and default available
                    value = fsig.parameters[k].default
                else:  # They did not provide and no default
                    abort(400, f'Please provide "{k}"')
                args[k] = value
            return fn(**args)

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
        fn = self.__create_protected_function(fn)
        fn = self.app.post(uri)(fn)
        return fn

    def add_cors(self, **kw):
        apidocstrings = {}
        for route in self.app.routes:
            apidocstrings[route.rule, route.method] = route.callback.__doc__
        self.app = add_cors(self.app, **kw)

        @self.app.get(f'/{self.version}/docs')
        def doc_fn():
            docs = f'''<html> <body> <h1> API Docs version {self.version}</h1>'''
            docs += '''Calling each API with the OPTIONS method return's it's documentation'''
            for k, v in apidocstrings.items():
                docs += f'''<h2>{k[1]}  {k[0]}</h2><pre>{v}</pre><hr>'''
            docs += ''' </body> </html> '''
            return docs

        return self.app
