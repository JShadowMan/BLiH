#!/usr/bin/env python3
#
# Copyright (C) 2016 ShadowMan
#
import random
import asyncio
import logging
from bilibili import Live, Helper, Config, Utils

helper = Helper.bliHelper()

for username in helper.accounts():
    trans = helper.select(username)
    print(trans.get_sign_info())
    print(trans.do_daily_sign())
    print(trans.get_own_live_info())
    print(trans.http_post('http://live.bilibili.com/User/getUserInfo').json())

loop = asyncio.get_event_loop()
loop.set_debug(True)

# task = [
#     Live.LiveBiliBili(loop = loop).listen(80914, Utils.MessageHandler),
#     Live.LiveBiliBili(loop = loop).listen(102, Utils.MessageHandler),
#     Live.LiveBiliBili(loop = loop).listen(5285, Utils.MessageHandler),
#     Live.LiveBiliBili(loop = loop).listen(1030, Utils.MessageHandler),
#     Live.LiveBiliBili(loop = loop).listen(245, Utils.MessageHandler),
#     Live.LiveBiliBili(loop = loop).listen(139, Utils.MessageHandler),
#     Live.LiveBiliBili(loop = loop).listen(5123, Utils.MessageHandler),
# ]
#
# loop.run_until_complete(asyncio.gather(*task))

