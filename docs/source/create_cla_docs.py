from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()
from builtins import *
from inspect import getmembers, isclass

from odm_sdk import cla

template = '''
{name}
{name_underline}

.. autoclass:: odm_sdk.{name}
        :members:
        :show-inheritance:

        .. autoattribute:: odm_sdk.{name}.APPLICATION_ID

'''


def main():
    with open('_cla_reference.rst', 'w') as f:
        for name, attr in getmembers(cla):
            if isclass(attr) and name != 'CLApplication' and issubclass(attr, cla.CLApplication):
                f.write(template.format(name=name, name_underline='-' * len(name)))
