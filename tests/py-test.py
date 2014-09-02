import unittest
import exdoc


#region Samples

def h(a, b, c=True, d=1, *args, **kwargs):
    """ Just a function

    :param a: A-value
    :type a: int
    :param b: B-value, no type
    :type c: None
    :param args: Varargs
    :param kwargs: Kwargs
    :return: nothing
    :rtype: None
    :raises AssertionError: sometimes
    """


class A(object):
    """ Empty class """


class B(A):
    """ Class with a constructor """

    def __init__(self, a, b=1, *args, **kwargs):
        """ Constructor """


class C(B):
    """ Subclass with methods """

    def f(self, a=1):
        """ Empty function

        :return: nothing
        """

    @staticmethod
    def s(a=2):
        """ Empty static method

        :rtype: None
        """

    @classmethod
    def c(cls, a=3): pass

    @property
    def p(self):
        """ Property doc """


class X:
    """ old-style class """

    def f(self, a=1): pass


class Y(X):
    """ Constructor documented in class body

        :param a: A
        :type a: int
    """

    def __init__(self, a, b=1): pass

#endregion


class PyTest(unittest.TestCase):
    """ Test Python helpers """

    def test_doc(self):
        """ Test doc() """

        # Module
        d = exdoc.doc(exdoc)
        self.assertEqual(d.pop('module'), None)
        self.assertEqual(d.pop('name'), 'exdoc')
        self.assertEqual(d.pop('qualname'), 'exdoc')
        self.assertTrue(d.pop('doc').startswith('Create a python file'))
        self.assertEqual(d, {})


        # Function
        d = exdoc.doc(h)
        self.assertEqual(d.pop('module'), 'py-test')
        self.assertEqual(d.pop('name'), 'h')
        self.assertEqual(d.pop('qualname'), 'h')
        self.assertEqual(d.pop('doc'), 'Just a function')
        self.assertEqual(d.pop('clsdoc'), '')
        self.assertEqual(d.pop('signature'),  'h(a, b, c=True, d=1, *args, **kwargs)')
        self.assertEqual(d.pop('qsignature'), 'h(a, b, c=True, d=1, *args, **kwargs)')
        self.assertEqual(d.pop('ret'), {'doc': 'nothing', 'type': 'None'})

        self.assertEqual(d.pop('args'), [
                {'name': 'a',        'type': 'int',  'doc': 'A-value'},
                {'name': 'b',        'type': None,   'doc': 'B-value, no type'},
                {'name': 'c',        'type': 'None', 'doc': '', 'default': True},
                {'name': 'd',        'type': None,   'doc': '', 'default': 1},
                {'name': '*args',    'type': None,   'doc': 'Varargs'},
                {'name': '**kwargs', 'type': None,   'doc': 'Kwargs'},
            ])
        self.assertEqual(d.pop('exc'), [
            {'name': 'AssertionError', 'doc': 'sometimes'}
        ])
        self.assertEqual(d, {})

        # Class: A
        d = exdoc.doc(A)
        self.assertEqual(d.pop('module'), 'py-test')
        self.assertEqual(d.pop('name'), 'A')
        self.assertEqual(d.pop('qualname'), 'A')
        self.assertIn('x.__init__(...)', d.pop('doc'))  # 'x.__init__(...) initializes x; see help(type(x)) for signature'  # Pythonic stuff here
        self.assertEqual(d.pop('clsdoc'), 'Empty class')
        self.assertEqual(d.pop('signature'),  'A()')
        self.assertEqual(d.pop('qsignature'), 'A()')
        self.assertEqual(d.pop('ret'), None)
        self.assertEqual(d.pop('args'), [])
        self.assertEqual(d.pop('exc'), [])
        self.assertEqual(d, {})

        # Class: B
        d = exdoc.doc(B)
        self.assertEqual(d.pop('module'), 'py-test')
        self.assertEqual(d.pop('name'), 'B')
        self.assertEqual(d.pop('qualname'), 'B')
        self.assertEqual(d.pop('doc'), 'Constructor')
        self.assertEqual(d.pop('clsdoc'), 'Class with a constructor')
        self.assertEqual(d.pop('signature'),  'B(a, b=1, *args, **kwargs)')
        self.assertEqual(d.pop('qsignature'), 'B(a, b=1, *args, **kwargs)')
        self.assertEqual(d.pop('ret'), None)
        self.assertEqual(d.pop('args'), [
            {'name': 'a', 'type': None, 'doc': ''},
            {'name': 'b', 'type': None, 'doc': '', 'default': 1},
            {'name': '*args', 'type': None, 'doc': ''},
            {'name': '**kwargs', 'type': None, 'doc': ''},
        ])
        self.assertEqual(d.pop('exc'), [])
        self.assertEqual(d, {})

        # Class: X
        d = exdoc.doc(X)
        self.assertEqual(d.pop('module'), 'py-test')
        self.assertEqual(d.pop('name'), 'X')
        self.assertEqual(d.pop('qualname'), 'X')
        self.assertEqual(d.pop('doc'), 'old-style class')
        self.assertEqual(d.pop('clsdoc'), 'old-style class')
        self.assertEqual(d.pop('signature'),  'X()')
        self.assertEqual(d.pop('qsignature'), 'X()')
        self.assertEqual(d.pop('ret'), None)
        self.assertEqual(d.pop('args'), [])
        self.assertEqual(d.pop('exc'), [])
        self.assertEqual(d, {})

        # Class: Y
        d = exdoc.doc(Y)
        self.assertEqual(d.pop('module'), 'py-test')
        self.assertEqual(d.pop('name'), 'Y')
        self.assertEqual(d.pop('qualname'), 'Y')
        self.assertEqual(d.pop('doc'), 'Constructor documented in class body')
        self.assertEqual(d.pop('clsdoc'), '')
        self.assertEqual(d.pop('signature'),  'Y(a, b=1)')
        self.assertEqual(d.pop('qsignature'), 'Y(a, b=1)')
        self.assertEqual(d.pop('ret'), None)
        self.assertEqual(d.pop('args'), [
            {'name': 'a', 'type': 'int', 'doc': 'A'},
            {'name': 'b', 'type': None, 'doc': '', 'default': 1},
        ])
        self.assertEqual(d.pop('exc'), [])
        self.assertEqual(d, {})

        # Method: C.f
        d = exdoc.doc(C.f)
        self.assertEqual(d.pop('module'), 'py-test')
        self.assertEqual(d.pop('name'), 'f')
        self.assertEqual(d.pop('qualname'), 'C.f')
        self.assertEqual(d.pop('doc'), 'Empty function')
        self.assertEqual(d.pop('clsdoc'), '')
        self.assertEqual(d.pop('signature'),  'f(a=1)')
        self.assertEqual(d.pop('qsignature'), 'C.f(a=1)')
        self.assertEqual(d.pop('ret'), {'type': None, 'doc': 'nothing'})
        self.assertEqual(d.pop('args'), [
            {'name': 'a', 'type': None, 'doc': '', 'default': 1}
        ])
        self.assertEqual(d.pop('exc'), [])
        self.assertEqual(d, {})

        # Static Method: C.s
        d = exdoc.doc(C.s)
        self.assertEqual(d.pop('module'), 'py-test')
        self.assertEqual(d.pop('name'), 's')
        self.assertEqual(d.pop('qualname'), 's')  # FIXME: wrong name for staticmethods!
        self.assertEqual(d.pop('doc'), 'Empty static method')
        self.assertEqual(d.pop('clsdoc'), '')
        self.assertEqual(d.pop('signature'),  's(a=2)')  # FIXME: wrong name for staticmethods!
        self.assertEqual(d.pop('qsignature'), 's(a=2)')  # FIXME: wrong name for staticmethods!
        self.assertEqual(d.pop('ret'), {'type': 'None', 'doc': ''})
        self.assertEqual(d.pop('args'), [
            {'name': 'a', 'type': None, 'doc': '', 'default': 2}
        ])
        self.assertEqual(d.pop('exc'), [])
        self.assertEqual(d, {})

        # Class Method: C.c
        d = exdoc.doc(C.c)
        self.assertEqual(d.pop('module'), 'py-test')
        self.assertEqual(d.pop('name'), 'c')
        self.assertEqual(d.pop('qualname'), 'C.c')
        self.assertEqual(d.pop('doc'), '')
        self.assertEqual(d.pop('clsdoc'), '')
        self.assertEqual(d.pop('signature'),  'c(a=3)')
        self.assertEqual(d.pop('qsignature'), 'C.c(a=3)')
        self.assertEqual(d.pop('ret'), None)
        self.assertEqual(d.pop('args'), [
            {'name': 'a', 'type': None, 'doc': '', 'default': 3}
        ])
        self.assertEqual(d.pop('exc'), [])
        self.assertEqual(d, {})

        # Property: C.p
        d = exdoc.doc(C.p)
        self.assertEqual(d.pop('module'), 'py-test')
        self.assertEqual(d.pop('name'), 'p')
        self.assertEqual(d.pop('qualname'), 'p')  # FIXME: wrong name for properties!
        self.assertEqual(d.pop('doc'), 'Property doc')
        self.assertEqual(d.pop('clsdoc'), '')
        self.assertEqual(d.pop('signature'),  'p')
        self.assertEqual(d.pop('qsignature'), 'p')
        self.assertEqual(d.pop('ret'), None)
        self.assertEqual(d.pop('args'), [])
        self.assertEqual(d.pop('exc'), [])
        self.assertEqual(d, {})

    def test_doc_specific(self):
        """ Test specific stuff on doc() """

        # Classes are represented correctly
        class A(object): pass
        def f(arg=A): pass
        d = exdoc.doc(f)
        self.assertEqual(d['signature'],  "f(arg=A)")
        self.assertEqual(d['qsignature'], "f(arg=A)")

        # Variadic arguments with classes
        class A(object):
            """ Blah blah

            :param a: First
            :param args: Many arguments
            :param kwargs: And keywords
            """

            def __init__(self, a=1, *args, **kwargs):
                pass

        d = exdoc.doc(A)
        self.assertEqual(d['signature'], "A(a=1, *args, **kwargs)")
        self.assertEqual(d['args'], [
            dict(name='a',          type=None, default=1,   doc='First'),
            dict(name='*args',      type=None,              doc='Many arguments'),
            dict(name='**kwargs',   type=None,              doc='And keywords')
        ])

    def test_getmembers(self):
        """ Test getmembers() """
        m = exdoc.getmembers(C)
        self.assertEqual(m, [
            ('c', C.c),
            ('f', C.f),
            ('p', C.p),
            ('s', C.s),
        ])

        # Try with predicate
        m = exdoc.getmembers(C, lambda key, value: key not in ('p', 's'))
        self.assertEqual(m, [
            ('c', C.c),
            ('f', C.f),
        ])

    def test_subclasses(self):
        """ Test subclasses() """
        self.assertEqual(exdoc.subclasses(A), [A, B, C])
        self.assertEqual(exdoc.subclasses(A, leaves=True), [C])
