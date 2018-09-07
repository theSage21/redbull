from bottlecors import add_cors


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
