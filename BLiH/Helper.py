'''BiliBili Helper

'''

import requests, logging
from . import Exception, Storage, Config, TerminalQr

class Helper(object):

    def __init__(self, **kwargs):
        self.__accountInformation = {}
        self.__userInformation    = {}
        self.__sessionObject      = requests.Session()

        if ('username' in kwargs) and ('password' in kwargs):
            self.login(**kwargs)

        if 'QRLogin' in kwargs:
            self.QRLogin()

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
        self.__sessionObject.get(Config.START_URL, stream = True).close()

        logging.info('From BiliBili Getting OAUTH Key...')
        response = self.__sessionObject.get(Config.OAUTH_KEY_URL).json()
        self.__OAuthKey = response.get('data').get('oauthKey')
        logging.info('OAUTH Key Getting Completed... <' + self.__OAuthKey + '>')

        if QRLogin is not True:
            logging.info('Authentication of Identity... <' + username + ':*@bilibili.com>')
        else:
            logging.info('Authentication of Identity... <QR Login>')
            with TerminalQr.create(Config.QR_LOGIN_URL % self.__OAuthKey) as qc:
                print(qc)

        input()
        response = self.__sessionObject.get('https://account.bilibili.com/site/setting')
        print(response.text)
