'''BiliBili Helper

'''

import requests, logging
from . import Exception, Storage, Config

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
        self.__sessionObject.get(Config.START_URL)

        logging.info('From BiliBili Getting OAUTH Key...')
        response = self.__sessionObject.get(Config.OAUTH_KEY_URL).json()
        logging.info('OAUTH Key Getting Completed... <' + response.get('data').get('oauthKey') + '>')

        if QRLogin is not True:
            logging.info('Authentication of Identity... <' + username + '>')
        else:
            logging.info('Authentication of Identity... <QR Login>')