#!/usr/bin/env python3
#
# Copyright (C) 2018 Jayson
#
import random
import requests


class BlServer(object):

    def __init__(self, room_id):
        self.room_id = room_id
        self.servers = {}

    def get_wss_servers(self) -> list:
        self._init_servers()

        servers = self.servers.setdefault('host_server_list', [])
        return ['wss://{}:{}'.format(s['host'], s['wss_port']) for s in servers]

    def get_random_wss_server(self) -> str:
        return random.choice(self.get_wss_servers())

    def _init_servers(self):
        if self.servers:
            return

        response = requests.get('https://api.live.bilibili.com/room/v1/Danmu/getConf', {
            'room_id': self.room_id,
            'platform': 'pc',
            'player': 'web'
        })
        self.servers = response.json().setdefault('data', {})


if __name__ == '__main__':
    server = BlServer(519)
    print('wss servers:', server.get_wss_servers())
    print('wss server:', server.get_random_wss_server())
