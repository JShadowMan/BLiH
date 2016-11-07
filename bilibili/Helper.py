#!/usr/bin/env python
#
# Copyright (C) 2016 ShadowMan
#
# bilibili.Helper
# This module is all toolkit startup

import os
import logging
import asyncio
from collections import namedtuple
from bilibili import Exceptions, Storage, Config, TerminalQr
from bilibili.User import User, Account
from bilibili.Transaction import Transaction

def bliHelper(qr = True, *, storage = True, account = None, log = logging.INFO, log_file = None,
              manual_login = False, multi_user = False, auto_dump = True):
    if log in [ logging.NOTSET, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL ]:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(levelname)-8s %(message)s',
                            datefmt='%d %b %Y %H:%M:%S')

    helper = Helper(storage = storage)
    if helper.accountSize() != 0 and manual_login is False:
        return helper

    if multi_user is False:
        if isinstance(account, Account):
            account = [account]
        elif account is None:
            account = [ Account(None, None, None) ]
        else:
            raise TypeError('multi_user and account, parameter conflicts')
        multi_user = 1
    elif multi_user is True and isinstance(account, list):
        account = list(filter(lambda x: isinstance(x, Account), account))
        multi_user = len(account)
    else:
        raise TypeError('multi_user and account, parameter conflicts')

    for index in range(min(multi_user, Config.MAX_USER_COUNT)):
        username, password, key = account[index]

        if (username is not None) and (password is not None):
            helper.login(username = username, password = password)
        elif qr is True:
            helper.login(qr = True)
        else:
            if helper.accountSize() is 0:
                raise Exceptions.FatalException('Params error')

    if auto_dump is True:
        helper.dump()

    return helper

class Helper(object):
    __session_file_name = 'bli_session.pkl'

    LoopInstance = asyncio.get_event_loop()

    def __init__(self, *, storage = True, loop = None):
        self.__user_list = {}

        if loop is None:
            self.__loop_instance = asyncio.get_event_loop()
        else:
            self.__loop = loop

        if storage is True:
            self.__load_session_file()

    def login(self, qr = True, *, username = None, password = None, storage = True, alias = None):
        if username is not None and password is not None:
            user = User(username = username, password = password)
        elif qr is True:
            user = User(qr = True)
        else:
            raise Exceptions.FatalException('login parameters are incorrect, type not specified')

        self.__user_list[alias if alias is not None and isinstance(alias, str) else user.name] = user
        logging.info('%s Login success' % ( user ))

    def dump(self):
        self.__dump_user_list()

    def accountSize(self):
        return len(self.__user_list)

    def isExists(self, name):
        return name in self.__user_list

    def accounts(self):
        return list(self.__user_list.keys())

    def select(self, name):
        if self.isExists(name):
            return Transaction(self.__user_list[name])

    def __dump_user_list(self):
        Storage.dump(self.__session_file_name, self.__user_list)

    def __load_session_file(self):
        if os.path.isfile(self.__session_file_name) is False:
            return False

        logging.info('dump file detected, using saved session')
        with Storage.load(self.__session_file_name) as user_list:
            logging.info('Dump file is loaded, the number of user is {}'.format(len(user_list)))

            self.__user_list = user_list
            for user in self.__user_list:
                logging.info('Updating user profile of {}'.format(user))
                self.__user_list[user].update_profile()
