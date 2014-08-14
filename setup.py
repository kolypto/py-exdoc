#!/usr/bin/env python
""" Documentation extractor. """

from setuptools import setup, find_packages

setup(
    name='exdoc',
    version='0.0.3-0',
    author='Mark Vartanyan',
    author_email='kolypto@gmail.com',

    url='https://github.com/kolypto/py-exdoc',
    license='BSD',
    description=__doc__,
    long_description=open('README.rst').read(),
    keywords=['documentation'],

    packages=find_packages(),
    scripts=[],
    entry_points={},

    install_requires=[
    ],
    extras_require={
        '_dev': ['wheel', 'nose', 'sqlalchemy', 'j2cli'],
    },
    include_package_data=True,
    test_suite='nose.collector',

    platforms='any',
    classifiers=[
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        #'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
