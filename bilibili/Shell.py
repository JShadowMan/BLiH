#!/usr/bin/env python
#
# Copyright (C) 2016 ShadowMan
#
import asyncio
import argparse
from bilibili import Utils

def parse_args():
    parse = argparse.ArgumentParser()
    group = parse.add_mutually_exclusive_group()

    parse.add_argument('-u', '--user', help = 'username')
    parse.add_argument('-p', '--password', help = 'password')
    parse.add_argument('-q', '--qr-login', help = 'using qr-code login', action = 'store_true')
    parse.add_argument('-c', '--user-count', help = 'max user count, default by 1', type = int)

    return parse.parse_args()

def entry_point():
    event_loop = asyncio.get_event_loop()

    args = Utils.check_args(parse_args())