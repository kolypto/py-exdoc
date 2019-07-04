""" Helpers for Python objects """

import inspect
import collections
import re
from inspect import cleandoc

from .. import data


def getdoc(obj):
    """ Get object docstring

    :rtype: str
    """
    inspect_got_doc = inspect.getdoc(obj)
    if inspect_got_doc in (object.__init__.__doc__, object.__doc__):
        return '' # We never want this builtin stuff
    return (inspect_got_doc or '').strip()


def _get_callable(obj, of_class = None):
    """ Get callable for an object and its full name.

    Supports:

    * functions
    * classes (jumps to __init__())
    * methods
    * @classmethod
    * @property

    :param obj: function|class
    :type obj: Callable
    :param of_class: Class that this method is a member of
    :type of_class: class|None
    :return: (qualname, Callable|None, Class|None). Callable is None for classes without __init__()
    :rtype: (str, Callable|None, Class|None)
    """
    # Cases
    o = obj

    if inspect.isclass(obj):
        try:
            o = obj.__init__
            of_class = obj
        except AttributeError:
            pass

    # Finish
    return obj.__qualname__, o, of_class


def _doc_parse(doc, module=None, qualname=None):
    """ Parse docstring into a dict

    :rtype: data.FDocstring
    """
    parser = _doc_parse__detect_format(doc, module, qualname)
    return parser(doc, module, qualname)


def _doc_parse__detect_format(doc, module=None, qualname=None):
    """ Detect docstring format and get a callable that will process it """
    # Try detectors
    found_sphinx_strict = sphinx_tags_detector_rex.search(doc) is not None
    found_google_strict = google_sections_detector_rex.search(doc) is not None
    found_sphinx_relaxed = sphinx_tags_rex.search(doc) is not None
    found_google_relaxed = google_sections_rex.search(doc) is not None

    # Choose: first, try strict.
    # If it didn't work, try relaxed
    if found_sphinx_strict or found_google_strict:
        found_sphinx = found_sphinx_strict
        found_google = found_google_strict
    else:
        # Prefer sphinx over Google here
        found_sphinx = found_sphinx_relaxed
        found_google = found_google_relaxed

    # Result?
    if found_google and found_sphinx:
        raise ValueError(
            "Cannot determine the format of {module}.{qualname} docstring: both Sphinx and Google formats seem to be "
            "applicable.".format(module=module, qualname=qualname)
        )

    # Use Google format
    if found_google:
        return _doc_parse_google

    # By default, use Sphinx format
    return _doc_parse_sphinx

# The list of sections used in Google format
known_google_secions = {
    "Arguments": "args",
    "Args": "args",
    "Parameters": "args",
    "Params": "args",
    "Raises": "excs",
    "Exceptions": "excs",
    "Except": "excs",
    "Attributes": "attrs",
    "Example": "examples",
    "Examples": "examples",
    "Returns": "ret",
    "Yields": "ret",
}
# And some regular expressions to detect and parse them
_google_sections_mkrex = lambda known_google_secions: \
    re.compile(r'^(' + '|'.join(map(re.escape, known_google_secions)) + r'):\s*$\s{4,}', re.MULTILINE)
google_sections_rex = _google_sections_mkrex(known_google_secions)
google_sections_detector_rex = _google_sections_mkrex(
    set(known_google_secions) - {'Example', 'Examples'}  # they give a lot of false positives
)


def _doc_parse_google(doc, module=None, qualname=None):
    """ Parse docstring into a dict, format: Google

    :rtype: data.FDocstring
    """
    # Sections that have a "name: text" structure or a "name (type): text" structure
    structured_sections = {'args', 'excs', 'attrs'}
    structured_sections_rex = re.compile(r'^(\S+)\s*(?:\(([^)]+)\))?\s*:', re.MULTILINE)

    # Parse the return type
    return_type_rex = re.compile(r'^(\S+):')

    # Dedent the whole thing first
    doc = cleandoc(doc)
    # Now we can count that sections are at column 0

    # Info variables
    doc = doc  # the leftover docstring
    doc_args = []
    doc_exc = []
    doc_ret = None
    doc_example = None

    # Go through sections in reverse
    # This way, it's always easy to copy the pieces
    for section_name_orig, section_text, doc in _parse_sections_in_reverse(google_sections_rex, doc):
        section_name = known_google_secions[section_name_orig]  # Normalized section name

        # Parse the section
        section_structure = []
        if section_name in structured_sections:
            # Dedent: make sure that columns start at column 0
            section_text = cleandoc(section_text)

            # Parse every item
            for item_name, item_type, item_text, section_text \
                in _parse_sections_in_reverse(structured_sections_rex, section_text):
                    section_structure.append((item_name, item_type, cleandoc(item_text)))
            # Finalize
            section_structure.reverse()
            section_text = section_text.strip()

            # Test
            if section_text != '':
                raise ValueError(
                    "There may be a typo in section '{section}' of {module}.{qualname}.\n"
                    "Unparsed data remains:\n{unparsed}".format(
                        section=section_name_orig, unparsed=section_text,
                        module=module, qualname=qualname
                    )
                )

        # Handle section
        if section_name == 'args':
            for arg_name, arg_type, arg_descr in section_structure:
                doc_args.append(data.ArgumentDoc(arg_name.lstrip('*'), arg_descr, arg_type))
        elif section_name == 'excs':
            for exc_class, _, exc_descr in section_structure:
                doc_exc.append(data.ExceptionDoc(exc_class, exc_descr))
        elif section_name == 'examples':
            doc_example = cleandoc(section_text)
        elif section_name == 'ret':
            # The return type might be in the very head of the string
            ret_type = None
            m = return_type_rex.match(section_text)
            if m:
                ret_type = m.group(1).strip()
                section_text = cleandoc(section_text[m.end():])
            # Done
            doc_ret = data.ValueDoc(section_text, ret_type)
        elif section_name == 'attrs':
            pass  # TODO: support for class attributes
        else:
            raise ValueError("Unsupported section '{section}' in {module}.{qualname}".format(
                section=section_name_orig, module=module, qualname=qualname
            ))

    # Done
    return data.FDocstring(module=module, qualname=qualname,
                           doc=doc, args=doc_args, exc=doc_exc, ret=doc_ret, example=doc_example)

# The list of tags used with Sphinx
known_sphinx_tags = {
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
# And regexes to parse and detect it
_sphinx_tags_mkrex = lambda sphinx_tags: \
    re.compile(r'^:(' + '|'.join(map(re.escape, sphinx_tags)) + r')\s*(\S+)?\s*:', re.MULTILINE)
sphinx_tags_rex = _sphinx_tags_mkrex(known_sphinx_tags)
sphinx_tags_detector_rex = sphinx_tags_rex  # reuse, because Sphinx format can be detected unambiguosly


def _doc_parse_sphinx(doc, module=None, qualname=None):
    """ Parse docstring into a dict, format: Sphinx (reST)

    :rtype: data.FDocstring
    """
    # Dedent the whole thing first
    doc = cleandoc(doc)
    # Now we can count that sections are at column 0

    # Match tags
    doc = doc  # the leftover docstring
    collect_args = {}
    collect_ret = {}
    doc_args = []
    doc_exc = []
    for tag, arg, value, doc in _parse_sections_in_reverse(sphinx_tags_rex, doc):
        tag = known_sphinx_tags[tag]  # Normalized tag name

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


def _parse_sections_in_reverse(rex, text):
    """ Keep chopping the matching `rex` sections from the `text` docstring """
    for m in reversed(list(rex.finditer(text))):
        groups = m.groups()  # the groups matched by the RegExp
        section_text = text[m.end():].strip()  # the text after the section header (its body)
        text = text[:m.start()]  # the remaining portion of the string
        yield (*groups, section_text, text.strip())


def is_method_static(cls, method_name):
    try:
        return isinstance(inspect.getattr_static(cls, method_name), staticmethod)
    except AttributeError:
        raise RuntimeError("Unable to find %s in %s" % (method_name, cls.__name__))

def annotation_to_string(annot):
    # None: passthru
    if annot is None:
        return None
    # Python types
    if isinstance(annot, type):
        return annot.__name__
    # Other types
    s = str(annot)
    # `typing` module inserts `typing.` prefixes which are ugly. Remove.
    s = s.replace('typing.', '')
    return s

def _argspec(func):
    """ For a callable, get the full argument spec, and its return type (if any) """
    assert isinstance(func, collections.Callable), 'Argument must be a callable'

    try: sp = inspect.getfullargspec(func)
    except TypeError:
        # inspect.getargspec() fails for built-in functions
        return [], None

    # Collect arguments with defaults
    ret = []
    defaults_start = len(sp.args) - len(sp.defaults) if sp.defaults else len(sp.args)
    for i, name in enumerate(sp.args):
        # Arg name, annotation
        arg = data.ArgumentSpec(name=name,
                                type=annotation_to_string(sp.annotations.get(name, None)))
        # Arg default value
        if i >= defaults_start:
            arg['default'] = sp.defaults[i - defaults_start]
        # Done
        ret.append(arg)

    # *args, **kwargs
    if sp.varargs:
        ret.append(data.ArgumentSpec(sp.varargs, varargs=True))
    if sp.varkw:
        ret.append(data.ArgumentSpec(sp.varkw, keywords=True))

    # Finish
    return ret, annotation_to_string(sp.annotations.get('return', None))


def _docspec(func, module=None, qualname=None, of_class=None):
    """ For a callable, get the full spec by merging doc_parse() and argspec()

    :type func: Callable
    :rtype: data.FDocstring
    """
    sp, return_type = _argspec(func)
    doc = _doc_parse(getdoc(func), module=module, qualname=qualname)

    # Merge args; priority to function signature
    doc_map = {arg.name: arg
               for arg in doc.args}
    doc.args = [data.Argument(arg,
                              doc_map.get(arg.name.lstrip('*'), None))
                for arg in sp]

    # Merge return type
    if return_type is not None:
        if 'ret' in doc and doc['ret'] is not None:
            doc.ret.type = return_type
        else:
            doc.ret = data.ValueDoc(type=return_type)

    # Args shift: dump `self`
    if (inspect.isroutine(func) and of_class is not None) and \
            (of_class is not None and not is_method_static(of_class, func.__name__)):
        doc.args = doc.args[1:]

    # Signature
    doc.update_signature()

    # Finish
    return doc


def doc(obj, of_class=None):
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
      'qsignature': 'f(a, b=1, *args)',  # qualified signature
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

    Note: in Python 3, when documenting a method of a class, pass the class to the `doc()` function as the second argument:

    ```python
    doc(cls.method, cls)
    ```

    This is necessary because in Python3 methods are not bound like they used to. Now, they are just functions.

    :type obj: ModuleType|type|Callable|property
    :param of_class: A class whose method is being documented.
    :type of_class: class|None
    :rtype: Docstring|FDocstring
    """
    # Special care about properties
    if isinstance(obj, property):
        docstr = doc(obj.fget)
        # Some hacks for properties
        docstr.signature = docstr.qsignature= obj.fget.__name__
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
    qualname, fun, of_class = _get_callable(obj, of_class)
    docstr = _docspec(fun, module=module, qualname=qualname, of_class=of_class)

    # Class? Get doc
    if inspect.isclass(obj):
        # Get class doc
        clsdoc = getdoc(obj)
        # Parse docstring and merge into constructor doc
        if clsdoc:
            # Parse docstring
            clsdoc = _doc_parse(clsdoc, module=module, qualname=qualname)

            # Store clsdoc always
            docstr.clsdoc = clsdoc.doc

            # Merge exceptions list
            docstr.exc.extend(clsdoc.exc)

            # If constructor does not have it's own docstr -- copy it from the clsdoc
            if not docstr.doc:
                docstr.doc = docstr.clsdoc

            # Merge arguments: type, doc
            for a_class in clsdoc.args:
                for a_constructor in docstr.args:
                    if a_class.name.lstrip('*') == a_constructor.name.lstrip('*'):
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
    def predicate(key_value_tuple):
        key, value = key_value_tuple
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
