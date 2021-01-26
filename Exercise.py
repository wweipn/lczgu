# -*- coding: utf-8 -*-
# @Time: 2021/1/4 12:33
# @Author: Waipang

import common


if __name__ == '__main__':
    user_login = common.account.user_login(['18123929299'])
    user_token = common.account.get_user_token('18123929299')
    user_info = common.req.request_get('/store/api/account/userinfo', token=user_token)
    print(user_info['text'], type(user_info['text']))
