#!/usr/bin/env python3
#
# Copyright (C) 2016 ShadowMan
#
import sys
import random
import asyncio
import logging
from bilibili import Live, Helper, Config, Utils, Exceptions, Package

loop = asyncio.get_event_loop()
helper = Helper.bliHelper(loop = loop, log = logging.DEBUG)
loop.set_debug(True)

class MessageHandler(Package.PackageHandlerProtocol):

    def __init__(self, *, file = sys.stdout):
        super(MessageHandler, self).__init__()

    def on_error_occurs(self, package):
        print(package)

    def on_welcome_message(self, contents):
        print(contents)

    def on_heartbeat_response(self, contents):
        print(contents)

    def on_allow_join(self):
        print('Join room complete')
        return True

    def on_dan_mu_message(self, contents):
        print(contents)

    def on_gift_message(self, contents):
        print(contents)

async def foreach(user_instance = None, helper = None, loop = None):
    if not isinstance(helper, Helper.Helper):
        raise Exceptions.FatalException('fatal error occurs, helper instance invalid')
    trans = helper.select(user_instance.name)

    result = await trans.get_sign_info()
    if not result.status:
        print('first sign_daily succeed', (await trans.do_daily_sign()).message)
    else:
        print('sign_daily succeed', result.message)

    own_live_profile = await trans.get_own_live_profile()
    print(own_live_profile)

    live_room_profile = await trans.get_live_room_profile(live_room_id = 102)
    print(live_room_profile)
    master_profile = await trans.get_master_level_profile(live_room_profile.master_id)
    print(master_profile)

    print(await trans.get_own_wear_medal())
    print(await trans.get_own_medal_list())

    await trans.listen(80914, MessageHandler)
    await trans.listen(102, MessageHandler)
    await trans.listen(245, MessageHandler)
    await trans.listen(1030, MessageHandler)

    medal_list = await trans.get_own_medal_list()
    print(await trans.do_wear_own_fans_medal(random.choice(medal_list).medal_id))
    print(await trans.do_wear_own_fans_medal(119))

    # TODO Imperfect
    print(await trans.get_own_wear_title())
    print(await trans.get_own_title_list())



# task = [
#     # Live.LiveBiliBili(loop = loop).listen(80914, MessageHandler),
#     # Live.LiveBiliBili(loop = loop).listen(102, MessageHandler),
#     # Live.LiveBiliBili(loop = loop).listen(5285, MessageHandler),
#     # Live.LiveBiliBili(loop = loop).listen(1030, MessageHandler),
#     # Live.LiveBiliBili(loop = loop).listen(245, MessageHandler),
#     # Live.LiveBiliBili(loop = loop).listen(139, MessageHandler),
#     # Live.LiveBiliBili(loop = loop).listen(5123, MessageHandler),
#     foreach(helper)
# ]

# loop.run_until_complete(asyncio.gather(*task))
# loop.run_until_complete(helper.async_foreach(foreach))
# pending = asyncio.Task.all_tasks()
# loop.run_until_complete(asyncio.gather(*pending))
helper.async_startup(
    helper.async_foreach(foreach)
)