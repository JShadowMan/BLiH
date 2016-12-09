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

    def __init__(self, user_instance = None, *, anonymous = True, loop = None):
        if loop is None:
            loop = asyncio.get_event_loop()
        self.__loop = loop

        if isinstance(user_instance, User):
            self.__uid = user_instance.uid
            self.__userInstance = user_instance
        elif anonymous is True:
            self.__uid = Utils.anonymous_uid()
            self.__userInstance = None
        else:
            raise TypeError

    async def listen(self, live_room_address, message_handler, *args, live_room_id = None, alias = None):
        live_room_id = await Utils.auto_get_real_room_id(self.__loop, live_room_address, live_room_id = live_room_id)

        if alias is None:
            alias = 'live_room_{}'.format(live_room_id)
        if message_handler is None:
            raise TypeError('listen require message_handler')

        generator = LivePackageGenerator(loop = self.__loop)
        return await generator.join(live_room_id, self.__uid, message_handler, *args)

    async def get_live_room_info(self, live_room_id):
        pass
