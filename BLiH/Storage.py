'''Object Storage

'''

import pickle, io
import logging

def dump(file, data):
    if isinstance(file, str):
        with open(file, 'wb') as f:
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
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

class SessionStorage(dict):

    def __init__(self, file):
        contents = {}
        if file.seek(0, io.SEEK_SET) == 0 and file.seek(0, io.SEEK_END) > 0:
            file.seek(0, io.SEEK_SET)

            contents = pickle.load(file)

        super(SessionStorage, self).__init__(contents)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

