''' User Module

'''

import re
import json
import requests
from . import Exception, Storage, Config

class User(object):
    def __init__(self, cookieJar, *, oauthKey = None):
        self.__sessionObject = requests.Session()
        self.__sessionObject.cookies = cookieJar

        self.__user = {}
        self.__initUserInformation()

        print(self.__user['name'], self.__user['level'], self.__user['money'])

    def __initUserInformation(self):
        navJs = self.__sessionObject.get('http://interface.bilibili.com/nav.js').text
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

    @property
    def name(self):
        return self.__user.get('name', None)

    @property
    def level(self):
        return self.__user.get('level', None)

    @property
    def money(self):
        return self.__user.get('money', None)

    @name.setter
    def __name__set(self):
        # Change name
        pass

    def __str__(self):
        return '<User name = {}, level = {}, money = {}>'.format(self.name, self.level, self.money)

    def __repr__(self):
        return '<User name = {}, level = {}, money = {}>'.format(self.name, self.level, self.money)