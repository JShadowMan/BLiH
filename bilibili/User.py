#!/usr/bin/env python
#
# Copyright (C) 2016 ShadowMan
#
#
#

import re
import sys
import json
import time
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

    def __init__(self, qr = True, *, username = None, password = None, alias = None):
        self.__session_object = self.__init_session_object()

        if username is not None and password is not None:
            self.__account = self.__login_with_pw(username, password)
        elif qr is True:
            self.__account = self.__login_with_qr()

        self.__profile = self.__init_profile()

    @classmethod
    def factory(cls, username, password, OAuthKey, cookieJar):
        pass

    # HTTP Method: GET
    def get(self, *args, **kwargs):
        try:
            return self.__session_object.get(*args, **kwargs)
        except requests.exceptions.ConnectionError as e:
            raise Exceptions.NetworkException('request timeout')

    # HTTP Method: POST
    def post(self, *args, **kwargs):
        try:
            return self.__session_object.post(*args, **kwargs)
        except requests.exceptions.ConnectionError as e:
            logging.debug('User::post() %s' % ( e ))
            raise Exceptions.NetworkException

    def update_profile(self):
        self.__profile = self.__init_profile()

    def __init_session_object(self):
        session = requests.Session()

        for times in range(Config.RE_LOGIN_COUNT):
            try:
                logging.info('Initializes a new session')
                session.get(Config.INIT_COOKIES_START, stream = True).close()
                break
            except requests.exceptions.ConnectionError:
                pass

        return session

    def __login_with_pw(self, username, password):
        key = self.__get_oauth_key()

        # TODO

        return Account(username, password, key)

    def __login_with_qr(self):
        key = self.__get_oauth_key()

        logging.info('Authentication of identity, using QrLogin')
        with User._qr_adapter(Config.login_with_qr_url(key)) as qc:
            print(qc, file = self._output_file)

        self.__check_login_status(key) # await

        return Account(None, None, key)

    def __get_oauth_key(self):
        logging.info('From the server gets a OAuth key')
        response = self.get(Config.GET_OAUTH_KEY).json()
        try:
            logging.info('Gets the OAuth key completed')
            return response.get('data').get('oauthKey')
        except KeyError:
            raise Exceptions.FatalException('Error occurred getting OAuth key, official API may be changed')
        except Exceptions.NetworkException:
            raise

    def __check_login_status(self, oauthKey):
        for times in range(Config.RE_LOGIN_COUNT):
            info = None
            for sec in range(0, Config.QR_EXPIRED_TIME, Config.DETECT_LOGIN_STATUS_INTERVAL):
                info = self.post(Config.LOGIN_INFO_URL, data = { 'oauthKey': oauthKey }).json()

                if info.get('status', None) is True:
                    break
                else:
                    time.sleep(Config.DETECT_LOGIN_STATUS_INTERVAL)
            else:
                logging.info('QrCode expired, refresh QrCode ...')

                with self._qr_adapter(Config.login_with_qr_url(oauthKey)) as qc:
                    print(qc, file = self._output_file)

            if info.get('status', None) is True:
                if 'data' in info and 'url' in info['data']:
                    try:
                        # Gets the child domain cookies ?
                        # self.__session_object.get(info['data']['url']).close()
                        pass
                    except requests.exceptions.ConnectionError:
                        logging.debug('User::__checkLoginInfo')
                        raise
                break
        else:
            self.__terminate(logging.error, 'The number of retries exceeds the limit.')


    def __init_profile(self):
        navJs = self.get(Config.GET_USER_INFO).text
        userInfo = json.loads(re.search(r'(loadLoginInfo\()([^\)].*)(\))', navJs).groups()[1])

        # TODO. Perfect this
        name  = userInfo.get('uname', None)
        level = userInfo.get('level_info', {}).get('current_level', None)
        money = userInfo.get('money', None)
        exp   = {
            'min': userInfo.get('level_info', {}).get('current_min', None),
            'current': userInfo.get('level_info', {}).get('current_exp', None),
            'next': userInfo.get('level_info', {}).get('next_exp', None)
        }
        other = {
            'vip': True if userInfo.get('vipStatus', 0) == 1 else False,
            'face': userInfo.get('face', None)
        }
        return Profile(name, level, money, exp, other)

    def __terminate(self, handler, message):
        handler(message)

    def __str__(self):
        return '<User name = {}, level = {}, money = {}>'.format(self.name, self.level, self.money)

    def __repr__(self):
        return '<User name = {}, level = {}, money = {}>'.format(self.name, self.level, self.money)

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

