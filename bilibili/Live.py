''' Live.BiliBili Helper

'''

import struct
import re
import requests
import asyncio
import random
from bilibili import Utils
from bilibili import Config
from bilibili.User import User
from bilibili.Package import LivePackageGenerator, PackageHandlerProtocol

__all__ = [ 'LiveBiliBili' ]

class LiveBiliBili(object):

    def __init__(self, userInstance = None, *, anonymous = True, loop = None):

        self.__loop = loop

        if isinstance(userInstance, User):
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

        generator = LivePackageGenerator(loop = self.__loop)
        if self.__loop.is_running() is False:
            self.__loop.run_until_complete(generator.join(roomId, self.__uid, messageHandler))
        else:
            self.__loop.create_task(generator.join(roomId, self.__uid, messageHandler))
