#!/usr/bin/env python3
#
# Copyright (C) 2018 Jayson
#
import json
import struct
import websocket
from bilibili import server


class BlLive(object):

    def __init__(self, room_id: int):
        self.room_id = room_id
        self.server = server.BlServer(self.room_id)
        self.ws = websocket.WebSocket()

    def watch(self):
        self.ws.connect(self.server.get_random_wss_server())
        self.ws.


if __name__ == '__main__':
    live = BlLive(6)
    live.watch()
