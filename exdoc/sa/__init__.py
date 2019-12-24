""" Documenting SqlAlchemy models.

```python
from exdoc.sa import doc

doc(User)  # ->
{
  'name': 'User',
  # List of tables the model uses
  'table': ('users',),
  'doc': 'User account',
  # PK: tuple[str]
  'primary': ('uid',),
  # Unique keys
  'unique': (
    # tuple[str]
    ('login',),
  ),
  # Foreign keys
  'foreign': (
    {'key': 'uid', 'target': 'users.uid', 'onupdate': None, 'ondelete': 'CASCADE'},
  ),
  # Columns
  'columns': [
    {'key': 'uid', 'type': 'INTEGER NOT NULL', 'doc': ''},
    {'key': 'login', 'type': 'VARCHAR NULL', 'doc': 'Login'},
    {'key': 'creator_uid', 'type': 'INTEGER NULL', 'doc': 'Creator'},
    {'key': 'meta', 'type': 'JSON NULL', 'doc': ''},
  ],
  # Relationships
  'relations': [
    {'key': 'creator', 'model': 'User',
     'target': 'User(creator_uid=uid)', 'doc': ''},
    {'key': 'devices[]', 'model': 'Device',
     'target': 'Device(uid)', 'doc': ''},
    {'key': 'created[]', 'model': 'User',
     'target': 'User(uid=creator_uid)', 'doc': ''},
  ]
}
```
"""

from ..data import SaModelDoc, SaColumnDoc, SaForeignkeyDoc, SaRelationshipDoc
from ..py import getdoc

try:
    from sqlalchemy import inspect, exc as sa_exc
    from sqlalchemy.orm.mapper import Mapper
    from sqlalchemy.orm.relationships import RelationshipProperty
    from sqlalchemy.sql.schema import ForeignKeyConstraint, UniqueConstraint
    from sqlalchemy.dialects import postgresql
except ImportError:
    pass


def _model_columns(ins):
    """ Get columns info

    :type ins: sqlalchemy.orm.mapper.Mapper
    :rtype: list[SaColumnDoc]
    """
    columns = []
    for c in ins.column_attrs:
        # Skip protected
        if c.key.startswith('_'):
            continue

        # Type
        column_type = c.columns[0].type  # FIXME: support multi-column properties
        # Compile it using a dialect if necessary
        try:
            column_type_str = str(column_type)
        except sa_exc.UnsupportedCompilationError:
            # Got to compile it using a dialect
            # TODO: support other dialects in addition to Postgres
            column_type_str = column_type.compile(dialect=postgresql.dialect())

        # Collect
        columns.append(SaColumnDoc(
            key=c.key,
            doc=c.doc or '',
            type=column_type_str,
            null=c.columns[0].nullable,
        ))
    return columns


def _model_primary(ins):
    """ Get primary key info

    :type ins: sqlalchemy.orm.mapper.Mapper
    :rtype: list[str]
    """
    return tuple(c.key for c in ins.primary_key)


def _model_foreign(ins):
    """ Get foreign keys info

    :type ins: sqlalchemy.orm.mapper.Mapper
    :rtype: list[SaForeignkeyDoc]
    """
    fks = []
    for t in ins.tables:
        fks.extend([
            SaForeignkeyDoc(
                key=fk.column.key,
                target=fk.target_fullname,
                onupdate=fk.onupdate,
                ondelete=fk.ondelete
            )
            for fk in t.foreign_keys])
    return fks


def _model_unique(ins):
    """ Get unique constraints info

    :type ins: sqlalchemy.orm.mapper.Mapper
    :rtype: list[tuple[str]]
    """
    unique = []
    for t in ins.tables:
        for c in t.constraints:
            if isinstance(c, UniqueConstraint):
                unique.append(tuple(col.key for col in c.columns))
    return unique


def _model_relations(ins):
    """ Get relationships info

    :type ins: sqlalchemy.orm.mapper.Mapper
    :rtype: list[SaRelationshipDoc]
    """
    relations = []
    for r in ins.relationships:
        # Target model name
        target_model_name = r.mapper.class_.__name__

        # Format
        relations.append(SaRelationshipDoc(
            key=r.key,
            doc=r.doc or '',
            model=target_model_name,
            pairs=map(lambda a_b_tuple: a_b_tuple[0].key if a_b_tuple[0].key == a_b_tuple[1].key else '{}={}'.format(a_b_tuple[0].key, a_b_tuple[1].key), r.local_remote_pairs),
            uselist=r.uselist
        ))
    return relations


def doc(model):
    """ Get documentation object for an SqlAlchemy model

    :param model: Model
    :type model: sqlalchemy.ext.declarative.DeclarativeBase
    :rtype: SaModelDoc
    """
    ins = inspect(model)

    return SaModelDoc(
        name=model.__name__,
        table=[t.name for t in ins.tables],
        doc=getdoc(ins.class_),
        columns=_model_columns(ins),
        primary=_model_primary(ins),
        foreign=_model_foreign(ins),
        unique=_model_unique(ins),
        relations=_model_relations(ins)
    )
