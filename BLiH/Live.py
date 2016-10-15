''' Live.BiliBili Helper

'''

import struct
import re
import requests
import asyncio
import random
from BLiH import Config, User
from BLiH.Utils import *
from BLiH.Package import LivePackageGenerator, LivePackageParser

class LiveBiliBili(object):

    def __init__(self, userInstance = None, *, anonymous = True):
        if isinstance(userInstance, User.User):
            self.__userInstance = userInstance
        elif anonymous is True:
            self.__userInstance = None
        else:
            pass

        self.__listenList = {}

    def listen(self, roomId = 0, *, alias = None):
        if alias is None:
            alias = 'room_{}'.format(roomId)
        generator = LivePackageGenerator()
        generator.join(roomId, self.__userInstance.uid if self.__userInstance is not None else liveAnonymousUID())

if __name__ == '__main__':
    live = LiveBiliBili()
    live.listen(45104)
