''' BiliBili Helper Utils

'''

import random
import asyncio

def liveAnonymousUID():
    return int(100000000000000 + (200000000000000 * random.random()))

