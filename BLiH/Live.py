''' Live.BiliBili Helper

'''

import struct
import re
import requests
import asyncio
import random
from BLiH import Utils
from BLiH import Config
from BLiH import User
from BLiH.Helper import *
from BLiH.Package import LivePackageGenerator, PackageHandlerProtocol

class LiveBiliBili(object):

    def __init__(self, userInstance = None, *, anonymous = True):
        if isinstance(userInstance, User.User):
            self.__uid = userInstance.uid
            self.__userInstance = userInstance
        elif anonymous is True:
            self.__uid = Utils.liveAnonymousUID()
            self.__userInstance = None
        else:
            raise TypeError

        self.__listenList = {}

    def listen(self, roomId = 0, *, alias = None, messageHandler = None):
        if alias is None:
            alias = 'room_{}'.format(roomId)

        if messageHandler is None:
            # raise TypeError('listen must be messageHandler')
            messageHandler = Utils.MessageHandler

        generator = LivePackageGenerator(loop = Helper.LoopInstance)
        Helper.LoopInstance.create_task(generator.join(roomId, self.__uid, messageHandler))

if __name__ == '__main__':
    live = LiveBiliBili()
    # Helper.LoopInstance.call_soon(live.listen, 1017)
    Helper.LoopInstance.run_forever()
    live.listen(1017)



