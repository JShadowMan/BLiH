'''Object Storage

'''

import io
import os
import pickle
import logging

def dump(file, data):
    if isinstance(file, str):
        with open(file, 'wb') as fd:
            pickle.dump(data, fd, pickle.HIGHEST_PROTOCOL)
    elif hasattr(file, 'write') and hasattr(file, 'read'):
        pickle.dump(data, file, pickle.HIGHEST_PROTOCOL)
    else:
        raise TypeError("file must have a 'write' attribute")

def load(file):
    try:
        if isinstance(file, str):
            with open(file, 'rb') as f:
                return SessionStorage(f)
        elif hasattr(file, 'write') and hasattr(file, 'read'):
            return SessionStorage(file)
        else:
            raise TypeError("file must have a 'write' attribute")
    except Exception as e:
        logging.debug('In Storage: %s' % ( e ))
        raise

class SessionStorage(dict):

    def __init__(self, file):
        contents = {}
        if os.path.getsize(file.name):
            try:
                contents = pickle.load(file)
            except Exception as e:
                print('in SessionStorage::__init__ error', e)
        else:
            raise EOFError('session file is empty')
        super(SessionStorage, self).__init__(contents)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val and exc_tb:
            raise exc_val
