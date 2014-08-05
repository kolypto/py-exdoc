[![Build Status](https://api.travis-ci.org/kolypto/py-exdoc.png?branch=master)](https://travis-ci.org/kolypto/py-exdoc)


ExDoc
=====

Documentation extractor.

Extracts pieces of documentation from your code to build a document which can be fed to template processors.

Output can be in JSON, YAML, whatever.
Use any command-line templating engine, like [j2cli](https://github.com/kolypto/j2cli), to render templates from it.

It does not do any automatic background magic: it just offers helpers which allows you to extract the necessary pieces.




Collectors
==========

ExDoc is just a set of helper functions that collects information into dictionaries.

Python
------


### doc(obj)
```python
from exdoc import doc
```

The `doc()` function simply fetches documentation for an object, which can be

* Module
* Class
* Function or method
* Property

The resulting dictionary includes argument specification, as well as parsed docstring:

```python
def f(a, b=1, *args):
    """ Simple function
       
    :param a: First
    :type a: int
    :param b: Second
    :type b: int
    :param args: More numbers
    :returns: nothing interesting
    :rtype: bool
    :raises ValueError: hopeless condition
    """
    
from exdoc import doc

doc(f)  # ->
{
  'module': '__main__',
  'name': 'f',
  'qualname': 'f',
  'signature': 'f(a, b=1, *args)',
  'clsdoc': '',
  'doc': 'Simple function',
  'exc': [{'doc': 'hopeless condition', 'name': 'ValueError'}],
  'ret': {'doc': 'nothing interesting', 'type': 'bool'},
  'args': [
    {'doc': 'First', 'name': 'a', 'type': 'int'},
    {'default': 1, 'doc': 'Second', 'name': 'b', 'type': 'int'},
    {'doc': 'More numbers', 'name': '*args', 'type': None}
  ],
}
```


### getmembers(obj, *predicates)

Return all the members of an object as a list of `(key, value)` tuples, sorted by name.

The optional list of predicates can be used to filter the members.

The default predicate drops members whose name starts with '_'. To disable it, pass `None` as the first predicate.


### subclasses(cls, leaves=False)

List all subclasses of the given class, including itself.

If `leaves=True`, only returns classes which have no subclasses themselves.
