# -*- coding: utf-8 -*-
# @Time: 2021/6/21 11:38
# @Author: Waipang
import common


def assist(token, launch_id):
    """
    助力
    :param token:
    :param launch_id:
    :return:
    """

    request = common.req.request_get(url=f'/store/api/assist/{launch_id}', token=token)
    common.api_print(name='助力', url=request['url'], data=launch_id, result=request)
    return int(request['data']['status'])


def get_assist_info(token):
    """
    获取助力提现信息
    :return:
    """
    request = common.req.request_get(url='/store/api/assist/info', token=token)
    assist_id = request['data']['launchAssistInfo']['id']
    token = request['req_header']['Authorization'][7:]
    print(f'{assist_id},{token}')


def assist_from_file(launch_id, time=1):
    """
    获取csv文件中的账号进行助力
    :return:
    """
    # 批量登录文件中的账号
    common.account.user_login(source=1)
    user_token_list = common.account.get_user_token()

    # 初始化助力次数
    count = 0
    for data in user_token_list:
        todo_assist = assist(token=data[1], launch_id=launch_id)
        # 助力成功, 增加次数
        if todo_assist in (4, 5):
            count += 1

        # 当前账号助力失败, 使用下一个账号
        elif todo_assist in (1, 2, 3, 6, 7):
            continue

        # 活动已失效, 退出
        else:
            print('活动已失效')
            return

        # 已达到要求的助力次数, 退出
        if time == count:
            return


def get_access_launch_assist_id(mobile):
    """
    获取已达成的活动ID
    :param mobile: 手机号
    :return:
    """

    result = common.db.select_one(sql=f"""
    select id from launch_assist where account_id = (select id from user_account where mobile = {mobile}) and status = 2
    """)

    return result


def withdrawal(mobile):
    """
    发起提现
    :param mobile: 手机号
    :return:
    """

    launch_assist_id = get_access_launch_assist_id(mobile)
    if launch_assist_id is not None:
        body = {
            'launchAssistId': launch_assist_id[0]
        }
        request = common.req.request_post(url='/store/api/trade/activityWithdrawal', token=common.user_token(mobile), body=body)

        common.api_print(name='申请提现', url=request['url'], data=body, result=request)
    else:
        print(f'未达成或未发起助力提现, 不符合提现申请条件\n')


if __name__ == '__main__':

    while 1:
        apply_for_withdrawal_mobile = int(input('输入申请提现的手机号: '))
        withdrawal(mobile=apply_for_withdrawal_mobile)


