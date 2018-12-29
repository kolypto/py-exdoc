""" Create a python file that collects the necessary information and prints json:

```python
#! /usr/bin/env python
from exdoc import doc
import json

from project import User

print json.dumps({
  'user': doc(User),
})
```

And then use its output:

```console
./collect.py | j2 --format=json README.md.j2
```


"""

from .py import doc, getmembers, subclasses
