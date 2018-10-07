RedBull
=======

Quickly develop JSON apis using Python type hints.
**Do not use in production**

Minimal Example
-----

```python
from redbull import Manager

mg = Manager()

@mg.api()
def say_Hello(name: str='World'):
    "Says hello if you provide a name"
    return f'Hello {name}.'

mg.run()
```

- APIs are live auto-documented at `/<version>/docs`
- You can still code the way your framework of choice expects you to (Bottle, Flask, Django, Aiohttp ...)
- Use python type hints to define json input keys.

The live page is minimal and looks like:

![docs screenshot](docs.png)


A bigger example
-----

```python
from aiohttp import web
from redbull import Manager

mg = Manager(web.Application())  # You can use another framework if you want

# The function name say_hi becomes the api say/hi
# the args are treated as JSON keys. All args must by type annotated
# optional args are supported
# Simply return dict/string. Redbull wraps it for you in the appropriate object
@mg.api(pass_args=True)
async def say_hi(name: str,
                 please: bool,
                 lastname: str='Snow',  # A default is provided
                 __args__,  #     The original args passed to the function by Aiohttp
                 __kwargs__):  #  are added if pass_args is True in the decorator.
    "Says hi if you say please"
    if please:
        return 'hi ' + name
    return 'um hmm'

# ADD a generous CORS for all defined routes using the OPTIONS method
# The OPTIONS of the page also provides a documentation of the API
# Add a `/<version>/docs` GET Page
mg.run()
```

Notes
----

- See if this is still possible with Flask / Django
- **DO NOT USE IN Production** This is just a neat way of making life easier for the person who works on the UI and yourself. Security and other implications are not studies in any significant way.
