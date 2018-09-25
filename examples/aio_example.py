from aiohttp import web
from redbull import Manager


mg = Manager(web.Application())


@mg.api
async def say_hi(name: str, please: bool, __args__, __kwargs__):
    "Says hi if you say please"
    if please:
        return 'hi ' + name
    return 'um hmm'


mg.finalize()
web.run_app(mg.app)
