''' BiliBili Helper Utils

'''

import sys
import random
import asyncio
import logging
from bilibili.Package import PackageHandlerProtocol

def liveAnonymousUID():
    return int(100000000000000 + (200000000000000 * random.random()))

class MessageHandler(PackageHandlerProtocol):

    def __init__(self, *, file = sys.stdout):
        super(MessageHandler, self).__init__()

        if hasattr(file, 'write'):
            self.__file = file
        else:
            logging.debug('messageHandler not set')
            raise TypeError('messageHandler')

    def onError(self, package):
        print(package)

    def onWelcome(self, contents):
        print(contents)

    def onHeartbeatResponse(self, contents):
        print(contents)

    def onAllowJoin(self):
        print('Join room complete')

        return True

    def onDanMuMessage(self, contents):
        print(contents)

    def onGift(self, contents):
        print(contents)