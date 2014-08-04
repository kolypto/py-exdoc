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
    :return: (name, Callable|None). Callable is None for classes without __init__()
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


def _doc_parse(doc, module=None, name=None):
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
    return data.FDocstring(module=module, name=name, doc=doc, args=doc_args, exc=doc_exc, ret=doc_ret)


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


def _docspec(func, module=None, name=None):
    """ For a callable, get the full spec by merging doc_parse() and argspec()

    :type func: Callable
    :rtype: data.FDocstring
    """
    sp = _argspec(func)
    doc = _doc_parse(getdoc(func), module=module, name=name)

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
    """ Get documentation for an object

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
            return data.Docstring(name=obj.__name__, doc=getdoc(obj))
        else:
            return None

    # Callables
    name, fun = _get_callable(obj)
    docstr = _docspec(fun, module=module, name=name)

    # Class? get doc
    if inspect.isclass(obj):
        docstr.clsdoc = getdoc(obj)

    # Finish
    return docstr
