#!/usr/bin/env python
#
# Copyright (C) 2016 ShadowMan
#
import asyncio
import logging
from collections import namedtuple
from bs4 import BeautifulSoup
from bilibili import Config, User, Exceptions, Utils, Live

OperatorResult = namedtuple('OperatorResult', 'username operator status message result other')

class Transaction(object):

    def __init__(self, user, loop = None):
        if isinstance(user, User.User):
            self.__user_instance = user

            self.__own_live_room_id = None
            self.__own_master_profile = None
            self.__own_live_profile = None

            self.__own_wear_medal = None
            self.__own_medal_list = None

            self.__own_wear_title = None
            self.__own_title_list = None
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
            # username
            self.get_user_name(),
            # operator
            'get_sign_info',
            # status
            response.get('status') is 1,
            # message
            response.get('text'),
            # result
            None,
            # other
            {
                'current_month': response.get('curMonth'),
                'all_days': response.get('allDays'),
                'had_sign_days': response.get('hadSignDays')
            }
        )

    def do_daily_sign(self):
        response = self.http_get(Config.LIVE_SIGN_DAILY).json()

        if response.get('code') is 0 and response.get('msg') == 'OK':
            return OperatorResult(
                # username
                self.get_user_name(),
                # operator
                'do_daily_sign',
                # status
                True,
                # message
                response.get('data').get('text'),
                # result
                None,
                # other
                {
                    'all_days': response.get('data').get('allDays'),
                    'had_sign_days': response.get('data').get('hadSignDays')
                }
            )
        else:
            return OperatorResult(
                # username
                self.get_user_name(),
                # operator
                'do_daily_sign',
                # status
                False,
                # message
                response.get('msg'),
                # result
                None,
                # other
                None
            )

    async def listen(self, live_room_id, handle = None):
        if not isinstance(live_room_id, int):
            raise TypeError('live_room_id must be int type')
        if isinstance(handle, Live.PackageHandlerProtocol):
            raise TypeError('handle must be base PackageHandlerProtocol')
        asyncio.ensure_future(Live.LiveBiliBili(loop = self.__loop).listen(live_room_id, handle))

    async def get_own_live_profile(self):
        if self.__own_live_profile is not None:
            return self.__own_live_profile
        return await self.update_own_live_profile()

    async def update_own_live_profile(self):
        response = self.http_get(Config.GET_USER_LIVE_INFO).json()
        message = response.get('msg', None)
        response = response.get('data', {})

        LiveProfile = namedtuple('LiveProfile', 'name silver gold level exp achieve identity room_id \
            master_profile live_room_profile')
        Exp = namedtuple('Exp', 'next_exp current_exp level_rank')

        self.__own_live_room_id = await self.get_own_live_room_id()
        own_live_master_profile = await self.get_own_master_info()
        live_room_profile = await self.get_live_room_profile(self.__own_live_room_id)
        self.__own_live_profile = LiveProfile(
            # name
            response.get('uname'),
            # silver
            response.get('silver'),
            # gold
            response.get('gold'),
            # level
            response.get('user_level'),
            # exp
            Exp(
                # next_exp
                response.get('user_next_intimacy'),
                # current_exp
                response.get('user_intimacy'),
                # level_rank
                response.get('user_level_rank')
            ),
            # achieve
            response.get('achieve'),
            # identity
            { 'vip': response.get('vip') != 0, 'svip': response.get('svip') != 0 },
            # room_id
            self.__own_live_room_id,
            # master_profile
            own_live_master_profile,
            # live_room_profile
            live_room_profile
        )
        return self.__own_live_profile

    async def get_own_live_room_id(self):
        if self.__own_live_profile is not None:
            return self.__own_live_profile.room_id
        if self.__own_live_room_id is not None:
            return self.__own_live_room_id

        response = self.http_get(Config.GET_OWN_LIVE_ROOM_INFO)
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            self.__own_live_room_id = int(soup.find('div', class_ = 'room-info-wrap').p.a.text)
            return self.__own_live_room_id
        except Exception as e:
            logging.debug('get_own_live_room_id %s', e)

    async def get_own_master_info(self):
        if self.__own_live_room_id is None:
            self.__own_live_room_id = await self.get_own_live_room_id()
        if self.__own_master_profile is not None:
            return self.__own_master_profile
        return await self.update_own_master_info()

    async def update_own_master_info(self):
        payload = { 'roomid': self.__own_live_room_id }
        response = self.http_get(Config.GET_OWN_MASTER_INFO, params = payload).json()

        MasterProfile = namedtuple('MasterProfile', 'has_cover user_cover has_num tags_num cover_audit_status \
            bg_audit_status bg_num cover_num allow_upload_bg_time cover_list total_num bg_list allow_update_area_time')

        response = response.get('data', {})
        self.__own_master_profile = MasterProfile(
            # has_cover
            response.get('hasCover'),
            # user_cover
            response.get('userCover'),
            # has_num
            response.get('hasNum'),
            # tags_num
            response.get('tagsNum'),
            # cover_audit_status
            response.get('coverAuditStatus'),
            # bg_audit_status
            response.get('bgAuditStatus'),
            # bg_num
            response.get('bgNum'),
            # cover_num
            response.get('coverNum'),
            # allow_upload_bg_time
            response.get('allowUploadBgTime'),
            # cover_list
            response.get('coverList'),
            # total_num
            response.get('totalNum'),
            # bg_list
            response.get('bgList'),
            # allow_update_area_time
            response.get('allowUpdateAreaTime')
        )
        return self.__own_master_profile

    async def get_own_wear_medal(self):
        if self.__own_wear_medal is not None:
            return self.__own_wear_medal
        return await self.update_own_wear_medal()

    async def update_own_wear_medal(self):
        response = self.http_get(Config.GET_MY_WEAR_MEDAL).json()
        response = response.get('data', {})

        MedalProfile = namedtuple('MedalProfile', 'medal_id medal_name master_room_id master_id is_wear')
        WearMedalInfo = namedtuple('WearMedalInfo', 'id self_uid wear_medal_id current_intimacy next_intimacy \
            day_limit level guard_level medal_profile master_name rank score is_wear')

        self.__own_wear_medal = WearMedalInfo(
            # id
            response.get('id', None),
            # self_uid
            response.get('uid', None),
            # wear_medal_id
            response.get('medal_id', None),
            # current_intimacy
            response.get('intimacy', 0),
            # next_intimacy
            response.get('next_intimacy', 0),
            # day_limit
            response.get('dayLimit', 0),
            # level
            response.get('level', None),
            # guard_level
            response.get('guard_level', None),
            # medal_profile
            MedalProfile(
                # medal_id
                response.get('medalInfo', {}).get('id'),
                # medal_name
                response.get('medalInfo', {}).get('medal_name'),
                # master_room_id
                response.get('medalInfo', {}).get('roomid'),
                # master_id
                response.get('medalInfo', {}).get('uid'),
                # is_wear
                response.get('medalInfo', {}).get('status', False)
            ),
            # master_name
            response.get('anchorName', None),
            # rank
            response.get('rank', None),
            # score
            response.get('score', None),
            # is_wear
            response.get('isWear', False) == 1
        )
        return self.__own_wear_medal

    async def get_own_medal_list(self):
        if self.__own_medal_list is not None:
            return self.__own_medal_list
        return await self.update_own_medal_list()

    async def update_own_medal_list(self):
        response = self.http_get(Config.GET_MY_MEDAL_LIST).json()
        response = response.get('data', {})

        MedalProfile = namedtuple('MedalProfile', 'medal_id medal_name is_wear master_name level')
        self.__own_medal_list = [
            MedalProfile(
                # medal_id
                medal['medalId'],
                # medal_name
                medal['medalName'],
                # is_wear
                medal['status'] == 1,
                # master_name
                medal['anchorName'],
                # level
                medal['level']
            ) for medal in response
        ]
        return self.__own_medal_list

    def do_wear_own_fans_medal(self, medal_id):
        if not isinstance(medal_id, int):
            raise TypeError('medal_id must be int type')
        payload = { 'medal_id': medal_id }
        response = self.http_post(Config.WEAR_FANS_MEDAL, params = payload).json()

        return OperatorResult(
            # username
            self.__user_instance.name,
            # operator
            'wear_own_fans_medal',
            # status
            response.get('code') is 0,
            # message
            response.get('msg'),
            # result
            None,
            # other
            response.get('data')
        )

    def do_cancel_own_wear_medal(self):
        response = self.http_get(Config.CANCEL_WEAR_MEDAL).json()

        return OperatorResult(
            # username
            self.__user_instance.name,
            # operator
            'wear_own_fans_medal',
            # status
            response.get('code') is 0,
            # message
            response.get('msg'),
            # result
            None,
            # other
            response.get('data')
        )

    async def get_own_wear_title(self):
        if self.__own_wear_title is not None:
            return self.__own_wear_title
        return await self.update_own_wear_title()

    async def update_own_wear_title(self):
        response = self.http_get(Config.GET_MY_WEAR_TITLE).json()

        # TODO perfect this
        TitleProfile = namedtuple('TitleProfile', 'has_title_list is_wear remark')

        self.__own_wear_title = TitleProfile(
            # has_title_list
            response.get('data', {}).get('hasTitleList'),
            # is_wear
            response.get('data', {}).get('isWear'),
            # !remark!
            '!imperfect!'
        )
        return self.__own_wear_title

    async def get_own_title_list(self):
        if self.__own_title_list is not None:
            return self.__own_title_list
        return await self.update_own_title_list()

    async def update_own_title_list(self):
        response = self.http_get(Config.GET_MY_TITLE_LIST).json()

        # TODO perfect this
        TitleProfile = namedtuple('TitleProfile', 'remark')

        self.__own_title_list = [
            TitleProfile(
                # remark
                '!imperfect!'
            ) for title in response.get('data', {})
        ]
        return self.__own_title_list

    def cancel_own_wear_title(self):
        response = self.http_get(Config.CANCEL_WEAR_TITLE).json()
        return response.get('code', None) is 0

    async def do_ban_user_on_own_room(self, uid):
        if self.__own_live_room_id is None:
            self.__own_live_room_id = await self.get_own_live_room_id()
        return await self.do_ban_user_on_live_room(uid, self.__own_live_room_id)

    async  def do_ban_user_on_live_room(self, uid, live_room_id):
        payload = { 'roomid': live_room_id, 'uid': uid, 'type': 1 }
        response = self.http_post(Config.ADMIN_SHIELD_USER, data = payload).json()
        # TODO


    def do_dan_mu_report(self):
        # TODO
        payload = {
            'roomid': 0,
            'uid': 0,
            'msg': 'dan mu',
            'reason': 'reason'
        }
        response = self.http_get(Config.USER_DM_REPORT, params = payload).json()

    def get_master_level_profile(self, master_uid):
        if not isinstance(master_uid, int):
            raise TypeError('master_uid must be int type')

        payload = {
            'uid': master_uid
        }
        response = self.http_post(Config.GET_OTHER_MASTER_INFO, data = payload).json()
        response = response.get('data', {})

        MasterLevelProfile = namedtuple('MasterLevelProfile', 'sort master_level next_score upgrade_score')
        return MasterLevelProfile(
            # sort
            response.get('sort', -1),
            # master_level
            response.get('master_level', -1),
            # next_score
            response.get('next_score', None),
            # upgrade_score
            response.get('upgrade_score', None)
        )

    def do_attention_master_room(self, master_uid):
        # TODO
        payload = {
            'uid': 0,
            'type': 1
        }
        response = self.http_get(Config.ATTENTION_MASTER_ROOM, params = payload).json()

    def get_current_treasure_info(self):
        # TODO
        pass

    def get_current_award(self):
        # TODO
        pass

    def get_capture(self):
        # TODO
        pass

    async def get_live_room_profile(self, live_room_id = None):
        if live_room_id is None:
            if self.__own_live_room_id is None:
                self.__own_live_room_id = await self.get_own_live_room_id()
            live_room_id = self.__own_live_room_id
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

    def http_get(self, *args, **kwargs):
        return self.__user_instance.get(*args, **kwargs)

    def http_post(self, *args, **kwargs):
        return self.__user_instance.post(*args, **kwargs)

    def get_user_instance(self):
        return self.__user_instance

    def get_user_name(self):
        return self.__user_instance.name

    def set_user_name(self):
        # TODO
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
