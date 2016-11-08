''' BiliBili Helper Utils

'''

import re
import sys
import random
import aiohttp
import asyncio
import logging
import requests
from bilibili.Package import PackageHandlerProtocol

def anonymous_uid():
    return int(100000000000000 + (200000000000000 * random.random()))

async def fetch(loop, *args, **kwargs):
    try:
        async with aiohttp.ClientSession(loop = loop, connector=aiohttp.TCPConnector(verify_ssl=False)) as client:
            async with client.get(*args, **kwargs) as response:
                if response.status is 200:
                    return await response.text()
                else:
                    raise Exception('request error', response.status)
    except Exception as e:
        print('in utils.fetch error', e)

async def get_real_room_id(loop, live_room_address):
    response = await fetch(loop, url = live_room_address)

    try:
        return re.search(r'(?<=ROOMID\s=\s)([\d]+)', response).group()
    except Exception as e:
        print('Utils.get_real_room_id error', e)

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