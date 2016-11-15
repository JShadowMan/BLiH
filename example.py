#!/usr/bin/env python3
#
# Copyright (C) 2016 ShadowMan
#
import random
import asyncio
import logging
from bilibili import Live, Helper, Config, Utils

loop = asyncio.get_event_loop()
helper = Helper.bliHelper(loop = loop)

loop.set_debug(True)

async def foreach(helper):
    for username in helper.accounts():
        trans = helper.select(username)
        # print(trans.get_sign_info())
        # print(trans.do_daily_sign())
        # print(trans.get_own_live_profile())
        # print(trans.get_live_room_profile())
        u = await trans.get_live_room_profile(102)
        print(u)
        print(trans.http_post('http://live.bilibili.com/user/getMasterInfo', data = { 'uid': u.master_id }).text)

task = [
    Live.LiveBiliBili(loop = loop).listen(80914, Utils.MessageHandler),
    Live.LiveBiliBili(loop = loop).listen(102, Utils.MessageHandler),
    Live.LiveBiliBili(loop = loop).listen(5285, Utils.MessageHandler),
    Live.LiveBiliBili(loop = loop).listen(1030, Utils.MessageHandler),
    Live.LiveBiliBili(loop = loop).listen(245, Utils.MessageHandler),
    Live.LiveBiliBili(loop = loop).listen(139, Utils.MessageHandler),
    Live.LiveBiliBili(loop = loop).listen(5123, Utils.MessageHandler),
    foreach(helper)
]

loop.run_until_complete(asyncio.gather(*task))
