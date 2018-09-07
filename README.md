RedBull
=======

Quickly develop JSON apis.


- Code as documentation
- Auto Options


Usage
-----

```python
from redbull import Manager
import bottle

mg = Manager(bottle.Bottle())

@mg.api
def say_hi():
    "says hi"
    return 'hi'

mg.add_cors()
mg.app.run()
```

This creates a bottle server with the `say_hi` function being
served at `/say/hi` URI under a `POST` method. If the method is
queried with an `OPTIONS` request, it returns the docstring of the
function.
