#!/usr/bin/env python
#
# Copyright (C) 2016 ShadowMan
#
#
#

import re
import sys
import json
import asyncio
import aiohttp
import logging
import requests
from collections import namedtuple
from bilibili import Exceptions, Config, TerminalQr, Utils

# Account Information
Account = namedtuple('Account', 'username password key')

# User Exp
Exp = namedtuple('Exp', 'min current next')

# User Profile
Profile = namedtuple('Profile', 'name level money exp other')

class User(object):
    _qr_adapter = TerminalQr.create
    _output_file = sys.stdout

    def __init__(self, qr = True, *, loop = None, username = None, password = None, alias = None, print_handle = None,
                 cookies = None):
        if loop is None:
            loop = asyncio.get_event_loop()
        self.__async_loop = loop
        self.__session_object = aiohttp.ClientSession(loop = self.__async_loop)

        if cookies is not None:
            self.__session_object.cookie_jar._cookies = cookies

        new_event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_event_loop)
        if cookies is not None:
            new_event_loop.run_until_complete(self.update_profile())
        else:
            new_event_loop.run_until_complete(self.__init_account(qr, username, password, print_handle))
        new_event_loop.stop()
        asyncio.set_event_loop(self.__async_loop)

    async def __init_account(self, qr, username, password, print_handle):
        if username is not None and password is not None:
            self.__account = await self.__login_with_pw(username, password)
        elif qr is True:
            self.__account = await self.__login_with_qr(print_handle)
        self.__profile = await self.__init_profile()

    @classmethod
    def factory(cls, username, password, OAuthKey, cookieJar):
        pass

    # Async HTTP Method: GET
    async def async_get(self, *args, **kwargs):
        try:
            async with self.__session_object.get(*args, **kwargs) as response:
                if response.status is 200:
                    return await response.text()
                else:
                    raise Exception('request error', response.status)
        except requests.exceptions.ConnectionError as e:
            raise Exceptions.NetworkException('request timeout')
        except RuntimeError as e:
            logging.warning(str(e))
            async with aiohttp.ClientSession(loop = asyncio.get_event_loop()) as client:
                client.cookie_jar._cookies = self.__session_object.cookie_jar._cookies
                async with client.get(*args, **kwargs) as response:
                    if response.status is 200:
                        return await response.text()
                    else:
                        raise Exception('request error', response.status)

    # Async HTTP Method: POST
    async def async_post(self, *args, **kwargs):
        try:
            async with self.__session_object.post(*args, **kwargs) as response:
                if response.status is 200:
                    return await response.text()
                else:
                    raise Exception('request error', response.status)
        except requests.exceptions.ConnectionError as e:
            raise Exceptions.NetworkException('request timeout')
        except RuntimeError as e:
            async with aiohttp.ClientSession(loop = asyncio.get_event_loop()) as client:
                client.cookie_jar._cookies = self.__session_object.cookie_jar._cookies
                async with client.post(*args, **kwargs) as response:
                    if response.status is 200:
                        return await response.text()
                    else:
                        raise Exception('request error', response.status)

    async def update_profile(self):
        self.__profile = await self.__init_profile()

    async def __login_with_pw(self, username, password):
        key = self.__get_oauth_key()

        # TODO

        return Account(username, password, key)

    async def __login_with_qr(self, print_handle):
        key = await self.__get_oauth_key()

        logging.info('Authentication of identity, using qr code')
        with User._qr_adapter(Utils.login_with_qr_url(key)) as qc:
            if asyncio.iscoroutine(print_handle):
                await print_handle(str(qc))
            else:
                print_handle(str(qc))

        await self.__check_login_status(key, print_handle)
        return Account(None, None, key)

    async def __get_oauth_key(self):
        logging.info('From the server get a oauth key')
        response = json.loads(await self.async_get(Config.GET_OAUTH_KEY))

        try:
            logging.info('Gets the OAuth key completed')
            return response.get('data', {}).get('oauthKey')
        except KeyError:
            raise Exceptions.FatalException('Error occurred getting oauth key, official API may be changed')
        except Exceptions.NetworkException:
            raise

    async def __check_login_status(self, oauth_key, print_handle):
        for times in range(Config.RE_LOGIN_COUNT):
            for sec in range(0, Config.QR_EXPIRED_TIME, Config.DETECT_LOGIN_STATUS_INTERVAL):
                info = json.loads(await self.async_post(Config.LOGIN_INFO_URL, data = {'oauthKey': oauth_key}))

                if info.get('status') is True:
                    break
                asyncio.sleep(Config.DETECT_LOGIN_STATUS_INTERVAL)
            else:
                logging.info('qr code expired, refresh qr code ...')
                with self._qr_adapter(Utils.login_with_qr_url(oauth_key)) as qc:
                    if asyncio.iscoroutine(print_handle):
                        await print_handle(str(qc))
                    print_handle(str(qc))
            break
        else:
            logging.error('The number of retries exceeds the limit')

    async def __init_profile(self):
        navJs = await self.async_get(Config.GET_USER_INFO)
        userInfo = json.loads(re.search(r'(loadLoginInfo\()([^\)].*)(\))', navJs).groups()[1])

        # TODO. Perfect this
        name  = userInfo.get('uname')
        level = userInfo.get('level_info', {}).get('current_level')
        money = userInfo.get('money')
        exp   = {
            'min': userInfo.get('level_info', {}).get('current_min'),
            'current': userInfo.get('level_info', {}).get('current_exp'),
            'next': userInfo.get('level_info', {}).get('next_exp')
        }
        other = {
            'vip': True if userInfo.get('vipStatus', False) == 1 else False,
            'face': userInfo.get('face')
        }
        return Profile(name, level, money, exp, other)

    def __str__(self):
        return '<User name = {}, level = {}, money = {}, exp={}/{}>'.format(
            self.name, self.level, self.money, self.exp['current'], self.exp['next']
        )

    def __repr__(self):
        return '<User name = {}, level = {}, money = {}, exp={}/{}>'.format(
            self.name, self.level, self.money, self.exp['current'], self.exp['next']
        )

    @property
    def name(self):
        return self.__profile.name

    @property
    def level(self):
        return self.__profile.level

    @property
    def money(self):
        return self.__profile.money
    
    @property
    def exp(self):
        return self.__profile.exp

    @property
    def username(self):
        return self.__account.username

    @property
    def password(self):
        return self.__account.password

    @property
    def oauth_key(self):
        return self.__account.key

    @property
    def uid(self):
        return Utils.anonymous_uid()

    @property
    def face(self):
        return self.__profile.other['face']

    @property
    def cookie_jar(self):
        return self.__session_object.cookie_jar

