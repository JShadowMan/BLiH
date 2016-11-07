#!/usr/bin/env python
#
# Copyright (C) 2016 ShadowMan
#
from collections import namedtuple
from bilibili import Config

OperatorResult = namedtuple('OperatorResult', 'username operator status message other')

class Transaction(object):

    def __init__(self, user):
        self.__user_instance = user

    def get_sign_info(self):
        response = self.__user_instance.get(Config.GET_SIGN_INFO).json()

        return OperatorResult(self.__user_instance.name, 'GetSign', False, response.get('data').get('text').encode(Config.ENCODING), {
            'curMonth': response.get('data').get('curMonth'),
            'allDays': response.get('data').get('allDays'),
            'hadSignDays': response.get('data').get('hadSignDays')
        })

    def do_daily_sign(self):
        response = self.__user_instance.get(Config.LIVE_SIGN_DAILY).json()

        if response.get('code') is 0 and response.get('msg') == 'OK':
            return OperatorResult(self.__user_instance.name, 'Sign', True, response.get('data').get('text').encode(Config.ENCODING), {
                'allDays': response.get('data').get('allDays'),
                'hadSignDays': response.get('data').get('hadSignDays')
            })
        else:
            return OperatorResult(self.__user_instance.name, 'Sign', False, response.get('msg').encode(Config.ENCODING), None)

    def listen(self, roomId):
        pass
