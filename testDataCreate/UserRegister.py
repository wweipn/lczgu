# -*- coding: utf-8 -*-
# @Time: 2021/1/25 14:43
# @Author: Waipang

import common
import time


def user_register(count=1, r_mobile=None):
    """
    用户注册
    :param count: 注册用户数量
    :param r_mobile: 推荐人手机号
    :return:
    """
    for i in range(count):
        common.account.user_register(r_mobile=r_mobile)
        # time.sleep(0.5)


if __name__ == '__main__':

    """
    推荐人注册
    """
    user_register(r_mobile=None, count=5000)

    """
    无推荐人注册
    """
    # user_register(count=1)

    """
    指定参数注册
    """
    # account_list = [
    #
    # ]
    #
    # for account in account_list:
    #     common.account.user_register(mobile=account, recommend_id='1')
    #     time.sleep(0.1)
