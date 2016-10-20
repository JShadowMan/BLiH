#!/usr/bin/env python3

from bilibili import Live
import asyncio


loop = asyncio.get_event_loop_policy()

print(Live.LiveBiliBili().listen(1017))