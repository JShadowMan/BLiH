#!/usr/bin/env python3
#
# Copyright (C) 2016 ShadowMan
#
import random
from bilibili import Live, Helper, Config

helper = Helper.bliHelper()

for username in helper.accounts():
    print(helper.select(username).do_daily_sign().message.decode(Config.ENCODING))

print(Live.LiveBiliBili().listen(5279))

