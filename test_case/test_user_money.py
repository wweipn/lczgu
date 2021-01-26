# -*- coding: utf-8 -*-
# @Time: 2021/1/5 20:25
# @Author: Waipang

import common


if __name__ == '__main__':
    user_login = common.account.user_login(['18123929299'])
    shop_login = common.account.shop_login('上海一休电子', 'a123456')
    admin_login = common.account.admin_login()
    user_token = common.account.get_user_token('18123929299')
    shop_token = common.account.get_shop_token()
    admin_token = common.account.get_admin_token()
    print(user_token)
    print(shop_token)
    print(admin_token)
