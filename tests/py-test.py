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


class A:
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

class Y:
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
        self.assertEqual(d.pop('example'), None)
        self.assertEqual(d, {})

        # Class: A
        d = exdoc.doc(A)
        self.assertEqual(d.pop('module'), 'py-test')
        self.assertEqual(d.pop('name'), 'A')
        self.assertEqual(d.pop('qualname'), 'A')
        self.assertEqual(d.pop('doc'), 'Empty class')
        self.assertEqual(d.pop('clsdoc'), 'Empty class')

        self.assertEqual(d.pop('signature'),  'A(*args, **kwargs)')
        self.assertEqual(d.pop('qsignature'), 'A(*args, **kwargs)')
        self.assertEqual(d.pop('ret'), None)
        self.assertEqual(d.pop('args'), [
            {'name': '*args', 'type': None, 'doc': ''},
            {'name': '**kwargs', 'type': None, 'doc': ''},
        ])
        self.assertEqual(d.pop('exc'), [])
        self.assertEqual(d.pop('example'), None)
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
        self.assertEqual(d.pop('example'), None)
        self.assertEqual(d, {})

        # Method: C.f
        d = exdoc.doc(C.f, C)
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
        self.assertEqual(d.pop('example'), None)
        self.assertEqual(d, {})

        # Static Method: C.s
        d = exdoc.doc(C.s, C)
        self.assertEqual(d.pop('module'), 'py-test')
        self.assertEqual(d.pop('name'), 's')
        self.assertEqual(d.pop('qualname'), 'C.s')
        self.assertEqual(d.pop('qsignature'), 'C.s(a=2)')
        self.assertEqual(d.pop('signature'), 's(a=2)')
        self.assertEqual(d.pop('doc'), 'Empty static method')
        self.assertEqual(d.pop('clsdoc'), '')
        self.assertEqual(d.pop('ret'), {'type': 'None', 'doc': ''})
        self.assertEqual(d.pop('args'), [
            {'name': 'a', 'type': None, 'doc': '', 'default': 2}
        ])
        self.assertEqual(d.pop('exc'), [])
        self.assertEqual(d.pop('example'), None)
        self.assertEqual(d, {})

        # Class Method: C.c
        d = exdoc.doc(C.c, C)
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
        self.assertEqual(d.pop('example'), None)
        self.assertEqual(d, {})

        # Property: C.p
        d = exdoc.doc(C.p)
        self.assertEqual(d.pop('module'), 'py-test')
        self.assertEqual(d.pop('name'), 'p')
        self.assertEqual(d.pop('qualname'), 'C.p')  # FIXME: wrong name for properties!
        self.assertEqual(d.pop('qsignature'), 'p')  # FIXME: wrong name for properties!
        self.assertEqual(d.pop('signature'), 'p')
        self.assertEqual(d.pop('doc'), 'Property doc')
        self.assertEqual(d.pop('clsdoc'), '')
        self.assertEqual(d.pop('ret'), None)
        self.assertEqual(d.pop('args'), [])
        self.assertEqual(d.pop('exc'), [])
        self.assertEqual(d.pop('example'), None)
        self.assertEqual(d, {})

    def test_doc_specific(self):
        """ Test specific stuff on doc() """

        # Classes are represented correctly
        class A: pass
        def f(arg=A): pass
        d = exdoc.doc(f)
        self.assertEqual(d['signature'],  "f(arg=A)")
        self.assertEqual(d['qsignature'], "PyTest.test_doc_specific.<locals>.f(arg=A)")

        # Variadic arguments with classes
        class A:
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

    def test_google_docstring(self):
        # === Test: Function
        def f1_args(a, b, c):
            """ Google format

                Args:
                    a: first
                    b (int): second
                        multiline
                    c: third
                        multiline
            """

        d = exdoc.doc(f1_args)
        self.assertEqual(d['doc'], 'Google format')
        self.assertEqual(d['ret'], None)
        self.assertEqual(d['args'], [
            {'name': 'a', 'type': None, 'doc': 'first'},
            {'name': 'b', 'type': 'int', 'doc': 'second\nmultiline'},
            {'name': 'c', 'type': None, 'doc': 'third\nmultiline'},
        ])
        self.assertEqual(d['exc'], [])
        self.assertEqual(d['example'], None)


        def f2_returns(a, b, c):
            """ Google 2

                Args:
                    a:
                    b:
                        something
                Returns:
                    nothing, really
            """
        d = exdoc.doc(f2_returns)
        self.assertEqual(d['doc'], 'Google 2')
        self.assertEqual(d['ret'], {'type': None, 'doc': 'nothing, really'})
        self.assertEqual(d['args'], [
            {'name': 'a', 'type': None, 'doc': ''},
            {'name': 'b', 'type': None, 'doc': 'something'},
            {'name': 'c', 'type': None, 'doc': ''},
        ])
        self.assertEqual(d['exc'], [])
        self.assertEqual(d['example'], None)

        def f3_raises(a):
            """ Google 3

            Arguments:
                a:
            Returns:
                None: nothing
                multiline
            Raises:
                ValueError: bad data
                KeyError: bad idea
            """
        d = exdoc.doc(f3_raises)
        self.assertEqual(d['doc'], 'Google 3')
        self.assertEqual(d['ret'], {'type': 'None', 'doc': 'nothing\nmultiline'})
        self.assertEqual(d['args'], [
            {'name': 'a', 'type': None, 'doc': ''},
        ])
        self.assertEqual(d['exc'], [
            {'name': 'ValueError', 'doc': 'bad data'},
            {'name': 'KeyError', 'doc': 'bad idea'},
        ])
        self.assertEqual(d['example'], None)

        def f4_example():
            """ Google 4
            Multiline

            Example:
                f4_example() #-> good results
                yeehaw
            """
        d = exdoc.doc(f4_example)
        self.assertEqual(d['doc'], 'Google 4\nMultiline')
        self.assertEqual(d['args'], [])
        self.assertEqual(d['exc'], [ ])
        self.assertEqual(d['example'], 'f4_example() #-> good results\nyeehaw')

        # === Test: Class
        class ClsDocstr:
            """
            Example class

            Attrs:
                a: first
                b(int): second
                c: third

            Example:
                hey :)
            """

        d = exdoc.doc(ClsDocstr)
        # TODO: class attributes unsupported yet

    def test_getmembers(self):
        """ Test getmembers() """
        m = exdoc.getmembers(C)
        self.assertEqual(list(m), [
            ('c', C.c),
            ('f', C.f),
            ('p', C.p),
            ('s', C.s),
        ])

        # Try with predicate
        m = exdoc.getmembers(C, lambda key, value: key not in ('p', 's'))
        self.assertEqual(list(m), [
            ('c', C.c),
            ('f', C.f),
        ])

    def test_subclasses(self):
        """ Test subclasses() """
        self.assertEqual(exdoc.subclasses(A), [A, B, C])
        self.assertEqual(exdoc.subclasses(A, leaves=True), [C])
