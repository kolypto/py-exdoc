""" Data objects """


class DictProxy(dict, object):
    """ Dictionary with attributes proxied to indicies (except for those starting with '_') """

    def __init__(self):
        super(DictProxy, self).__init__()

    def __getattr__(self, key):
        if key.startswith('_'):
            return object.__getattribute__(self, key)
        return self[key]

    def __setattr__(self, key, value):
        if key.startswith('_'):
            object.__setattr__(self, key, value)
        else:
            self[key] = value


class ExceptionDoc(DictProxy):
    def __init__(self, name, doc):
        """ Documentation for an exception

        :param name: Exception name
        :type name: str
        :param doc: Description text
        :type doc: str
        """
        super(ExceptionDoc, self).__init__()
        self.name = name
        self.doc = doc


class ValueDoc(DictProxy):
    def __init__(self, doc='', type=None):
        """ Documentation for a value

        :param doc: Documenation string
        :type doc: str|unicode
        :param type: Value type, if any
        :type type: str|None
        """
        super(ValueDoc, self).__init__()
        self.doc = doc
        self.type = type


class ArgumentDoc(ValueDoc):
    def __init__(self, name, doc='', type=None):
        """ Documentation for an argument

        :param name: Argument name
        :type name: str
        :param doc: Argument documenation string
        :type doc: str|unicode
        :param type: Argument type, if any
        :type type: str|None
        """
        super(ArgumentDoc, self).__init__(doc, type)
        self.name = name


class ArgumentSpec(DictProxy):
    NODEFAULT = NotImplemented

    def __init__(self, name, default=NODEFAULT, varargs=False, keywords=False):
        """ Specification for an argument

        :param name: Argument name
        :type name: str
        :param default: Default value, if any
        :type default: *
        :param varargs: *args indicator
        :type varargs: bool
        :param keywords: **kwargs indicator
        :type keywords: bool
        """
        super(ArgumentSpec, self).__init__()
        self.name = name
        if varargs:  self.name =  '*' + self.name
        if keywords: self.name = '**' + self.name
        if default is not self.NODEFAULT:
            self.default = default


class Argument(ArgumentSpec, ArgumentDoc):
    def __init__(self, spec, doc=''):
        """ Init argument description

        :param spec: Argument spec
        :type spec: ArgumentSpec
        :param doc: Argument doc, if any
        :type doc: ArgumentDoc|None
        """
        dict.__init__(self)
        self.update(doc or ArgumentDoc(spec.name))
        self.update(spec)


class Docstring(DictProxy):
    def __init__(self, module=None, fullname=None, doc=''):
        """ Plaintext docstring

        :param module: Module name
        :type module: str|None
        :param fullname: Object name
        :type fullname: str|None
        :param doc: Text
        :type doc: str
        """
        super(Docstring, self).__init__()
        self.module = module
        self.name = fullname.rsplit('.', 1)[-1]
        self.fullname = fullname
        self.doc = doc


class FDocstring(Docstring):
    def __init__(self, module=None, fullname=None, doc='', clsdoc='', args=(), ret=None, exc=()):
        """ Parsed docstring for a callable

        :param module: Module name
        :type module: str|None
        :param name: Object name
        :type name: str
        :param doc: Callable docstring
        :type doc: str
        :param clsdoc: Class docstring
        :type clsdoc: str
        :param args: List of arguments
        :type args: list[Argument|ArgumentDoc]
        :param ret: Return value, if any
        :type ret: ValueDoc|None
        :param exc: List of exceptions
        :type exc: list[ExceptionDoc]
        """
        super(FDocstring, self).__init__(module, fullname, doc)
        self.clsdoc = clsdoc
        self.args = args
        self.ret = ret
        self.exc = exc
        self.signature = None

    def update_signature(self):
        args = ['='.join((a.name, repr(a.default))) if 'default' in a else a.name
                for a in self.args]
        self.signature = '{}({})'.format(self.name, ', '.join(args))
