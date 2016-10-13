'''BiliBili Helper

'''

import requests, logging, sys, time, os
import asyncio
import pickle
from . import Exceptions, Storage, Config, TerminalQr, User

class Helper(object):

    def __init__(self, **kwargs):
        self.__oauthKey           = None
        self.__accountInformation = {}
        self.__userInformation    = {}
        self.__userPool           = {}
        self.__sessionObject      = requests.Session()
        self.__outFile            = sys.stdout

        if kwargs.get('session', None) is True:
            if self.__loadSession() == False:
                if 'QRLogin' in kwargs:
                    self.QRLogin()
                elif ('username' in kwargs) and ('password' in kwargs):
                    self.login(**kwargs)

        print(self.__userPool)

    def login(self, username, password):
        self.__initSession(username = username, password = password)

    def QRLogin(self):
        self.__initSession(QRLogin = True)

    def bullet(self, videoId, message):
        pass

    def listen(self, liveId):
        pass

    def __initSession(self, *, QRLogin = False, username = None, password = None):
        logging.info('Create a New Session...')
        self.__sessionObject.get(Config.INIT_COOKIES_START, stream = True).close()

        self.__getOAuthKey()

        if QRLogin is not True:
            logging.info('Authentication of Identity... <' + username + ':*@bilibili.com>')
        else:
            logging.info('Authentication of Identity... <QR Login>')
            with TerminalQr.create(Config.QrLoginUrl(self.__oauthKey)) as qc:
                print(qc, file = self.__outFile)

        # poll server check login status
        self.__checkLoginInfo()

        user = User.User(self.__sessionObject.cookies, oauthKey = self.__oauthKey)
        self.__userPool[user.name] = user

        self.__saveSession()

    def __getOAuthKey(self):
        logging.info('From BiliBili Getting OAUTH Key...')
        response = self.__sessionObject.get(Config.GET_OAUTH_KEY).json()
        self.__oauthKey = response.get('data').get('oauthKey')
        logging.info('OAUTH Key Getting Completed... <' + self.__oauthKey + '>')

        return self.__oauthKey

    def __checkLoginInfo(self):
        for reLoginCount in range(0, Config.RE_LOGIN_COUNT, Config.DETECT_LOGIN_STATUS_INTERVAL):
            info = None
            for sec in range(Config.QR_EXPIRED_TIME):
                info = self.__sessionObject.post(Config.LOGIN_INFO_URL, data={'oauthKey': self.__oauthKey}).json()

                if info.get('status', None) is True:
                    break
                else:
                    time.sleep(Config.DETECT_LOGIN_STATUS_INTERVAL)
            else:
                logging.info('QrCode Expired! Refresh QrCode ...')

                with TerminalQr.create(Config.QrLoginUrl(self.__getOAuthKey())) as qc:
                    print(qc, file=self.__outFile)

            if info.get('status', None) is True:
                if 'data' in info and 'url' in info['data']:
                    try:
                        # self.__sessionObject.get(info['data']['url']).close()
                        pass
                    except requests.exceptions.ConnectionError as e:
                        print(e)
                break
        else:
            self.__exit(logging.error, 'The number of retries exceeds the limit.')

    def __saveSession(self):
        session = {}
        for user in self.__userPool:
            session[user] = self.__userPool[user].cookieJar

        Storage.dump('session.pkl', session)

    def __loadSession(self):
        if os.path.isfile('session.pkl') == False:
            return False

        logging.info('Session file detected, using a saved session')
        with Storage.load('session.pkl') as session:
            for user in session:
                if user not in self.__userPool:
                    self.__userPool[user] = User.User(session[user])

    def __exit(self, handler, message):
        handler(message)
        exit()