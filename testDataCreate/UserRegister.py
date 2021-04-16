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
    pass
    # 推荐人注册
    # user_register(r_mobile=19216850225, count=12)

    # 无推荐人注册
    # user_register(count=1)

    account_list = [
        19216880132,
        19216880133,
        19216880134,
        19216880135,
        19216880136,
        19216880137,
        19216880138,
        19216880139,
        19216880140,
        19216880141,
        19216880142,
        19216880143,
        19216880144,
        19216880145,
        19216880146,
        19216880147,
        19216880148,
        19216880149,
        19216880150,
        19216880151,
        19216880152,
        19216880153,
        19216880154,
        19216880155,
        19216880156,
        19216880157,
        19216880158
    ]
    # 指定参数注册
    for i in account_list:
        common.account.user_register(mobile=i, recommend_id='1')
        time.sleep(0.1)
    # common.account.user_register(mobile=19216880053, recommend_id='1')
