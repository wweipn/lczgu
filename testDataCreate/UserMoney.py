# -*- coding: utf-8 -*-
# @Time: 2021/3/3 11:14
# @Author: Waipang

import common
from datetime import datetime, timedelta


def update_user_money(token, mobile, money_type, update_type, money):
    """
    修改用户可提现余额/臻宝/活动余额
    :param token: 管理后台token
    :param mobile: 用户手机号
    :param money: 增加/扣除金额
    :param update_type: 修改类型 1:扣除, 2:添加
    :param money_type: 类型 0:可提现余额, 1:活动余额, 2:臻宝
    :return:
    """

    # 查询账号account_id
    result = common.db.select_one(sql=f"""
    SELECT id FROM user_account WHERE mobile = {mobile}
    """)
    account_id = result[0]

    body = {
        "accountId": account_id,
        "money": money,
        "remark": "Wepn_update",
        "moneyType": money_type,
        "type": update_type,
    }

    # 判断是否是添加活动余额的类型,如果是,则在请求信息加上过期时间
    if money_type == 1 and update_type == 2:
        now = datetime.now()
        end_time = str((now + timedelta(days=7)).date())
        body['endTime'] = end_time

    request = common.req.request_post(url='/store/manage/finance/updateAccountBalance', token=token, body=body)
    print(f"""
    【修改账户金额】
    请求参数
    {body}
    
    返回参数
    {request['text']}
    """.replace("'", '"'))


if __name__ == '__main__':
    # 获取管理后台token
    admin_token = common.admin_token()

    # 修改用户可提现余额/臻宝/活动余额
    # money_type: 类型 0:可提现余额, 1:活动余额, 2:臻宝
    # update_type: 修改类型 1:扣除, 2:添加
    update_user_money(token=admin_token, mobile=13113103424, money_type=2, update_type=2, money=999999)

    # user_list = [17199990013, 17199990015, 17199990016, 17199990021, 17199990044, 17199990046, 17199990048,
    # 17199990050, 17199990052, 17199990056, 17199990058, 17199990060, 17199990062, 17199990064, 17199990073,
    # 17199990075, 17199990077, 17199990079, 17199990081, 17199990083, 17199990085, 17199990087, 17199990089,
    # 17199990091, 19216821501, 17199990095, 17199990097, 17199990098, 19216850015, 19216862001, 19216862002,
    # 19216862003, 19216862004, 19216862005]

    # user_money_dic = [{"mobile": 17199990013, "money": 9927.00}, {"mobile": 17199990015, "money": 9812.00},
    # {"mobile": 17199990016, "money": 9796.00}, {"mobile": 17199990021, "money": 9829.00}, {"mobile": 17199990044,
    # "money": 9861.40}, {"mobile": 17199990046, "money": 9818.50}, {"mobile": 17199990048, "money": 9877.12},
    # {"mobile": 17199990050, "money": 9869.00}, {"mobile": 17199990052, "money": 9531.00}, {"mobile": 17199990056,
    # "money": 9899.00}, {"mobile": 17199990058, "money": 9887.10}, {"mobile": 17199990060, "money": 9693.00},
    # {"mobile": 17199990062, "money": 9860.10}, {"mobile": 17199990064, "money": 9600.00}, {"mobile": 17199990073,
    # "money": 9793.00}, {"mobile": 17199990075, "money": 9511.00}, {"mobile": 17199990077, "money": 9712.00},
    # {"mobile": 17199990079, "money": 9567.20}, {"mobile": 17199990081, "money": 9784.20}, {"mobile": 17199990083,
    # "money": 9511.00}, {"mobile": 17199990085, "money": 9885.00}, {"mobile": 17199990087, "money": 4910.00},
    # {"mobile": 17199990089, "money": 9501.00}, {"mobile": 17199990091, "money": 9936.20}, {"mobile": 17199990095,
    # "money": 9856.00}, {"mobile": 17199990097, "money": 9874.10}, {"mobile": 17199990098, "money": 9462.00},
    # {"mobile": 19216821501, "money": 9825.00}, {"mobile": 19216850015, "money": 9774.60}, {"mobile": 19216862001,
    # "money": 9528.00}, {"mobile": 19216862002, "money": 9511.00}, {"mobile": 19216862003, "money": 9802.00},
    # {"mobile": 19216862004, "money": 9809.00}, {"mobile": 19216862005, "money": 9796.00}]

    # for mobile in user_list:
    #     update_user_money(token=admin_token, mobile=mobile, update_type=2, money_type=0, money=9999)
