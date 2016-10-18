#!/usr/bin/env python3

import sys
from BLiH import bliHelper

helper = bliHelper(afterLogin = False)
print(helper.accounts())

transaction = helper.select('GoogleMap')
print(transaction.doSign())
