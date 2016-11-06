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
import logging
import requests
from collections import namedtuple
from bilibili import Exceptions, Config, TerminalQr, Live, Utils

# Account Information
Account = namedtuple('Account', 'username password key')

# User Exp
Exp = namedtuple('Exp', 'min current next')

# User Profile
Profile = namedtuple('Profile', 'name level money exp other')

class User(object):
    QrAdapter = TerminalQr.create
    OutFile   = sys.stdout

    def __init__(self, QrLogin = True, *, username = None, password = None, alias = None):
        self.__sessionObject = self.__initSession()

        if username is not None and password is not None:
            self.__account = self.__login(username, password)
        elif QrLogin is True:
            self.__account = self.__qrLogin()

        self.__profile = self.__initProfile()
        self.__live = self.__initLiveProfile()

    @classmethod
    def factory(cls, username, password, OAuthKey, cookieJar):
        pass

    # HTTP Method: GET
    def get(self, *args, **kwargs):
        try:
            return self.__sessionObject.get(*args, **kwargs)
        except requests.exceptions.ConnectionError as e:
            logging.debug('User::get() %s' % ( e ))
            raise Exceptions.NetworkException

    # HTTP Method: POST
    def post(self, *args, **kwargs):
        try:
            return self.__sessionObject.post(*args, **kwargs)
        except requests.exceptions.ConnectionError as e:
            logging.debug('User::post() %s' % ( e ))
            raise Exceptions.NetworkException

    def profileUpdate(self):
        self.__profile = self.__initProfile()

    def live(self):
        return self.__live

    def __initSession(self):
        session = requests.Session()

        for times in range(Config.RE_LOGIN_COUNT):
            try:
                logging.info('Initializes a new session')
                session.get(Config.INIT_COOKIES_START, stream = True).close()
                break
            except requests.exceptions.ConnectionError:
                pass

        return session

    def __login(self, username, password):
        key = self.__getOAuthKey()

        # TODO

        return Account(username, password, key)

    def __qrLogin(self):
        key = self.__getOAuthKey()

        logging.info('Authentication of identity, using QrLogin')
        with User.QrAdapter(Config.QrLoginUrl(key)) as qc:
            print(qc, file = self.OutFile)

        self.__checkLoginInfo(key) # await

        return Account(None, None, key)

    def __initLiveProfile(self):
        return Live.LiveBiliBili()

    def __getOAuthKey(self):
        logging.info('From the server gets a OAuth key')
        response = self.get(Config.GET_OAUTH_KEY).json()
        try:
            logging.info('Gets the OAuth key completed')
            return response.get('data').get('oauthKey')
        except KeyError:
            raise Exceptions.FatalException('Error occurred getting OAuth key, official API may be changed')
        except Exceptions.NetworkException:
            raise

    def __checkLoginInfo(self, oauthKey):
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

                with self.QrAdapter(Config.QrLoginUrl(oauthKey)) as qc:
                    print(qc, file = self.OutFile)

            if info.get('status', None) is True:
                if 'data' in info and 'url' in info['data']:
                    try:
                        # Gets the child domain cookies ?
                        # self.__sessionObject.get(info['data']['url']).close()
                        pass
                    except requests.exceptions.ConnectionError:
                        logging.debug('User::__checkLoginInfo')
                        raise
                break
        else:
            self.__terminate(logging.error, 'The number of retries exceeds the limit.')


    def __initProfile(self):
        navJs = self.get(Config.GET_USER_INFO).text
        userInfo = json.loads(re.search('(loadLoginInfo\()([^\)].*)(\))', navJs).groups()[1])

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
    def cookieJar(self):
        return self.__sessionObject.cookies

    @property
    def username(self):
        return self.__account.username

    @property
    def password(self):
        return self.__account.password

    @property
    def oauthKey(self):
        return self.__account.key

    @property
    def uid(self):
        return Utils.liveAnonymousUID()

    @name.setter
    def name(self):
        # Change name
        pass
