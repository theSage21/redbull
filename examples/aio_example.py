from aiohttp import web
from redbull import Manager


mg = Manager(web.Application())


@mg.api
async def say_hi(name: str, please: bool):
    "Says hi if you say please"
    if please:
        return 'hi ' + name
    return 'um hmm'


mg.add_cors()
web.run_app(mg.app)
