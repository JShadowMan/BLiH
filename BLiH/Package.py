''' BiliBili Live Package
'''

import abc
import json
import struct
import socket
import asyncio
import logging
from collections import namedtuple
from BLiH import Config, Exceptions

RawPackage    = namedtuple('RawPackage', 'pkgLength headerLength version type unknown body')
PackageHeader = namedtuple('PackageHeader', 'pkgLength headerLength version type unknown')
Package       = namedtuple('Package', 'type header body')

''' Response Format

    packageLength Int(4)
    headerLength  Short(2)
    version       Short(2)
    package type  Int(4)
    unknown       Int(4)
    json data     0+
'''

class LivePackageParser(object):

    __SingleInstance = None

    def __init__(self, rawPackage = None):
        if rawPackage is None:
            return

        if not isinstance(rawPackage, RawPackage):
            raise Exceptions.FatalException('Internal error occurs, rawPackage not allow')

        self.__rawPackage = rawPackage

    def parse(self, rawPackage):
        if not isinstance(rawPackage, RawPackage):
            raise Exceptions.FatalException('Internal error occurs, rawPackage not allow')

        self.__rawPackage = rawPackage

    @classmethod
    def factory(cls, rawPackage):
        if cls.__SingleInstance is None:
            cls.__SingleInstance = LivePackageParser(None)

        cls.__SingleInstance.parse(rawPackage)
        return cls.__SingleInstance

    @property
    def type(self):
        ''' Package Type

              value             description         direction                note
               02                Heartbeat             send                30s per time
               03           Heartbeat-response        receive      number of people who watch live, Int(4)
               05              DanMu Message          receive            dan-mu information
               07               Join Live              send              join the live room
               08               Allow Join            receive          allow join thee live room
        '''
        if self.__rawPackage.type == 0x02:
            return self.PkgTypeHeartbeat
        elif self.__rawPackage.type == 0x03:
            return self.PkgTypeHeartbeatResponse
        elif self.__rawPackage.type == 0x05:
            return self.PkgTypeDanMuMessage
        elif self.__rawPackage.type == 0x07:
            return self.PkgTypeJoinLiveRoom
        elif self.__rawPackage.type == 0x08:
            return self.PkgTypeAllowJoinLiveRoom
        else:
            return self.PackageType(0xFFFFFFFF, 'Error')

    # Package Type Define
    PackageType = namedtuple('PackageType', 'value toString')

    PkgTypeHeartbeat         = PackageType(0x00000002, 'Heartbeat')
    PkgTypeHeartbeatResponse = PackageType(0x00000003, 'Heartbeat Response')
    PkgTypeDanMuMessage      = PackageType(0x00000005, 'Dan-Mu Message')
    PkgTypeJoinLiveRoom      = PackageType(0x00000007, 'Join Live Room')
    PkgTypeAllowJoinLiveRoom = PackageType(0x00000007, 'Allow Join')

    @property
    def header(self):
        return PackageHeader(
            self.__rawPackage.pkgLength,
            self.__rawPackage.headerLength,
            self.__rawPackage.version,
            self.__rawPackage.type,
            self.__rawPackage.unknown
        )

    @property
    def body(self):
        if self.type == self.PkgTypeHeartbeatResponse:
            HeartbeatResponse = namedtuple('HeartbeatResponse', 'peopleCount')
            return HeartbeatResponse(struct.unpack('!I', self.__rawPackage.body)[0])
        elif self.type == self.PkgTypeAllowJoinLiveRoom:
            return None
        elif self.type == self.PkgTypeDanMuMessage:
            return self.__parseDanMuMessage()
        else:
            return None

    def __parseDanMuMessage(self):
        contents = self.__rawPackage.body.decode('utf-8')
        try:
            contents = json.loads(contents)
        except json.decoder.JSONDecodeError:
            logging.debug('Parse DanMu message error occurs.', self.__rawPackage)

        if contents.get('cmd') == 'DANMU_MSG':
            return self.___parseDanMuMessage(contents)
        elif contents.get('cmd') == 'WELCOME':
            return self.___parseWelcome(contents)
        elif contents.get('cmd') == 'SEND_GIFT':
            return self.___parseSendGift(contents)
        else:
            return contents

    def ___parseDanMuMessage(self, contents):
        Message = namedtuple('Message', 'name message other')

        return Message(contents.get('info', {})[2][1], contents.get('info', {})[1], {
            # ...
        })

    def ___parseWelcome(self, contents):
        Welcome = namedtuple('Welcome', 'uid name vip admin other')

        return Welcome(contents.get('data', {}).get('uid', None), contents.get('data', {}).get('uname', None),
                       True if contents.get('data', {}).get('vip', None) == 1 else False,
                       True if contents.get('data', {}).get('isadmin', None) == 1 else False, {
            'roomId': contents.get('roomid', None)
        })

    def ___parseSendGift(self, contents):
        Gift = namedtuple('Gift', 'uid name gift count time other')

        return Gift(contents.get('data', {}).get('uid', None), contents.get('data', {}).get('uname', None),
                    contents.get('data', {}).get('giftName', None), contents.get('data', {}).get('num', None),
                    contents.get('data', {}).get('timestamp', None), {
            'roomId': contents.get('roomid', None)
            # top list
        })

    @property
    def package(self):
        return Package(
            self.type,
            self.header,
            self.body
        )


class LivePackageGenerator(object):

    # Package Type Value
    __PKG_TYPE_JOIN_ROOM = 7

    # Package Type Value
    __PKG_TYPE_HEARTBEAT = 2

    # Package Header Length = Int(4) + Short(2) + Short(2) + Int(4) + Int(4) + Int(4) = 16
    __PKG_HEADER_LENGTH = 16

    # Package API Version
    __PKG_API_VERSION = 1

    # Unknown Field, Pad Field
    __UNKNOWN_FIELD_VALUE = 1

    # Join Room Package Body Format
    __JOIN_ROOM_BODY_FORMAT = '{ "roomid": %s, "uid": %s }'

    # DanMu Server Address
    __DM_SERVER_ADDRESS = 'dm.live.bilibili.com'

    # DanMu Server Port
    __DM_SEVER_PORT = 788

    def __init__(self, *, loop = asyncio.get_event_loop()):
        self.__loop           = loop
        self.__listening      = False
        self.__roomID         = None
        self.__uid            = None
        self.__packageHandler = None
        self.__loop.set_debug(True)

        try:
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__sock.connect((self.__DM_SERVER_ADDRESS, self.__DM_SEVER_PORT))
            self.__sock.setblocking(False)
        except Exception as e:
            print('LivePackageGenerator::__init__() error', e)

    async def join(self, roomId, uid, packageHandler):
        self.__roomID = roomId
        self.__uid    = uid

        if callable(packageHandler):
            handler = packageHandler()

            if isinstance(handler, PackageHandlerProtocol):
                self.__packageHandler = handler
            else:
                raise TypeError('packageHandler must be callable')
        else:
            raise TypeError('packageHandler must be callable')

        data    = (self.__JOIN_ROOM_BODY_FORMAT % (roomId, uid)).encode(Config.ENCODING)
        package = self.__packageGenerator(type = self.__PKG_TYPE_JOIN_ROOM, body = data)

        if await self.__sendPackage(package) is True:
            response = await self.__receivePackage()

            if response.type == LivePackageParser.PkgTypeAllowJoinLiveRoom and self.__packageHandler.onAllowJoin():
                self.__listening = True

                self.__loop.create_task(self.__heartbeat())
                while self.__listening is True:
                    package = await self.__receivePackage()

                    if package.type == LivePackageParser.PkgTypeHeartbeatResponse:
                        self.__packageHandler.onHeartbeatResponse(package.body)
                    elif package.type == LivePackageParser.PkgTypeDanMuMessage:
                        messageType = package.body.__class__.__name__
                        if messageType == 'Message':
                            self.__packageHandler.onDanMuMessage(package.body)
                        elif messageType == 'Gift':
                            self.__packageHandler.onGift(package.body)
                        elif messageType == 'Welcome':
                            self.__packageHandler.onWelcome(package.body)

    async def __heartbeat(self):
        package = self.__packageGenerator(type = self.__PKG_TYPE_HEARTBEAT)
        while self.__listening is True:
            await asyncio.sleep(Config.LIVE_HEARTBEAT_TIME, loop = self.__loop)
            await self.__sendPackage(package)
            logging.debug('Heartbeat send completed (roomId = {}, uid = {})'.format(self.__roomID, self.__uid))

    def __packageGenerator(self, *, type = 0xFFFFFFFF, body = None):
        if type not in (self.__PKG_TYPE_HEARTBEAT, self.__PKG_TYPE_JOIN_ROOM):
            pass

        if isinstance(body, str):
            body = body.encode(Config.ENCODING)
        if body is not None and not isinstance(body, bytes):
            raise TypeError('LivePackageGenerator::___makePackage params error')

        return self.___createPackage(type = type, body = body)

    async def __sendPackage(self, package):
        await self.__loop.sock_sendall(self.__sock, package)

        return True

    async def __receivePackage(self, *, rawPackage = False):
        try:
            buffer = b''
            while len(buffer) < 4:
                buffer += await self.__loop.sock_recv(self.__sock, 4)
            packageLength, = struct.unpack('!I', buffer)
            packageLength -= 4

            while packageLength > 0:
                temp = await self.__loop.sock_recv(self.__sock, packageLength)
                packageLength -= len(temp)
                buffer += temp

            rawPackage = RawPackage(*struct.unpack('!IHHII{}s'.format(len(buffer) - 16), buffer))
            if rawPackage is True:
                return rawPackage
            else:
                return LivePackageParser.factory(rawPackage).package
        except struct.error as e:
            raise Exceptions.FatalException('Receive package error occurs. internal error.')
        except ConnectionAbortedError as e:
            print('[EXCEPTION] FUCK', e)

    def ___createPackage(self, *, pkgLength = 0, headerLength = __PKG_HEADER_LENGTH,
                         version = __PKG_API_VERSION, type = 0, unknown = __UNKNOWN_FIELD_VALUE, body = None):
        if isinstance(body, str):
            body = body.encode(Config.ENCODING)

        if body is not None and not isinstance(body, bytes):
            raise TypeError('LivePackageGenerator::___makePackage params error')

        pkgLength = headerLength + len(body) if body is not None else 0

        try:
            if body is None:
                return struct.pack('!IHHII', pkgLength, headerLength, version, type, unknown)
            return struct.pack('!IHHII{}s'.format(len(body)), pkgLength, headerLength, version, type, unknown, body)
        except Exception as e:
            pass

    @classmethod
    def getDanMuServerAddress(cls):
        return cls.__DM_SERVER_ADDRESS

    @classmethod
    def getDanMuServerPort(cls):
        return cls.__DM_SEVER_PORT

class PackageHandlerProtocol(object, metaclass = abc.ABCMeta):

    def __init__(self):
        pass

    @abc.abstractclassmethod
    def onAllowJoin(self):
        return True

    @abc.abstractclassmethod
    def onHeartbeatResponse(self, contents):
        pass

    @abc.abstractclassmethod
    def onDanMuMessage(self, contents):
        pass

    @abc.abstractclassmethod
    def onGift(self, contents):
        pass

    @abc.abstractclassmethod
    def onWelcome(self, contents):
        pass

    @abc.abstractclassmethod
    def onError(self, package):
        pass

if __name__ == '__main__':
    from BLiH import Utils

    class MessageHandler(PackageHandlerProtocol):

        def onAllowJoin(self):
            print('Join Live Room Completed')

            return True

        def onDanMuMessage(self, contents):
            print('{} Say: {}'.format(contents.name, contents.message))

        def onGift(self, contents):
            print('{} sent out {} {}'.format(contents.name, contents.count, contents.gift))

        def onHeartbeatResponse(self, contents):
            print('Live Room People Count: {}'.format(contents.peopleCount))

        def onWelcome(self, contents):
            print('Welcome {}'.format(contents.name))

        def onError(self, package):
            print('Error occurs', package)

    loop = asyncio.get_event_loop()
    # loop.set_exception_handler(lambda loop,e: print(loop, e))
    generator = LivePackageGenerator(loop = loop)
    loop.run_until_complete(generator.join(1017, Utils.liveAnonymousUID(), lambda : MessageHandler()))