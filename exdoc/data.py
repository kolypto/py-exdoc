""" Data objects """


class DictProxy(dict, object):
    """ Dictionary with attributes proxied to indicies (except for those starting with '_') """

    def __init__(self, *args, **kwargs):
        super(DictProxy, self).__init__(*args, **kwargs)

    def __getattr__(self, key):
        if key.startswith('_'):
            return object.__getattribute__(self, key)
        return self[key]

    def __setattr__(self, key, value):
        if key.startswith('_'):
            object.__setattr__(self, key, value)
        else:
            self[key] = value


#region Py

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
    def __init__(self, module=None, qualname=None, doc=''):
        """ Plaintext docstring

        :param module: Module name
        :type module: str|None
        :param qualname: Qualified object name
        :type qualname: str
        :param doc: Text
        :type doc: str
        """
        super(Docstring, self).__init__()
        self.module = module
        self.name = qualname.rsplit('.', 1)[-1]
        self.qualname = qualname
        self.doc = doc


class FDocstring(Docstring):
    def __init__(self, module=None, qualname=None, doc='', clsdoc='', args=(), ret=None, exc=()):
        """ Parsed docstring for a callable

        :param module: Module name
        :type module: str|None
        :param qualname: Qualified object name
        :type qualname: str
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
        super(FDocstring, self).__init__(module, qualname, doc)
        self.clsdoc = clsdoc
        self.args = args
        self.ret = ret
        self.exc = exc
        self.signature = None
        self.qsignature = None

    def update_signature(self):
        args = ['='.join((a.name, repr(a.default))) if 'default' in a else a.name
                for a in self.args]
        self.signature = '{}({})'.format(self.name, ', '.join(args))
        self.qsignature = '{}({})'.format(self.qualname, ', '.join(args))

#endregion

#region SA


class SaModelDoc(DictProxy):
    def __init__(self, name, table, doc='', columns=(), primary=(), foreign=(), unique=(), relations=()):
        """ Documentation for an SqlAlchemy model

        :param name: Model name
        :type name: str
        :param doc: Model docstring
        :type doc: str
        :param table: Table name
        :type table: list[str]
        :param columns: Columns spec
        :type columns: list[SaColumnDoc]
        :param primary: Primary key
        :type primary: list[str]
        :param foreign: Foreign Keys
        :type foreign: list[SaForeignkeyDoc]
        :param unique: Unique keys: list of lists
        :type unique: list[tuple[str]]
        :param relations: Relationships
        :type relations: list[SaRelationshipDoc]
        """
        super(SaModelDoc, self).__init__()
        self.name = name
        self.table = tuple(table) if len(table) > 1 else table[0]
        self.doc = doc
        self.columns = columns
        self.primary = tuple(primary) if len(primary) > 1 else primary[0]
        self.foreign = foreign
        self.unique = [u if len(u)>1 else u[0] for u in unique]
        self.relations = relations


class SaColumnDoc(DictProxy):
    def __init__(self, key, type, doc='', null=False):
        """ SqlAlchemy column doc

        :param key: Key name
        :type key: str
        :param type: Column type
        :type type: str
        :param doc: Column docstring
        :type doc: str
        :param null: Nullable?
        :type null: bool
        """
        super(SaColumnDoc, self).__init__()
        self.key = key
        self.type = type + (' NULL' if null else ' NOT NULL')
        self.doc = doc


class SaForeignkeyDoc(DictProxy):
    def __init__(self, key, target):
        """ Foreign key doc

        :param key: Key name
        :type key: str
        :param target: Target name
        :type target: str
        """
        super(SaForeignkeyDoc, self).__init__()
        self.key = key
        self.target = target


class SaRelationshipDoc(DictProxy):
    def __init__(self, key, doc='', model=None, pairs=(), uselist=True):
        """ SqlAlchemy relationship doc

        :param key: Key name
        :type key: str
        :param doc: Relationship docstring
        :type doc: str
        :param model: Foreign model name
        :type model: str|None
        :param pairs: Local-remote pairs
        :type pairs: list[str]
        :param uselist: -to-Many?
        :type uselist: bool
        """
        super(SaRelationshipDoc, self).__init__()
        self.key = key + ('[]' if uselist else '')
        self.model = model
        self.target = '{}({})'.format(self.model, ', '.join(pairs))

        self.doc = doc

#endregion
