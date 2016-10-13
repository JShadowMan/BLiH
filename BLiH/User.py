''' User Module

'''

import re
import json
import requests
from . import Exceptions, Storage, Config, TerminalQr

class User(object):
    def __init__(self, cookieJar, *, oauthKey = None):
        self.__sessionObject = requests.Session()

        if isinstance(cookieJar, requests.session().cookies.__class__):
            self.__sessionObject.cookies = cookieJar
        else:
            raise Exceptions.UserException('cookieJar type error')

        self.__user = {}
        self.__initUserInformation()

    def __initUserInformation(self):
        navJs = self.get(Config.GET_USER_INFO).text
        userInfo = json.loads(re.search('(loadLoginInfo\()([^\)].*)(\))', navJs).groups()[1])

        # TODO. Perfect this
        self.__user['name']  = userInfo.get('uname', None)
        self.__user['face']  = userInfo.get('face', None)
        self.__user['level'] = userInfo.get('level_info', {}).get('current_level', None)
        self.__user['money'] = userInfo.get('money', None)
        self.__user['vip']   = True if userInfo.get('vipStatus', 0) == 1 else False
        self.__user['exp']   = {
            'min': userInfo.get('level_info', {}).get('current_min', None),
            'current': userInfo.get('level_info', {}).get('current_exp', None),
            'next': userInfo.get('level_info', {}).get('next_exp', None)
        }

    def login(self, *, qrLogin = True, qrAdapter = TerminalQr.create, username = None, password = None):
        pass

    def get(self, url, *args, **kwargs):
        try:
            return self.__sessionObject.get(url = url, **kwargs)
        except requests.exceptions.ConnectionError as e:
            print(e)

    def post(self, url, *args, **kwargs):
        try:
            return self.__sessionObject.post(url = url, **kwargs)
        except requests.exceptions.ConnectionError as e:
            print(e)

    @property
    def name(self):
        return self.__user.get('name', None)

    @property
    def level(self):
        return self.__user.get('level', None)

    @property
    def money(self):
        return self.__user.get('money', None)

    @property
    def cookieJar(self):
        return self.__sessionObject.cookies

    @name.setter
    def name(self):
        # Change name
        pass

    def __str__(self):
        return '<User name = {}, level = {}, money = {}>'.format(self.name, self.level, self.money)

    def __repr__(self):
        return '<User name = {}, level = {}, money = {}>'.format(self.name, self.level, self.money)
