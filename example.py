import bottle
from redbull import Manager

mg = Manager(bottle.Bottle())


@mg.api
def say_hi(name: str, please: bool):
    "Says hi if you say please"
    if please:
        return 'hi ' + name
    return 'um hmm'


mg.add_cors()
mg.app.run()
