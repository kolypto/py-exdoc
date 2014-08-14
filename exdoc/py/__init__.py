""" Helpers for Python objects """

import inspect
import collections
import re
from .. import data


def getdoc(obj):
    """ Get object docstring

    :rtype: str
    """
    return (inspect.getdoc(obj) or '').strip()


def _get_callable(obj):
    """ Get callable for an object and its full name.

    Supports:

    * functions
    * classes (jumps to __init__())
    * methods
    * @classmethod
    * @property

    :param obj: function|class
    :type obj: Callable
    :return: (qualname, Callable|None). Callable is None for classes without __init__()
    :rtype: (str, Callable|None)
    """
    # Cases
    name = ''
    o = obj
    if inspect.isfunction(obj):
        pass
    elif inspect.isclass(obj):
        try:
            o = obj.__init__
        except AttributeError:
            pass
    elif inspect.ismethod(obj):
        if obj.im_class is type:
            # @classmethod: bound to class
            cls = obj.im_self
        else:
            # Ordinary methods: not bound
            cls = obj.im_class
        name = cls.__name__ + '.'
    else:
        raise AssertionError('Unsupported type provided: {}'.format(type(obj)))

    # Finish
    return name + obj.__name__, o


def _doc_parse(doc, module=None, qualname=None):
    """ Parse docstring into a dict

    :rtype: data.FDocstring
    """

    # Build the rex
    known_tags = {
        'param': 'arg',
        'type': 'arg-type',
        'return': 'ret',
        'returns': 'ret',
        'rtype': 'ret-type',
        'exception': 'exc',
        'except': 'exc',
        'raise': 'exc',
        'raises': 'exc',
    }
    tag_rex = re.compile(r'^\s*:(' + '|'.join(map(re.escape, known_tags)) + r')\s*(\S+)?\s*:', re.MULTILINE)

    # Match tags
    collect_args = {}
    collect_ret = {}
    doc_args = []
    doc_exc = []
    for m in reversed(list(tag_rex.finditer(doc))):
        # Fetch data
        tag, arg = m.groups()
        tag = known_tags[tag]  # Normalized tag name

        # Fetch docstring part
        value = doc[m.end():].strip()  # Copy text after the tag
        doc = doc[:m.start()].strip()  # truncate the string

        # Handle tag: collect data
        if tag == 'exc':
            doc_exc.append(data.ExceptionDoc(arg, value))
        elif tag in ('ret', 'ret-type'):
            # Collect fields 1 by 1
            collect_ret[{'ret': 'doc', 'ret-type': 'type'}[tag]] = value
        elif tag in ('arg', 'arg-type'):
            # Init new collection
            if arg not in collect_args:
                doc_args.append(arg)  # add name for now, then map() replace with classes
                collect_args[arg] = {}
            # Collect fields 1 by 1
            collect_args[arg][{'arg': 'doc', 'arg-type': 'type'}[tag]] = value
        else:
            raise AssertionError('Unknown tag type: {}'.format(tag))

    # Merge collected data
    doc_ret = data.ValueDoc(**collect_ret) if collect_ret else None
    doc_args = map(lambda name: data.ArgumentDoc(name=name, **collect_args[name]), collect_args)

    # Finish
    return data.FDocstring(module=module, qualname=qualname, doc=doc, args=doc_args, exc=doc_exc, ret=doc_ret)


def _argspec(func):
    """ For a callable, get the full argument spec

    :type func: Callable
    :rtype: list[data.ArgumentSpec]
    """
    assert isinstance(func, collections.Callable), 'Argument must be a callable'

    try: sp = inspect.getargspec(func)
    except TypeError:
        # inspect.getargspec() fails for built-in functions
        return []

    # Collect arguments with defaults
    ret = []
    defaults_start = len(sp.args) - len(sp.defaults) if sp.defaults else len(sp.args)
    for i, name in enumerate(sp.args):
        arg = data.ArgumentSpec(name)
        if i >= defaults_start:
            arg['default'] = sp.defaults[i - defaults_start]
        ret.append(arg)

    # *args, **kwargs
    if sp.varargs:
        ret.append(data.ArgumentSpec(sp.varargs, varargs=True))
    if sp.keywords:
        ret.append(data.ArgumentSpec(sp.keywords, keywords=True))

    # Finish
    return ret


def _docspec(func, module=None, qualname=None):
    """ For a callable, get the full spec by merging doc_parse() and argspec()

    :type func: Callable
    :rtype: data.FDocstring
    """
    sp = _argspec(func)
    doc = _doc_parse(getdoc(func), module=module, qualname=qualname)

    # Merge args
    doc_map = {a.name: a for a in doc.args}
    doc.args = [data.Argument(a, doc_map.get(a.name.lstrip('*'), None)) for a in sp]

    # Args shift
    if inspect.ismethod(func):
        doc.args = doc.args[1:]

    # Signature
    doc.update_signature()

    # Finish
    return doc


def doc(obj):
    """ Get parsed documentation for an object as a dict.

    This includes arguments spec, as well as the parsed data from the docstring.

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
        ''' Simple function

        : param a: First
        : type a: int
        : param b: Second
        : type b: int
        : param args: More numbers
        : returns: nothing interesting
        : rtype: bool
        : raises ValueError: hopeless condition
        '''

    from exdoc import doc

    doc(f)  # ->
    {
      'module': '__main__',
      'name': 'f',
      'qualname': 'f',  # qualified name: e.g. <class>.<method>
      'signature': 'f(a, b=1, *args)',
      'doc': 'Simple function',
      'clsdoc': '',  # doc from the class (used for constructors)
      # Exceptions
      'exc': [
        {'doc': 'hopeless condition', 'name': 'ValueError'}
      ],
      # Return value
      'ret': {'doc': 'nothing interesting', 'type': 'bool'},
      # Arguments
      'args': [
        {'doc': 'First', 'name': 'a', 'type': 'int'},
        {'default': 1, 'doc': 'Second', 'name': 'b', 'type': 'int'},
        {'doc': 'More numbers', 'name': '*args', 'type': None}
      ],
    }
    ```

    :type obj: ModuleType|type|Callable|property
    :rtype: Docstring|FDocstring
    """
    # Special care about properties
    if isinstance(obj, property):
        docstr = doc(obj.fget)
        # Some hacks for properties
        docstr.signature = obj.fget.__name__
        docstr.args = docstr.args[1:]
        return docstr

    # Module
    module = inspect.getmodule(obj)
    if module:
        module = module.__name__

    # Not callable: e.g. modules
    if not callable(obj):
        if hasattr(obj, '__name__'):
            return data.Docstring(qualname=obj.__name__, doc=getdoc(obj))
        else:
            return None

    # Callables
    qualname, fun = _get_callable(obj)
    docstr = _docspec(fun, module=module, qualname=qualname)

    # Class? Get doc
    if inspect.isclass(obj):
        # Get class doc
        clsdoc = getdoc(obj)
        # Parse docstring and merge into constructor doc
        if clsdoc:
            # Parse docstring
            clsdoc = _doc_parse(clsdoc, module=module, qualname=qualname)
            # Copy: doc, exc
            if not docstr.doc:
                # If constructor does not have it's own docstr -- copy it to constructor
                docstr.doc = clsdoc.doc
                docstr.clsdoc = ''
            else:
                # Otherwise, leave classdoc as is
                docstr.clsdoc = clsdoc.doc
            docstr.exc.extend(clsdoc.exc)
            # Merge arguments: type, doc
            for a_class in clsdoc.args:
                for a_constructor in docstr.args:
                    if a_class.name == a_constructor.name:
                        a_constructor.type = a_class.type
                        a_constructor.doc = a_class.doc

    # Finish
    return docstr


def getmembers(obj, *predicates):
    """ Return all the members of an object as a list of `(key, value)` tuples, sorted by name.

    The optional list of predicates can be used to filter the members.

    The default predicate drops members whose name starts with '_'. To disable it, pass `None` as the first predicate.

    :param obj: Object to list the members for
    :param predicates: Functions to filter the members.

        If the first value is not None, a default predicate is added that filters private members out (name starts with '_')

    :type predicates: tuple[Callable|None]
    :returns: Sorted list of (name, value) tuples
    :rtype: list[(str, *)]
    """
    # Add default
    if not predicates or predicates[0] is not None:
        predicates = (lambda key, value: not key.startswith('_'),) + predicates
    # Build composite predicate
    def predicate((key, value)):
        for p in predicates:
            if p is not None and not p(key, value):
                return False
        return True
    # Filter
    return filter(predicate, inspect.getmembers(obj))


def subclasses(cls, leaves=False):
    """ List all subclasses of the given class, including itself.

    If `leaves=True`, only returns classes which have no subclasses themselves.

    :type cls: type
    :param leaves: Only return leaf classes
    :type leaves: bool
    :rtype: list[type]
    """
    stack = [cls]
    subcls = []
    while stack:
        c = stack.pop()
        c_subs = c.__subclasses__()
        stack.extend(c_subs)
        if not leaves or not c_subs:
            subcls.append(c)
    return subcls
