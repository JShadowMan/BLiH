#!/usr/bin/env python3

from BLiH import bliHelper

helper = bliHelper(afterLogin = False)

result = helper.select('GoogleMap').doSign()
print(result)