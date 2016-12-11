''' BiliBili Helper Utils

'''

import re
import sys
import random
import aiohttp
import logging
import xml.etree.cElementTree as ET
from urllib.parse import urljoin
from bilibili import Config, Exceptions

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

async def auto_get_real_room_id(loop, live_room_address, *, live_room_id = None):
    if live_room_id is None:
        if isinstance(live_room_address, int):
            live_room_address = str(live_room_address)
        if isinstance(live_room_address, str) and live_room_address.isalnum():
            live_room_address = urljoin(Config.LIVE_ROOM_ADDRESS_PREFIX, live_room_address)
        elif not isinstance(live_room_address, str):
            raise TypeError('live_room_address must be str or int')

        live_room_id = await get_real_room_id(loop, live_room_address)
        if live_room_id is None:
            raise Exception('live room not found of {}'.format(live_room_address))
        live_room_id = int(live_room_id)
    elif not isinstance(live_room_id, int):
        live_room_id = int(live_room_id)
    return live_room_id

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


def login_with_qr_url(oauth_key = None):
    if oauth_key is None:
        raise Exceptions.ConfigException('oauth_key parameter must be specified')
    else:
        if len(oauth_key) != 32:
            raise Exceptions.ConfigException('oauth_key format error, length is not 32')
        return Config.QR_LOGIN_URL.format(oauth_key)

def check_args(args):
    pass