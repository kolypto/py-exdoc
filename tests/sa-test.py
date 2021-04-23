import unittest
from exdoc import sa

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship, column_property


Base = declarative_base()

class User(Base):
    """ User """
    __tablename__ = 'users'

    uid = Column(Integer, primary_key=True, nullable=False)
    login = Column(String, unique=True, doc='Login')
    creator_uid = Column(Integer, ForeignKey(uid, ondelete='SET NULL'), nullable=True, doc="Creator")
    meta = Column(JSON)

    age = Column(Integer)
    age_plus_10 = column_property(age + 10)

    creator = relationship('User', backref='created', remote_side=[uid], foreign_keys=creator_uid)


class Device(Base):
    """ User device """
    __tablename__ = 'devices'
    __table_args__ = (
        UniqueConstraint('uid', 'serial'),
    )

    id = Column(Integer, primary_key=True, nullable=False)
    uid = Column(Integer, ForeignKey(User.uid, ondelete='CASCADE'), nullable=False, doc="Owner")
    serial = Column(String(32), nullable=False)

    user = relationship(User, backref="devices", foreign_keys=uid, doc="Owner")


class SaTest(unittest.TestCase):
    def test_doc(self):
        """ Test doc() """

        # User
        d = sa.doc(User)
        self.assertEqual(d.pop('name'), 'User')
        self.assertEqual(d.pop('table'), ('users',))
        self.assertEqual(d.pop('doc'), 'User')
        self.assertEqual(d.pop('primary'), ('uid',))
        self.assertEqual(d.pop('unique'), (('login',),))
        self.assertEqual(d.pop('foreign'), (
            {'key': 'uid', 'target': 'users.uid', 'onupdate': None, 'ondelete': 'SET NULL'},
        ))
        self.assertEqual(d.pop('columns'), [
            {'key': 'age_plus_10', 'type': 'INTEGER NOT NULL', 'doc': ''},
            {'key': 'uid', 'type': 'INTEGER NOT NULL', 'doc': ''},
            {'key': 'login', 'type': 'VARCHAR NULL', 'doc': 'Login'},
            {'key': 'creator_uid', 'type': 'INTEGER NULL', 'doc': 'Creator'},
            {'key': 'meta', 'type': 'JSON NULL', 'doc': ''},
            {'key': 'age', 'type': 'INTEGER NULL', 'doc': ''},
        ])
        self.assertEqual(sorted(d.pop('relations'), key=lambda a: a['key']), [
            {'key': 'created[]', 'model': 'User', 'target': 'User(uid=creator_uid)', 'doc': ''},
            {'key': 'creator', 'model': 'User', 'target': 'User(creator_uid=uid)', 'doc': ''},
            {'key': 'devices[]', 'model': 'Device', 'target': 'Device(uid)', 'doc': ''},
        ])
        self.assertEqual(d, {})

        # Device
        d = sa.doc(Device)
        self.assertEqual(d.pop('name'), 'Device')
        self.assertEqual(d.pop('table'), ('devices',))
        self.assertEqual(d.pop('doc'), 'User device')
        self.assertEqual(d.pop('primary'), ('id',))
        self.assertEqual(d.pop('unique'), (('uid', 'serial'),))
        self.assertEqual(d.pop('foreign'), (
            {'key': 'uid', 'target': 'users.uid', 'onupdate': None, 'ondelete': 'CASCADE'},
        ))
        self.assertEqual(d.pop('columns'), [
            {'key': 'id', 'type': 'INTEGER NOT NULL', 'doc': ''},
            {'key': 'uid', 'type': 'INTEGER NOT NULL', 'doc': 'Owner'},
            {'key': 'serial', 'type': 'VARCHAR(32) NOT NULL', 'doc': ''},
        ])
        self.assertEqual(d.pop('relations'), [
            {'key': 'user', 'model': 'User', 'target': 'User(uid)', 'doc': 'Owner'}
        ])
        self.assertEqual(d, {})

