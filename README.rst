|Build Status|

ExDoc
=====

Documentation extractor.

Extracts pieces of documentation from your code to build a document
which can be fed to template processors.

Output can be in JSON, YAML, whatever. Use any command-line templating
engine, like `j2cli <https://github.com/kolypto/j2cli>`__, to render
templates from it.

It does not do any automatic background magic: it just offers helpers
which allows you to extract the necessary pieces.

Collector
=========

Extractors
----------

.. |Build Status| image:: https://api.travis-ci.org/kolypto/py-exdoc.png?branch=master
   :target: https://travis-ci.org/kolypto/py-exdoc
