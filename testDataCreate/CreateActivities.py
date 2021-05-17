# -*- coding: utf-8 -*-
# @Time: 2021/2/2 10:02
# @Author: Waipang

import common
from datetime import datetime, timedelta


def get_activity_goods(num, activity_type=1, activity_num=100, limit_num=5):
    """
    生成创建活动时所需的商品数据
    :param limit_num: 限购数量(限时抢购用)
    :param activity_num: 活动库存
    :param activity_type: 活动类型: 1: 普通活动(第二件半价,满减) 2: 限时抢购活动 3: 拼团活动
    :param num: 需要添加的商品数量
    :return:
    """

    sql = f"""
    SELECT
        id,
        goods_id,
        price,
        spu_name
    FROM
        goods_sku where goods_id in (SELECT
        a.id
        FROM
        ( SELECT
    id 
    FROM goods_spu WHERE STATUS = 3 AND type = 0 ORDER BY RAND( ) LIMIT {num} ) AS a)
    """

    sql1 = f"""
    SELECT
       id,
       goods_id,
       price,
       spu_name
    FROM
       goods_sku
    WHERE
        id in (1391670749768556545,1391670749948911617,1391670749894385665,1391670750003437569)
       """

    result = common.db.select_all(sql=sql)

    goods_list = []

    for goods in result:
        sku_id = goods[0]
        spu_id = goods[1]
        price = goods[2]
        goods_name = goods[3]
        if activity_type == 1:
            goods_list.append({"goodsId": spu_id, "skuId": sku_id})
        elif activity_type == 2:
            goods_list.append({
                "goodsId": spu_id,
                "skuId": sku_id,
                "activityNum": activity_num,
                "limitNum": limit_num,
                "goodsName": goods_name,
                "sort": 99,
                "price": round(float(price * 80 / 100), 2)})
        elif activity_type == 3:
            goods_list.append({
                "activityNum": activity_num,
                "goodsId": spu_id,
                "goodsName": goods_name,
                "price": round(float(price * 70 / 100), 2),
                "skuId": sku_id,
                "sort": 99
            })
    return goods_list


def half_price_activity(goods_num):
    """
    创建第二件半价活动
    :param goods_num: 需要添加的商品数量
    :return:
    """

    admin_token = common.admin_token()
    # 获取商品数据
    goods_list = get_activity_goods(num=goods_num)

    # 定义开始时间和结束时间
    now = datetime.now()
    start_time = (now + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
    end_time = (now + timedelta(days=300)).strftime('%Y-%m-%d %H:%M:%S')

    # 定义请求参数
    body = {
        "name": f"半价活动({start_time})",
        "startTime": start_time,
        "endTime": end_time,
        "goodsList": goods_list
    }

    # 请求创建活动接口
    request = common.req.request_post(url='/store/manage/promotion/half-price/saveHalfPrice',
                                      token=admin_token,
                                      body=body)
    print(f"""
    {str(body).replace("'", '"')}
    {request['text']}
    """)


def full_discount(goods_num, limit_num=100):
    """
    创建满减活动
    :param limit_num: 限制参与次数
    :param goods_num: 商品数量
    :return:
    """

    full_reduction_detail = []
    # 填写满减活动信息
    while 1:
        add_price = input('输入门槛(0:退出): ')
        if add_price == '0':
            break
        reduce_price = input('输入减免金额: ')
        full_reduction_detail.append({
            "addPrice": add_price,
            "reducePrice": reduce_price,
            "limitNum": limit_num
        })

    # 获取商品数据
    goods_list = get_activity_goods(num=goods_num)

    # 定义开始时间和结束时间
    now = datetime.now()
    start_time = (now + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
    end_time = (now + timedelta(days=300)).strftime('%Y-%m-%d %H:%M:%S')

    # 定义请求参数
    body = {
        "name": f"满减活动({start_time})",
        "startTime": start_time,
        "endTime": end_time,
        "modeType": 0,
        "goodsList": goods_list,
        "addReduce": full_reduction_detail
    }

    # 请求创建活动接口
    request = common.req.request_post(url='/store/manage/promotion/full-discount/saveFullDiscount',
                                      token=common.admin_token(),
                                      body=body)

    common.api_print(name='创建满减活动', url=request['url'], data=body, result=request)


def flash_sale(time_line, days=0, goods_num=10):
    """
    创建限时抢购活动
    :param days: 活动开始日期, 0代表今天,1代表明天,以此类推
    :param goods_num: 需要添加的商品数量
    :param time_line: 时间段, 格式: '20:30:00-21:30:00'
    :return:
    """

    admin_token = common.admin_token()
    now = datetime.now()
    start_time = (now + timedelta(days=days)).strftime('%Y-%m-%d')
    goods_list = get_activity_goods(activity_type=2, num=goods_num)
    activity_name = f"限时抢购({start_time} {time_line})"

    body = {
        "startTime": start_time,
        "seckillName": activity_name,
        "timeLine": time_line,
        "goodsList": goods_list
    }

    request = common.req.request_post(url='/store/manage/promotion/time-limit/saveTimeLimit',
                                      body=body,
                                      token=admin_token)
    if request['code'] != 200:
        print(f'活动 - {activity_name}添加失败, code: {request["code"]}, 错误信息: {request["desc"]}')
        if request['code'] in (8068, 8069):
            return
        else:
            flash_sale(time_line, days, goods_num)
    else:
        common.api_print(name='创建限时抢购活动', url=request['url'], data=body, result=request)


def assemble(day, add_num, goods_num, chief_type, team_type):
    """
    创建拼团活动
    :param add_num: 几人团
    :param team_type: 虚拟成团 0:否 1:是
    :param chief_type: 团长免单 0:否 1:是
    :param day: 开始日期, 今天传0, 明天传1, 以此类推
    :param goods_num: 添加的商品数量
    :return:
    """
    admin_token = common.admin_token()
    now = datetime.now()
    goods_list = get_activity_goods(activity_type=3, num=goods_num)
    start_date = str((now + timedelta(days=day)).date())
    name = f"{add_num}人团{' 团长免单' if chief_type == 1 else ''} {' 虚拟成团' if team_type == 1 else ''}({start_date})"

    body = {
        "addNum": add_num,  # 参团人数
        "limitNum": 30,  # 限购数量
        "chiefType": chief_type,  # 团长免单: 0: 关闭, 1: 开启
        "teamType": team_type,  # 虚拟成团: 0: 关闭, 1: 开启
        "startDate": start_date,  # 开始时间
        "name": name,  # 活动名称
        "title": name,  # 活动标题
        "goodsList": goods_list  # 商品列表
    }

    url = '/store/manage/promotion/pintuan/savePintuan'
    request = common.req.request_post(url=url,
                                      body=body,
                                      token=admin_token)
    if request['code'] != 200:
        print(f'活动 - {name}添加失败, code: {request["code"]} 错误信息: {request["desc"]}')
        if request['code'] in (8068, 8069):
            return
        else:
            assemble(day, add_num, goods_num, chief_type, team_type)
    else:
        common.api_print(name='创建拼团活动', url=request['url'], data=body, result=request)


if __name__ == '__main__':

    "第二件半价活动创建"
    # half_price_activity(goods_num=100)

    "满减活动创建"
    # full_discount(goods_num=10, limit_num=1)

    "拼团活动创建"
    assemble(day=6, add_num=3, goods_num=15, chief_type=1, team_type=0)  # 拼团活动创建
    assemble(day=6, add_num=2, goods_num=15, chief_type=0, team_type=1)  # 拼团活动创建

    "限时抢购活动创建"
    # flash_sale(days=0, time_line='00:00:00-09:59:59', goods_num=10)
    # flash_sale(days=0, time_line='10:00:00-13:59:59', goods_num=10)
    # flash_sale(days=0, time_line='14:00:00-19:59:59', goods_num=10)
    # flash_sale(days=0, time_line='20:00:00-23:59:59', goods_num=10)

    # print(common.account.get_admin_token())
