#! /usr/bin/env python

from exdoc import doc, getmembers
import json

import exdoc, exdoc.py, exdoc.sa


def docmodule(module):
    return { name: doc(value)
             for name, value in getmembers(module) + [('__module__', module)] }

data = {
    'exdoc': {
        '__module__': doc(exdoc),
        'py': docmodule(exdoc.py),
        'sa': docmodule(exdoc.sa)
    }
}

print json.dumps(data, indent=2)
