''' BiliBili Live Package
'''

import abc
import struct
import socket
import asyncio
import logging
from collections import namedtuple
from BLiH import Config, Exceptions

RawPackage    = namedtuple('RawPackage', 'pkgLength headerLength version type unknown body')
PackageHeader = namedtuple('PackageHeader', 'pkgLength headerLength version type unknown')
Package       = namedtuple('Package', 'type header body')

async def sendPackage(sock, package, *, loop = asyncio.get_event_loop()):
    loop.sock_sendall(sock, package)

    return True

async def receivePackage(sock, *, rawPackage = False, loop = asyncio.get_event_loop()):
    try:
        buffer = await loop.sock_recv(sock, 4)
        packageLength, = struct.unpack('!I', buffer)
        packageLength -= 4

        while packageLength > 0:
            buffer += await loop.sock_recv(sock, packageLength)
            packageLength -= len(buffer)

        rawPackage = RawPackage(*struct.unpack('!IHHII{}s'.format(len(buffer) - 16), buffer))
        if rawPackage is True:
            return rawPackage
        else:
            return LivePackageParser.factory(rawPackage).package
    except struct.error as e:
        raise Exceptions.FatalException('Receive package error occurs. internal error.')

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
            return { 'PeopleCount': struct.unpack('!I', self.__rawPackage.body)[0] }
        elif self.type == self.PkgTypeAllowJoinLiveRoom:
            return None
        elif self.type == self.PkgTypeDanMuMessage:
            return self.__parseDanMuMessage()
        else:
            return None

    def __parseDanMuMessage(self):
        return self.__rawPackage.body

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
        self.__loop      = loop
        self.__listening = False
        self.__roomID    = None
        self.__uid       = None
        self.__loop.set_debug(True)

        try:
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__sock.connect((self.__DM_SERVER_ADDRESS, self.__DM_SEVER_PORT))
            self.__sock.setblocking(False)
        except Exception as e:
            print('LivePackageGenerator::__init__() error', e)

    async def join(self, roomId, uid):
        self.__roomID = roomId
        self.__uid    = uid

        data    = (self.__JOIN_ROOM_BODY_FORMAT % (roomId, uid)).encode(Config.ENCODING)
        package = self.__packageGenerator(type = self.__PKG_TYPE_JOIN_ROOM, body = data)

        if await sendPackage(self.__sock, package, loop = self.__loop) is True:
            response = await receivePackage(self.__sock, loop = self.__loop)
            print(response)
            if response.type == LivePackageParser.PkgTypeAllowJoinLiveRoom:
                self.__listening = True

                self.__loop.create_task(self.__heartbeat())
                while True:
                    package = await receivePackage(self.__sock, rawPackage = True, loop = self.__loop)
                    print(package)

                return True

    async def __heartbeat(self):
        package = self.__packageGenerator(type = self.__PKG_TYPE_HEARTBEAT)
        while self.__listening is True:
            await asyncio.sleep(Config.LIVE_HEARTBEAT_TIME, loop = self.__loop)
            await sendPackage(self.__sock, package, loop = self.__loop)
            logging.debug('Heartbeat send completed (roomId = {}, uid = {})'.format(self.__roomID, self.__uid))

    def __packageGenerator(self, *, type = 0xFFFFFFFF, body = None):
        if type not in (self.__PKG_TYPE_HEARTBEAT, self.__PKG_TYPE_JOIN_ROOM):
            pass

        if isinstance(body, str):
            body = body.encode(Config.ENCODING)
        if body is not None and not isinstance(body, bytes):
            raise TypeError('LivePackageGenerator::___makePackage params error')

        return self.___createPackage(type = type, body = body)

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
    def onAllowJoin(self, package):
        pass

    @abc.abstractclassmethod
    def onHeartbeatResponse(self, package):
        pass

    @abc.abstractclassmethod
    def onDanMuMessage(self, package):
        pass

    @abc.abstractclassmethod
    def onDanMu(self):
        pass

if __name__ == '__main__':
    from BLiH import Utils
    loop = asyncio.get_event_loop()
    # loop.set_exception_handler(lambda loop,e: print(loop, e))
    generator = LivePackageGenerator(loop = loop)
    loop.run_until_complete(asyncio.wait([ generator.join(98284, Utils.liveAnonymousUID()) ]))