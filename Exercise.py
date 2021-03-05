# -*- coding: utf-8 -*-
# @Time: 2021/1/4 12:33
# @Author: Waipang

import common
from datetime import datetime, timedelta

common.account.user_login(source=1)

print(common.account.get_user_token())
