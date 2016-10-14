''' Live.BiliBili Helper

'''

import struct
import re
import requests
import asyncio
import random
from BLiH import Config

# Package Type Value
PKG_TYPE_JOIN_ROOM = 7

# Package Type Value
PKG_TYPE_HEARTBEAT = 2

class LiveBiliBili(object):
    ''' __PKG_HEADER_LENGTH
            Int(4) + Short(2) + Short(2) + Int(4) + Int(4) + Int(4) = 16
        '''
    __PKG_HEADER_LENGTH = 16

    ''' __PKG_API_VERSION
        API Defined
    '''
    __PKG_API_VERSION = 1

    ''' __UNKNOWN_FIELD_VALUE
        API Defined
    '''
    __UNKNOWN_FIELD_VALUE = 1

    '''

    '''
    __JOIN_ROOM_BODY_FORMAT = '{ "roomid": %s, "uid": %s }'

    def __init__(self):
        pass

    async def heartbeat(self):
        pass

    def joinRoom(self, roomId):
        package = self.makePackage(body = self.__joinRoomBody(roomId, self.__makeUID()))
        print(package)

    def makePackage(self, *, type = PKG_TYPE_JOIN_ROOM, body = None):
        if isinstance(body, (str, bytes)):
            if isinstance(body, str):
                body = body.encode(Config.ENCODING)
        else:
            if body is not None:
                raise TypeError('Package Body must be str or bytes')

        package = self.__makePackage(
            pkgLength    = self.__PKG_HEADER_LENGTH + len(body) if body is not None else 0,
            headerLength = self.__PKG_HEADER_LENGTH,
            version      = self.__PKG_API_VERSION,
            type         = type,
            unknown      = self.__UNKNOWN_FIELD_VALUE,
            body         = body
        )

        print(package)

    async def listen(self):
        pass

    def __makePackage(self, *, pkgLength = 0, headerLength = 16, version = 1, type = 0, unknown = 1, body = None):
        try:
            if body is None:
                return struct.pack('!IHHII', pkgLength, headerLength, version, type, unknown)
            return struct.pack('!IHHII{}s'.format(len(body)), pkgLength, headerLength, version, type, unknown, body)
        except Exception as e:
            pass

    def __makeUID(self):
        return int(100000000000000 + (200000000000000 * random.random()))

    def __joinRoomBody(self, roomId, uid):
        return (self.__JOIN_ROOM_BODY_FORMAT % (roomId, uid)).encode(Config.ENCODING)

if __name__ == '__main__':
    live = LiveBiliBili()
    live.joinRoom(83264)




















