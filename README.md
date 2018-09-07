RedBull
=======

Quickly develop JSON apis.


- Code as documentation
- Auto Options


Write a minimal api
-----

```python
import bottle
from redbull import Manager

mg = Manager(bottle.Bottle())

@mg.api
def say_hi():
    "says hi to people"
    return 'hi'

mg.add_cors()
mg.app.run()
```

```python
import requests

root = 'http://something.com'
print(requests.options(root+'/say/hi').text)
# says hi to people

print(requests.post(root+'/say/hi').text)
# hi
```

Accessing JSON
---------

```python

@mg.api
def say_hi_if_they_say_please():
    "says hi only if you say please"
    please, name = mg.json_get('please', 'name')
    if please:
        return f'hi {name}'
    return ''
```

```python
import requests

requests.post(root+'/say/hi/if/they/say/please', json={"please": True,
                                                       "name": "something"})
```
