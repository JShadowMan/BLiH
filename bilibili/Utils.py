''' BiliBili Helper Utils

'''

import re
import sys
import random
import aiohttp
import asyncio
import logging
import requests
import xml.etree.cElementTree as ET
from bilibili.Package import PackageHandlerProtocol
from bilibili import Config

def anonymous_uid():
    return int(100000000000000 + (200000000000000 * random.random()))

async def fetch(loop, *args, **kwargs):
    try:
        async with aiohttp.ClientSession(loop = loop) as client:
            async with client.get(*args, **kwargs) as response:
                if response.status is 200:
                    return await response.text()
                else:
                    raise Exception('request error', response.status)
    except Exception as e:
        logging.debug('in utils.fetch error', e)

async def get_real_room_id(loop, live_room_address):
    response = await fetch(loop, url = live_room_address)

    try:
        return re.search(r'(?<=ROOMID\s=\s)([\d]+)', response).group()
    except Exception as e:
        logging.debug('Utils.get_real_room_id error', e)

async def get_dan_mu_server_info(loop, live_room_id = None):
    request_server_address = 'http://live.bilibili.com/api/player?id=cid:{}'

    try:
        response = await fetch(loop, url = request_server_address.format(live_room_id))

        root = ET.fromstring('<root>' + response + '</root>')
        return root.find('server').text, Config.LIVE_SERVER_PORT
    except Exception as e:
        logging.debug('Utils.get_dan_mu_server_info error', e)

class MessageHandler(PackageHandlerProtocol):

    def __init__(self, *, file = sys.stdout):
        super(MessageHandler, self).__init__()

    def on_error_occurs(self, package):
        print(package)

    def on_welcome_message(self, contents):
        print(contents)

    def on_heartbeat_response(self, contents):
        print(contents)

    def on_allow_join(self):
        print('Join room complete')
        return True

    def on_dan_mu_message(self, contents):
        print(contents)

    def on_gift_message(self, contents):
        print(contents)

def check_args(args):
    pass