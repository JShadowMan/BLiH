'''BLiH, BiliBili Helper

'''

import logging
from .Helper import Helper

__all__ = [ 'bliHelper' ]

def enableLogging():
    logging.basicConfig(level = logging.INFO, format = '%(asctime)s %(levelname)s: %(message)s',
                    datefmt = '%d %b %Y %H:%M:%S')

def bliHelper(QRLogin = True, *, username = None, password = None, logging = True, background = True, logfile = None):
    if logging is True:
        enableLogging()

    if (username is not None) and (password is not None):
        return Helper(username=username, password=password)

    return Helper(QRLogin = True)