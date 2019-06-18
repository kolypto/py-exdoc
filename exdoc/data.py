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

    def update(self, *args, **kwargs):
        """ A handy update() method which returns self :)

        :rtype: DictProxy
        """
        super(DictProxy, self).update(*args, **kwargs)
        return self


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

    def __init__(self, name, type=None, default=NODEFAULT, varargs=False, keywords=False):
        """ Specification for an argument

        :param name: Argument name
        :type name: str
        :param type: Argument type
        :type type: type
        :param default: Default value, if any
        :type default: *
        :param varargs: *args indicator
        :type varargs: bool
        :param keywords: **kwargs indicator
        :type keywords: bool
        """
        super(ArgumentSpec, self).__init__()
        self.name = name
        self.type = type
        if varargs:  self.name =  '*' + self.name
        if keywords: self.name = '**' + self.name
        if default is not self.NODEFAULT:
            self.default = default


class Argument(ArgumentSpec, ArgumentDoc):
    def __init__(self, spec, doc=''):
        """ Init argument description from ArgumentSpec (function info) and ArgumentDoc (docstring info)

        :param spec: Argument spec
        :type spec: ArgumentSpec
        :param doc: Argument doc, if any
        :type doc: ArgumentDoc|None
        """
        dict.__init__(self)
        self.update(doc or ArgumentDoc(spec.name))
        self.update(spec)

        # If argspec has no type, get it from the doc
        if spec.type is None and doc:
            self.type = doc.type


class Docstring(DictProxy):
    """ Plaintext docstring

    Attrs:
        module (str?): Module name
        qualname (str): Qualified object name (class.method)
        doc (str): The docstring
    """

    def __init__(self, module=None, qualname=None, doc=''):
        super(Docstring, self).__init__()
        self.module = module
        self.name = qualname.rsplit('.', 1)[-1]
        self.qualname = qualname
        self.doc = doc


class FDocstring(Docstring):
    """ Docstring for a callable

    Attrs:
        clsdoc: Docstring for the class
        args (list[Argument|ArgumentDoc]): Function arguments
        ret (ValueDoc|None): Return type
        exc (list[ExceptionDoc]): Exceptions info
        signature (str): function signature (with args)
        tsignature (str): typed function signature (with args and types)
        rtsignature (str): return-typed function signature (with args and return-type)
        qsignature (str): qualified function signature (with full name and  args)
        qtsignature (str): qualified typed function signature (with full name and args and types)
        qrtsignature (str): qualified return-typed function signature (with full name and args and return-type)
        example (str): the "Example" section, if any
    """

    def __init__(self, module=None, qualname=None, doc='', clsdoc='', args=(), ret=None, exc=(), example=None):
        super(FDocstring, self).__init__(module, qualname, doc)
        self.clsdoc = clsdoc
        self.args = args
        self.ret = ret
        self.exc = exc
        self.signature = None
        self.tsignature = None
        self.rtsignature = None
        self.qsignature = None
        self.qtsignature = None
        self.qrtsignature = None
        self.example = example

    def update_signature(self):
        # Prepare arguments
        args_typed = []
        args_untyped = []
        for a in self.args:
            a_type = ': {}'.format(a.type) if a.type else ''
            a_default = '={}'.format(a.default.__name__ if isinstance(a.default, type) else repr(a.default)) \
                        if 'default' in a else ''

            # untyped
            args_untyped.append(a.name + a_default)
            args_typed.append(a.name + a_type + a_default)

        # untyped
        self.signature = '{}({})'.format(self.name, ', '.join(args_untyped))
        self.qsignature = '{}({})'.format(self.qualname, ', '.join(args_untyped))

        # rtyped
        self.rtsignature = self.signature
        self.qrtsignature = self.qsignature

        # typed
        self.tsignature = '{}({})'.format(self.name, ', '.join(args_typed))
        self.qtsignature = '{}({})'.format(self.qualname, ', '.join(args_typed))
        # -> returns
        if self.ret and self.ret.type is not None:
            rtype_str = ' -> {}'.format(self.ret.type)
            self.tsignature += rtype_str
            self.qtsignature += rtype_str
            self.rtsignature += rtype_str
            self.qrtsignature += rtype_str

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
        :type table: tuple[str]
        :param columns: Columns spec
        :type columns: list[SaColumnDoc]
        :param primary: Primary key
        :type primary: tuple[str]
        :param foreign: Foreign Keys
        :type foreign: tuple[SaForeignkeyDoc]
        :param unique: Unique keys: list of lists
        :type unique: tuple[tuple[str]]
        :param relations: Relationships
        :type relations: list[SaRelationshipDoc]
        """
        super(SaModelDoc, self).__init__()
        self.name = name
        self.table = tuple(table)
        self.doc = doc
        self.columns = columns
        self.primary = tuple(primary)
        self.foreign = tuple(foreign)
        self.unique = tuple(tuple(u) for u in unique)
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
    def __init__(self, key, target, onupdate=None, ondelete=None):
        """ Foreign key doc

        :param key: Key name
        :type key: str
        :param target: Target name
        :type target: str
        :param onupdate: Behavior on update
        :type onupdate: str|None
        :param ondelete: Behavior on delete
        :type ondelete: str|None
        """
        super(SaForeignkeyDoc, self).__init__()
        self.key = key
        self.target = target
        self.onupdate = onupdate
        self.ondelete = ondelete


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
