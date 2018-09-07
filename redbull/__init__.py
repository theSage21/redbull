import bottle
from bottlecors import add_cors, abort


class Manager:
    def __init__(self, bottleapp):
        self.app = bottleapp

    def api(self, fn):
        uri = fn.__name__.replace('_', '/')
        uri = '/' + uri.lstrip('/')
        fn = self.app.post(uri)(fn)
        return fn

    def add_cors(self, **kw):
        self.app = add_cors(self.app, **kw)
        return self.app

    def json_get(self, *keys, strict=False):
        if strict:
            self.ensure_keys(*keys)
        return [bottle.request.json.get(k) for k in keys]

    def ensure_keys(self, *keys):
        "Ensure that some keys are present in the JSON"
        jsn = bottle.request.json
        for key in keys:
            if key not in jsn:
                abort(400, f'"{key}" not provided')
