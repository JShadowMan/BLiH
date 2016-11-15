#!/usr/bin/env python
#
# Copyright (C) 2016 ShadowMan
#
import asyncio
import logging
from collections import namedtuple
from bilibili import Config, User, Exceptions, Utils

OperatorResult = namedtuple('OperatorResult', 'username operator status message other')

class Transaction(object):

    def __init__(self, user, loop = None):
        if isinstance(user, User.User):
            self.__user_instance = user

            self.__own_live_profile = None
        else:
            raise TypeError('user is not User type')

        if loop is None:
            self.__loop = asyncio.get_event_loop()
        else:
            self.__loop = loop

    def get_sign_info(self):
        response = self.http_get(Config.GET_SIGN_INFO).json()
        response = response.get('data', {})

        return OperatorResult(
            # username operator status message other
            self.get_user_name(), 'get_sign_info', response.get('status') is 1, response.get('text'), {
            'current_month': response.get('curMonth'),
            'all_days': response.get('allDays'),
            'had_sign_days': response.get('hadSignDays')
        })

    def do_daily_sign(self):
        response = self.http_get(Config.LIVE_SIGN_DAILY).json()

        if response.get('code') is 0 and response.get('msg') == 'OK':
            return OperatorResult(
                # username operator status message other
                self.get_user_name(), 'do_daily_sign', True, response.get('data').get('text'), {
                'all_days': response.get('data').get('allDays'),
                'had_sign_days': response.get('data').get('hadSignDays')
            })
        else:
            return OperatorResult(self.get_user_name(), 'do_daily_sign', False, response.get('msg'), None)

    def listen(self, live_room_id):
        pass

    def get_own_live_profile(self):
        if self.__own_live_profile is not None:
            return self.__own_live_profile

        self.update_own_live_profile()
        return self.__own_live_profile

    def update_own_live_profile(self):
        response = self.http_get(Config.GET_USER_LIVE_INFO).json()
        response = response.get('data', {})

        LiveUserInfo = namedtuple('LiveUserInfo', 'name silver gold level exp achieve identity')
        self.__own_live_profile = LiveUserInfo(
            response.get('uname'), response.get('silver'), response.get('gold'), response.get('user_level'), {
                'next_exp': response.get('user_next_intimacy'),
                'current_exp': response.get('user_intimacy'),
                'level_rank': response.get('user_level_rank')
            }, response.get('achieve'), {
                'vip': response.get('vip') != 0,
                'svip': response.get('svip') != 0
            }
        )

    def get_own_master_info(self):
        self.update_own_master_info()

    def update_own_master_info(self):
        response = self.http_get(Config.GET_OWN_MASTER_INFO).json()

    def get_own_wear_medal(self):
        self.update_own_wear_medal()

    def update_own_wear_medal(self):
        response = self.http_get(Config.GET_MY_WEAR_MEDAL).json()

    def get_own_medal_list(self):
        self.update_own_medal_list()

    def update_own_medal_list(self):
        response = self.http_get(Config.GET_MY_MEDAL_LIST).json()

    def set_own_sear_medal(self, medal_id):
        pass

    def cancel_own_wear_medal(self):
        response = self.http_get(Config.CANCEL_WEAR_MEDAL).json()

        return response.get('code', None) is 0

    def get_own_wear_title(self):
        self.update_own_wear_title()

    def update_own_wear_title(self):
        response = self.http_get(Config.GET_MY_WEAR_TITLE).json()

    def get_own_title_list(self):
        self.update_own_title_list()

    def update_own_title_list(self):
        response = self.http_get(Config.GET_MY_TITLE_LIST).json()

    def cancel_own_wear_title(self):
        response = self.http_get(Config.CANCEL_WEAR_TITLE).json()

        return response.get('code', None) is 0

    def do_ban_user_on_own_room(self, uid):
        payload = {
            'roomid': 0,
            'uid': 0,
            'type': 1
        }
        response = self.http_get(Config.ADMIN_SHIELD_USER, params = payload)

    def do_dan_mu_report(self):
        payload = {
            'roomid': 0,
            'uid': 0,
            'msg': 'dan mu',
            'reason': 'reason'
        }
        response = self.http_get(Config.USER_DM_REPORT, params = payload).json()

    def get_other_master_info(self, master_uid):
        payload = {
            'uid': 0
        }
        response = self.http_post(Config.GET_OTHER_MASTER_INFO, params = payload)

    def do_attention_master_room(self, master_uid):
        payload = {
            'uid': 0,
            'type': 1
        }
        response = self.http_get(Config.ATTENTION_MASTER_ROOM, params = payload).json()

    def get_current_treasure_info(self):
        pass

    def get_current_award(self):
        pass

    def get_capture(self):
        pass

    async def get_live_room_profile(self, live_room_id = None):
        if live_room_id is None:
            live_room_id = 0
        elif not isinstance(live_room_id, int):
            if isinstance(live_room_id, str) and live_room_id.isalnum():
                live_room_id = int(live_room_id)
            else:
                raise TypeError('live_room_id must be int')

        live_room_id = await Utils.auto_get_real_room_id(self.__loop, live_room_id)
        return await self.update_live_room_profile(live_room_id)

    async def update_live_room_profile(self, live_room_id):
        if not isinstance(live_room_id, int):
            raise TypeError('live_room_id must be int')
        payload = {
            'roomid': live_room_id
        }
        response = self.http_get(Config.GET_ROOM_INFO, params = payload).json()
        response = response.get('data', {})

        LiveRoomProfile = namedtuple('LiveRoomProfile', 'master_id master_name live_room_id live_status \
            live_room_title live_room_fans_count live_rom_gift_top live_room_all_gift is_attention')

        return LiveRoomProfile(
            # master_id
            response.get('MASTERID'),
            # master_name
            response.get('ANCHOR_NICK_NAME'),
            # live_room_id
            response.get('ROOMID'),
            # live_status
            response.get('LIVE_STATUS') == 'LIVE',
            # live_room_title
            response.get('ROOMTITLE'),
            # live_room_fans_count
            response.get('FANS_COUNT'),
            # live_rom_gift_top
            [ { 'uid': u['uid'], 'name': u['uname'], 'coin': u['coin'] } for u in response.get('GIFT_TOP') ],
            # live_room_all_gift
            response['RCOST'],
            # is_attention
            response['IS_STAR']
        )

    def get_own_live_room_id(self):
        pass

    def http_get(self, *args, **kwargs):
        return self.__user_instance.get(*args, **kwargs)

    def http_post(self, *args, **kwargs):
        return self.__user_instance.post(*args, **kwargs)

    def get_user_instance(self):
        return self.__user_instance

    def get_user_name(self):
        return self.__user_instance.name

    def set_user_name(self):
        pass

    def get_user_password(self):
        return self.__user_instance.password

    def get_user_coin(self):
        return self.__user_instance.money

    def get_user_id(self):
        return self.__user_instance.uid

    def get_user_level(self):
        return self.__user_instance.level

    def get_user_face(self):
        return self.__user_instance.face
