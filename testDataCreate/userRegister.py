# -*- coding: utf-8 -*-
# @Time: 2021/1/25 14:43
# @Author: Waipang

import common


def user_register(count=1, r_mobile=None):
    """
    用户注册
    :param count: 注册用户数量
    :param r_mobile: 推荐人手机号
    :return:
    """
    for i in range(count):
        common.account.user_register(r_mobile=r_mobile)


if __name__ == '__main__':
    user_register(1)
