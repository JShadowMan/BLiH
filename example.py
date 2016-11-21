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

        result = trans.get_sign_info()
        if not result.status:
            print(trans.do_daily_sign().message)
        else:
            print('sign_daily succeed', result.message)

        # own_live_profile = await trans.get_own_live_profile()
        # print(own_live_profile)

        # live_room_profile = await trans.get_live_room_profile(live_room_id = 102)
        # print(live_room_profile)
        # master_profile = trans.get_master_level_profile(live_room_profile.master_id)
        # print(master_profile)

        # print(await trans.get_own_wear_medal())
        # print(await trans.get_own_medal_list())

        await trans.listen(80914, Utils.MessageHandler)
        await trans.listen(102, Utils.MessageHandler)
        await trans.listen(245, Utils.MessageHandler)
        await trans.listen(1030, Utils.MessageHandler)
        await trans.listen(245, Utils.MessageHandler)

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

# loop.run_until_complete(asyncio.gather(*task))
loop.run_until_complete(foreach(helper))
pending = asyncio.Task.all_tasks()
loop.run_until_complete(asyncio.gather(*pending))
