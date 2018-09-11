RedBull
=======

Quickly develop JSON apis.


- Auto OPTIONS
- All APIs are JSON, POST.
- Using static types APIs are auto-documented.
- You're not locked in. You can still code the old way.


Bottle Example
-----

```python
import bottle
from redbull import Manager

mg = Manager(bottle.Bottle(),
             apiversion='1')

@mg.api
def say_hi(name: str, please: bool):
    "Says hi if you say please"
    if please:
        return 'hi ' + name
    return 'um hmm'

mg.add_cors()
mg.app.run()
```


Aiohttp Example
-----

```python
from aiohttp import web
from redbull import Manager

mg = Manager(web.Application(),
             apiversion='1')

@mg.api
async def say_hi(name: str, please: bool):
    "Says hi if you say please"
    if please:
        return 'hi ' + name
    return 'um hmm'

mg.add_cors()
web.run_app(mg.app)
```
