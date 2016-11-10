''' BiliBili Live Package
'''

import abc
import json
import struct
import socket
import asyncio
import logging
from collections import namedtuple
from bilibili import Config, Exceptions

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

    __single_instance = None

    def __init__(self, room_id, raw_package = None):
        if raw_package is None:
            return

        if not isinstance(raw_package, RawPackage):
            raise Exceptions.FatalException('Internal error occurs, raw_package not allow')

        self.__room_id = room_id
        self.__raw_package = raw_package

    def parse(self, raw_package, room_id, other_data):
        if not isinstance(raw_package, RawPackage):
            raise Exceptions.FatalException('Internal error occurs, raw_package not allow')

        self.__room_id = room_id
        self.__raw_package = raw_package
        self.__other_data = {}

    @classmethod
    def factory(cls, raw_package, room_id, other_data = None):
        if cls.__single_instance is None:
            cls.__single_instance = LivePackageParser(None)
        if other_data is None:
            other_data = {}

        cls.__single_instance.parse(raw_package, room_id, other_data)
        return cls.__single_instance

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
        if self.__raw_package.type == 0x02:
            return self.PkgTypeHeartbeat
        elif self.__raw_package.type == 0x03:
            return self.PkgTypeHeartbeatResponse
        elif self.__raw_package.type == 0x05:
            return self.PkgTypeDanMuMessage
        elif self.__raw_package.type == 0x07:
            return self.PkgTypeJoinLiveRoom
        elif self.__raw_package.type == 0x08:
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
            self.__raw_package.pkgLength,
            self.__raw_package.headerLength,
            self.__raw_package.version,
            self.__raw_package.type,
            self.__raw_package.unknown
        )

    @property
    def body(self):
        if self.type == self.PkgTypeHeartbeatResponse:
            HeartbeatResponse = namedtuple('HeartbeatResponse', 'peopleCount')
            return HeartbeatResponse(struct.unpack('!I', self.__raw_package.body)[0])
        elif self.type == self.PkgTypeAllowJoinLiveRoom:
            return None
        elif self.type == self.PkgTypeDanMuMessage:
            return self.__parse_dan_mu_message()
        else:
            return None

    def __parse_dan_mu_message(self):
        contents = self.__raw_package.body.decode('utf-8')
        try:
            contents = json.loads(contents)
        except json.decoder.JSONDecodeError:
            logging.debug('Parse DanMu message error occurs.', self.__raw_package)

        if contents.get('cmd') == 'DANMU_MSG':
            return self.___parse_dan_mu_message(contents)
        elif contents.get('cmd') == 'WELCOME':
            return self.___parse_welcome_message(contents)
        elif contents.get('cmd') == 'SEND_GIFT':
            return self.___parse_send_gift_message(contents)
        else:
            return contents

    def ___parse_dan_mu_message(self, contents):
        Message = namedtuple('Message', 'name message other')

        return Message(contents.get('info', {})[2][1], contents.get('info', {})[1], dict({
            'roomId': self.__room_id
        }, **self.__other_data))

    def ___parse_welcome_message(self, contents):
        Welcome = namedtuple('Welcome', 'uid name vip admin other')

        return Welcome(contents.get('data', {}).get('uid', None), contents.get('data', {}).get('uname', None),
                       True if contents.get('data', {}).get('vip', None) == 1 else False,
                       True if contents.get('data', {}).get('isadmin', None) == 1 else False, dict({
            'roomId': contents.get('roomid', None)
        }, **self.__other_data))

    def ___parse_send_gift_message(self, contents):
        Gift = namedtuple('Gift', 'uid name gift count time other')

        return Gift(contents.get('data', {}).get('uid', None), contents.get('data', {}).get('uname', None),
                    contents.get('data', {}).get('giftName', None), contents.get('data', {}).get('num', None),
                    contents.get('data', {}).get('timestamp', None), dict({
            'roomId': contents.get('roomid', None)
            # top list
        }, **self.__other_data))

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
    __join_live_room_request_body = '{ "roomid": %s, "uid": %s }'

    # DanMu Server Address
    __DM_SERVER_ADDRESS = 'dm.live.bilibili.com'

    # DanMu Server Port
    __DM_SEVER_PORT = 788

    def __init__(self, extra_data = None, *, loop = asyncio.get_event_loop()):
        self.__uid = None
        self.__loop = loop
        self.__listening = False
        self.__extra_data = extra_data if isinstance(extra_data, dict) else {}
        self.__live_room_id = None
        self.__package_handler = None

        try:
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__sock.connect((self.__DM_SERVER_ADDRESS, self.__DM_SEVER_PORT))
            self.__sock.setblocking(False)
        except Exception as e:
            print('LivePackageGenerator::__init__() error', e)

    async def join(self, live_room_id, uid, package_handler):
        if isinstance(live_room_id, int) and isinstance(uid, int):
            self.__uid = uid
            self.__live_room_id = live_room_id
        else:
            raise TypeError('live_room_id and uid muse be int type')

        if callable(package_handler):
            handler = package_handler()

            if isinstance(handler, PackageHandlerProtocol):
                self.__package_handler = handler
            else:
                raise TypeError('package_handler must base for PackageHandlerProtocol')
        else:
            raise TypeError('package_handler must be callable')

        data = (self.__join_live_room_request_body % (live_room_id, uid)).encode(Config.ENCODING)
        package = self.__package_generator(type = self.__PKG_TYPE_JOIN_ROOM, body = data)

        if await self.__send_package(package) is True:
            response = await self.__receive_package()

            if response.type == LivePackageParser.PkgTypeAllowJoinLiveRoom and self.__package_handler.on_allow_join():
                self.__listening = True

                self.__loop.create_task(self.__heartbeat())
                while self.__listening is True:
                    package = await self.__receive_package()

                    if package.type == LivePackageParser.PkgTypeHeartbeatResponse:
                        self.__package_handler.on_heartbeat_response(package.body)
                    elif package.type == LivePackageParser.PkgTypeDanMuMessage:
                        messageType = package.body.__class__.__name__
                        if messageType == 'Message':
                            self.__package_handler.on_dan_mu_message(package.body)
                        elif messageType == 'Gift':
                            self.__package_handler.on_gift_message(package.body)
                        elif messageType == 'Welcome':
                            self.__package_handler.on_welcome_message(package.body)

    async def __heartbeat(self):
        package = self.__package_generator(type = self.__PKG_TYPE_HEARTBEAT)
        while self.__listening is True:
            await asyncio.sleep(Config.LIVE_HEARTBEAT_TIME, loop = self.__loop)
            await self.__send_package(package)
            logging.debug('Heartbeat send completed (roomId = {}, uid = {})'.format(self.__live_room_id, self.__uid))

    def __package_generator(self, *, type = 0xFFFFFFFF, body = None):
        if type not in (self.__PKG_TYPE_HEARTBEAT, self.__PKG_TYPE_JOIN_ROOM):
            raise Exceptions.FatalException('error occurs with internal error')

        if isinstance(body, str):
            body = body.encode(Config.ENCODING)
        if body is not None and not isinstance(body, bytes):
            raise TypeError('LivePackageGenerator::___makePackage params error')

        return self.___create_package(type = type, body = body)

    async def __send_package(self, package):
        await self.__loop.sock_sendall(self.__sock, package)
        return True

    async def __receive_package(self, *, need_raw_package = False):
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

            raw_package = RawPackage(*struct.unpack('!IHHII{}s'.format(len(buffer) - 16), buffer))
            if need_raw_package is True:
                return raw_package
            else:
                return LivePackageParser.factory(raw_package, self.__live_room_id, self.__extra_data).package
        except struct.error as e:
            raise Exceptions.FatalException('Receive package error occurs. internal error.', e)
        except ConnectionAbortedError as e:
            logging.debug('Package::__receive_package error', e)

    def ___create_package(self, *, package_length = 0, header_length = __PKG_HEADER_LENGTH,
                          version = __PKG_API_VERSION, type = 0, unknown = __UNKNOWN_FIELD_VALUE, body = None):
        if isinstance(body, str):
            body = body.encode(Config.ENCODING)

        if body is not None and not isinstance(body, bytes):
            raise TypeError('LivePackageGenerator::___makePackage params error')

        package_length = header_length + len(body) if body is not None else 0

        try:
            if body is None:
                return struct.pack('!IHHII', package_length, header_length, version, type, unknown)
            return struct.pack('!IHHII{}s'.format(len(body)), package_length, header_length, version, type, unknown, body)
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
    def on_allow_join(self):
        return True

    @abc.abstractclassmethod
    def on_heartbeat_response(self, contents):
        pass

    @abc.abstractclassmethod
    def on_dan_mu_message(self, contents):
        pass

    @abc.abstractclassmethod
    def on_gift_message(self, contents):
        pass

    @abc.abstractclassmethod
    def on_welcome_message(self, contents):
        pass

    @abc.abstractclassmethod
    def on_error_occurs(self, package):
        pass
