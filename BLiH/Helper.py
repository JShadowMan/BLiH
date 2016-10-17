'''BiliBili Helper

'''

import os
import logging
import asyncio
from collections import namedtuple
from BLiH import Exceptions, Storage, Config, TerminalQr
from BLiH.User import User
from BLiH.User import Account

def bliHelper(QRLogin = True, *, storage = True, account = (None, None), log = True, logfile = None,
              afterLogin = True, multiUser = False, autoDump = True):
    if log is True:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s',
                            datefmt='%d %b %Y %H:%M:%S')

    helper = Helper(storage = storage)
    if helper.accountSize() != 0 and afterLogin is False:
        return helper

    if multiUser is False:
        multiUser = 1

    for index in range(min(multiUser, Config.MAX_USER_COUNT)):
        if isinstance(account, Account):
            account = [ account ]
        elif not isinstance(account, list):
            raise TypeError('Account must be Account or list type')

        try:
            username, password = account[index]
        except IndexError:
            username, password = (None, None)

        if (username is not None) and (password is not None):
            helper.login(username = username, password = password)
        elif QRLogin is True:
            helper.login()
        else:
            if helper.accountSize() is 0:
                raise Exceptions.FatalException('Params error')

    if autoDump is True:
        helper.dump()

    return helper

class Helper(object):

    __DUMP_FILE_NAME = 'userList.pkl'

    LoopInstance = asyncio.get_event_loop()

    def __init__(self, *, storage = True):
        self.__userList = {}
        self.__transaction = None # must be None

        if storage is True:
            self.__load()

    def login(self, QrLogin = True, *, username = None, password = None, storage = True, alias = None):
        if username is not None and password is not None:
            user = User(username = username, password = password)
        elif QrLogin is True:
            user = User(QrLogin = True)
        else:
            raise Exceptions.FatalException('login parameters are incorrect, type not specified')

        self.__userList[alias if alias is not None and isinstance(alias, str) else user.name ] = user
        logging.info('%s Login success' % ( user ))

    def dump(self):
        self.__dump()

    def accountSize(self):
        return len(self.__userList)

    def isExists(self, name):
        return name in self.__userList

    def select(self, name):
        if self.isExists(name):
            # self.__transaction = name
            return Transaction(self.__userList[name])

    def __dump(self):
        Storage.dump(self.__DUMP_FILE_NAME, self.__userList)

    def __load(self):
        if os.path.isfile(self.__DUMP_FILE_NAME) == False:
            return False

        logging.info('Dump file detected, using a saved session')
        with Storage.load(self.__DUMP_FILE_NAME) as userList:
            logging.info('Dump file is loaded, the number of user is {}'.format(len(userList)))

            self.__userList = userList
            for user in self.__userList:
                logging.info('Updating user profile of {}'.format(user))
                self.__userList[user].profileUpdate()

OperatorResult = namedtuple('OperatorResult', 'username operator status message other')

class Transaction(object):

    def __init__(self, user):
        self.__userInstance = user

    def getSign(self):
        response = self.__userInstance.get(Config.GET_SIGN_INFO).json()

        return OperatorResult(self.__userInstance.name, 'GetSign', False, response.get('data').get('text').encode(Config.ENCODING), {
            'curMonth': response.get('data').get('curMonth'),
            'allDays': response.get('data').get('allDays'),
            'hadSignDays': response.get('data').get('hadSignDays')
        })

    def doSign(self):
        response = self.__userInstance.get(Config.LIVE_SIGN_DAILY).json()

        if response.get('code') is 0 and response.get('msg') == 'OK':
            return OperatorResult(self.__userInstance.name, 'Sign', True,response.get('data').get('text').encode(Config.ENCODING), {
                'allDays': response.get('data').get('allDays'),
                'hadSignDays': response.get('data').get('hadSignDays')
            })
        else:
            return OperatorResult(self.__userInstance.name, 'Sign', False, response.get('msg').encode(Config.ENCODING), None)

    def close(self):
        pass