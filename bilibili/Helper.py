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

def bliHelper(qr = True, *, storage = True, account = None, log = logging.INFO, log_file = None, log_redirection = None,
              manual_login = False, multi_user = False, auto_dump = True, loop = None):
    if log not in [ logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL, logging.DEBUG ]:
        log = logging.INFO
    logging.basicConfig(level = log,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%d %b %Y %H:%M:%S')

    if loop is None:
        loop = asyncio.get_event_loop()

    helper = Helper(storage = storage, loop = loop)
    if helper.accountSize() != 0 or manual_login is True:
        if multi_user is True or multi_user is False:
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
    elif isinstance(multi_user, int):
        account = []
        multi_user = multi_user - helper.accountSize()
        if multi_user < 0:
            return helper
        else:
            for user_index in range(multi_user):
                account.append(Account(None, None, None))
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

    def __init__(self, *, storage = True, loop = None):
        self.__user_list = {}

        self.__async_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.__async_loop)
        self.__async_loop.run_until_complete(self.__load_session_file())
        if loop is not None:
            self.__async_loop = loop
            asyncio.set_event_loop(self.__async_loop)

    @classmethod
    def change_session_file_name(cls, file_name):
        if not isinstance(file_name, str):
            raise TypeError('file_name must be str type')
        cls.__session_file_name = file_name

    @classmethod
    def get_session_file_name(cls):
        return cls.__session_file_name

    def login(self, qr = True, *, username = None, password = None, storage = True, alias = None, print_handle = None):
        if username is not None and password is not None:
            user = User(username = username, password = password, loop = self.__async_loop)
        elif qr is True:
            if print_handle is None:
                print_handle = print
            user = User(qr = True, print_handle = print_handle, loop = self.__async_loop)
        else:
            raise Exceptions.FatalException('login parameters are incorrect, type not specified')

        self.__user_list[alias if alias is not None and isinstance(alias, str) else user.name] = user
        logging.info('%s Login success' % ( user ))

    async def async_foreach(self, handler):
        if callable(handler) and asyncio.iscoroutine(handler):
            raise TypeError('handler must be callable and coroutine')
        for user in self.__user_list:
            self.__async_loop.create_task(
                handler(user_instance = self.__user_list[user], helper = self, loop = self.__async_loop)
            )

    def async_startup(self, *task):
        if len(task) == 1 and isinstance(task[0], list):
            logging.warning('task is a single list')
            task = task[0]
        self.__async_loop.run_until_complete(asyncio.gather(*task))

        while asyncio.Task.all_tasks(): # pending
            self.__async_loop.run_until_complete(asyncio.gather(*asyncio.Task.all_tasks()))

    def dump(self):
        self.__dump_user_list()

    def accountSize(self):
        return len(self.__user_list)

    def is_exists(self, name):
        return name in self.__user_list

    def accounts(self):
        return list(self.__user_list.keys())

    def select(self, name):
        if self.is_exists(name):
            return Transaction(self.__user_list[name], loop = self.__async_loop)

    def get_user(self, name = None, index = None):
        if name is not None and self.is_exists(name):
            return self.__user_list[name]
        if index is not None and index < len(self.__user_list):
            return self.__user_list[self.accounts()[index]]

    def __dump_user_list(self):
        pickle_data = {}
        for user in self.__user_list:
            pickle_data[self.__user_list[user].name] = self.__user_list[user].cookie_jar._cookies
        Storage.dump(self.__session_file_name, pickle_data)

    async def __load_session_file(self):
        if os.path.isfile(self.__session_file_name) is False:
            return False

        if os.path.getsize(self.__session_file_name) == 0:
            logging.warning('the session file is empty')
            os.remove(self.__session_file_name)
            return

        logging.info('Dump file detected, using saved session')
        with Storage.load(self.__session_file_name) as cookies_list:
            logging.info('Dump file is loaded, the number of user is {}'.format(len(cookies_list)))

            self.__user_list = {}
            for user in cookies_list:
                logging.info('Updating user profile of {}'.format(user))
                self.__user_list[user] = User(loop = self.__async_loop, cookies = cookies_list[user])
                logging.info('{} profile updated'.format(user))
