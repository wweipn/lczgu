# -*- coding: utf-8 -*-
# @Time: 2021/3/3 11:14
# @Author: Waipang

import common
from datetime import datetime, timedelta
from testDataCreate.Coupon import send_coupon


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

    if result is None:
        print(f'账号{mobile}不存在')
        return
    else:
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
        end_time = str((now + timedelta(days=1)).date())
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

    """
    修改用户可提现余额/臻宝/活动余额
    money_type: 类型 0:可提现余额, 1:活动余额, 2:臻宝
    update_type: 修改类型 1:扣除, 2:添加
    """
    update_user_money(token=common.admin_token(), mobile=19216850208, money_type=0, update_type=1, money=10000)

    # send_coupon(account_id=1354604046874423298, coupon_id=1377905938366816257)
