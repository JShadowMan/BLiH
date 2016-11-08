''' Live.BiliBili Helper

'''

import struct
import re
import requests
import asyncio
import random
from urllib.parse import urljoin
from bilibili import Utils
from bilibili import Config
from bilibili.User import User
from bilibili.Package import LivePackageGenerator, PackageHandlerProtocol

__all__ = [ 'LiveBiliBili' ]

class LiveBiliBili(object):

    _live_room_address_prefix = 'http://live.bilibili.com/'

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

        self.__listenList = {}

    async def listen(self, live_room_address, message_handler, *, live_room_id = None, alias = None):
        if live_room_id is None:
            if isinstance(live_room_address, int):
                live_room_address = str(live_room_address)
            if isinstance(live_room_address, str) and live_room_address.isalnum():
                live_room_address = urljoin(self._live_room_address_prefix, live_room_address)
            elif not isinstance(live_room_address, str):
                raise TypeError('live_room_address must be str or int')

            live_room_id = await Utils.get_real_room_id(self.__loop, live_room_address)
        elif not isinstance(live_room_id, int):
            live_room_id = int(live_room_id)

        if alias is None:
            alias = 'live_room_{}'.format(live_room_id)

        if message_handler is None:
            raise TypeError('listen require message_handler')

        generator = LivePackageGenerator(loop = self.__loop)
        if self.__loop.is_running() is False:
            self.__loop.run_until_complete(generator.join(live_room_id, self.__uid, message_handler))
        else:
            self.__loop.create_task(generator.join(live_room_id, self.__uid, message_handler))
