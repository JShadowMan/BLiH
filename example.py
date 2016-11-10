#!/usr/bin/env python3
#
# Copyright (C) 2016 ShadowMan
#
import random
import asyncio
from bilibili import Live, Helper, Config, Utils

helper = Helper.bliHelper()

for username in helper.accounts():
    print(helper.select(username).do_daily_sign().message.decode(Config.ENCODING))

loop = asyncio.get_event_loop()

task = [
    Live.LiveBiliBili(loop = loop).listen(80914, Utils.MessageHandler),
    Live.LiveBiliBili(loop = loop).listen(102, Utils.MessageHandler),
    Live.LiveBiliBili(loop = loop).listen(5285, Utils.MessageHandler),
    Live.LiveBiliBili(loop = loop).listen(1030, Utils.MessageHandler),
    Live.LiveBiliBili(loop = loop).listen(245, Utils.MessageHandler),
    Live.LiveBiliBili(loop = loop).listen(139, Utils.MessageHandler),
    Live.LiveBiliBili(loop = loop).listen(5123, Utils.MessageHandler),
]

loop.run_until_complete(asyncio.gather(*task))
