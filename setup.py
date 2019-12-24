#!/usr/bin/env python
""" Documentation extractor. """

from setuptools import setup, find_packages

setup(
    name='exdoc',
    version='0.1.3',
    author='Mark Vartanyan',
    author_email='kolypto@gmail.com',

    url='https://github.com/kolypto/py-exdoc',
    license='BSD',
    description=__doc__,
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    keywords=['documentation'],

    packages=find_packages(),
    scripts=[],
    entry_points={},

    python_requires='>=3.4',
    install_requires=[],
    extras_require={},
    include_package_data=True,
    test_suite='nose.collector',

    platforms='any',
    classifiers=[
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
