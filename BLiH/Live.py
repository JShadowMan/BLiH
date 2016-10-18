''' Live.BiliBili Helper

'''

import struct
import re
import requests
import asyncio
import random
from BLiH import Config, User
from BLiH.Helper import *
from BLiH.Utils import *
from BLiH.Package import LivePackageGenerator, PackageHandlerProtocol

class LiveBiliBili(object):

    def __init__(self, userInstance = None, *, anonymous = True):
        if isinstance(userInstance, User):
            self.__uid = userInstance.uid
            self.__userInstance = userInstance
        elif anonymous is True:
            self.__uid = liveAnonymousUID()
            self.__userInstance = None
        else:
            pass

        self.__listenList = {}

    def listen(self, roomId = 0, *, alias = None):
        if alias is None:
            alias = 'room_{}'.format(roomId)
        generator = LivePackageGenerator(loop = Helper.LoopInstance)
        Helper.LoopInstance.run_until_complete(generator.join(roomId, self.__uid, lambda : MessageHandler()))
        # Helper.LoopInstance.create_task(generator.join(roomId, self.__uid, lambda : MessageHandler()))

class MessageHandler(PackageHandlerProtocol):
    def onAllowJoin(self):
        print('Join Live Room Completed')
        return True

    def onDanMuMessage(self, contents):
        print('{} Say: {}'.format(contents.name, contents.message))

    def onGift(self, contents):
        print('{} sent out {} {}'.format(contents.name, contents.count, contents.gift))

    def onHeartbeatResponse(self, contents):
        print('Live Room People Count: {}'.format(contents.peopleCount))

    def onWelcome(self, contents):
        print('Welcome {}'.format(contents.name))

    def onError(self, package):
        print('Error occurs', package)

if __name__ == '__main__':
    live = LiveBiliBili()
    live.listen(584704)
