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

loop.run_until_complete(Live.LiveBiliBili(loop = loop).listen(102, Utils.MessageHandler))
