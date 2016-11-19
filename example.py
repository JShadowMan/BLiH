#!/usr/bin/env python3
#
# Copyright (C) 2016 ShadowMan
#
import random
import asyncio
import logging
from bilibili import Live, Helper, Config, Utils

loop = asyncio.get_event_loop()
helper = Helper.bliHelper(loop = loop, log = logging.DEBUG)

loop.set_debug(True)

async def foreach(helper):
    for username in helper.accounts():
        trans = helper.select(username)
        # print(trans.get_sign_info())
        # print(trans.do_daily_sign())
        own_live_profile = await trans.get_own_live_profile()
        print(own_live_profile)

        live_room_profile = await trans.get_live_room_profile(live_room_id = 102)
        print(live_room_profile)
        master_profile = trans.get_master_level_profile(live_room_profile.master_id)
        print(master_profile)

task = [
    # Live.LiveBiliBili(loop = loop).listen(80914, Utils.MessageHandler),
    # Live.LiveBiliBili(loop = loop).listen(102, Utils.MessageHandler),
    # Live.LiveBiliBili(loop = loop).listen(5285, Utils.MessageHandler),
    # Live.LiveBiliBili(loop = loop).listen(1030, Utils.MessageHandler),
    # Live.LiveBiliBili(loop = loop).listen(245, Utils.MessageHandler),
    # Live.LiveBiliBili(loop = loop).listen(139, Utils.MessageHandler),
    # Live.LiveBiliBili(loop = loop).listen(5123, Utils.MessageHandler),
    foreach(helper)
]

loop.run_until_complete(asyncio.gather(*task))
