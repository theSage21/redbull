RedBull
=======

Quickly develop JSON apis.


- Auto OPTIONS
- All APIs are JSON, POST.
- Using static types APIs are auto-documented at `/<version>/docs`
- You're not locked in. You can still code the old way.


Bottle Example
-----

```python
import bottle
from redbull import Manager

mg = Manager(bottle.Bottle(),
             apiversion='1')

# The function name say_hi becomes the api say/hi
# the args are treated as JSON keys. All args must by type annotated
# optional args are supported
# Simply return dict/string. Redbull wraps it for you in the appropriate object
# The docstring will be provided when the path is called with an OPTIONS method

# In addition the API does not have to return anything. If nothing (None) is
# returned an 'ok' string is returned automatically
@mg.api
def say_hi(name: str, please: bool):
    "Says hi if you say please"
    if please:
        return 'hi ' + name
    return 'um hmm'

# ADD a generous CORS for all routes using the OPTIONS method
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

# The function name say_hi becomes the api say/hi
# the args are treated as JSON keys. All args must by type annotated
# optional args are supported
# Simply return dict/string. Redbull wraps it for you in the appropriate object
@mg.api
async def say_hi(name: str, please: bool, lastname: str='Snow'):
    "Says hi if you say please"
    if please:
        return 'hi ' + name
    return 'um hmm'

# ADD a generous CORS for all routes using the OPTIONS method
mg.add_cors()
web.run_app(mg.app)
```
