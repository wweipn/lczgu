# -*- coding: utf-8 -*-
# @Time: 2021/1/4 12:33
# @Author: Waipang

import common
from datetime import datetime, timedelta

now = datetime.now()
# start_time = now.strftime('%Y-%m-%d')
start_time = (now + timedelta(days=0)).strftime('%Y-%m-%d')
print(start_time)