'''BLiH, BiliBili Helper

'''

__version__ = '1.0.0/10142016'
__author__  = 'ShadowMan(Wang) <shadowman@shellboot.com>'

import sys

if sys.version_info.major >= 3:
    if sys.version_info.minor < 5:
        from .Exceptions import FatalException
        raise FatalException('BiliBili Helper requires Python 3.5 or greater')

from .Helper import bliHelper

__all__ = [ 'bliHelper' ]
