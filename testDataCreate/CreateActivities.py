# -*- coding: utf-8 -*-
# @Time: 2021/2/2 10:02
# @Author: Waipang

import common
from datetime import datetime, timedelta


def admin_token():
    common.account.admin_login()
    token = common.account.get_admin_token()
    return token


def get_activity_goods(num=10, activity_type=1, activity_num=100, limit_num=10):
    """
    生成添加活动时所需的商品数据
    :param limit_num: 限购数量(限时抢购用)
    :param activity_num: 活动库存(限时抢购用)
    :param activity_type: 活动类型: 1: 普通活动(第二件半价,满减) 2: 限时抢购活动
    :param num: 需要添加的商品数量
    :return:
    """
    result = common.db.select_all(sql=f"""
    SELECT
        sku.id AS 'skuId',
        spu.id AS 'spuId',
        sku.price
    FROM
        goods_sku sku
        left join goods_spu spu ON spu.id = sku.goods_id
    WHERE
        spu.audit_status  = 1
        AND	spu.status = 3
        AND spu.type = 0   
    ORDER BY RAND()
    LIMIT {num}
    """)

    goods_list = []

    # 判断查询结果是否为空
    if result:
        for goods in result:
            sku_id = goods[0]
            spu_id = goods[1]
            price = goods[2]
            if activity_type == 1:
                goods_list.append({"goodsId": spu_id, "skuId": sku_id})
            elif activity_type == 2:
                goods_list.append({"goodsId": spu_id,
                                   "skuId": sku_id,
                                   "activityNum": activity_num,
                                   "limitNum": limit_num,
                                   "price": float(price - (price * 15 / 100))
                                   })
        return goods_list
    else:
        print('商品列表为空')
        return


def half_price_activity(goods_num):
    """
    创建第二件半价活动
    :param goods_num: 需要添加的商品数量
    :return:
    """

    # 获取商品数据
    goods_list = get_activity_goods(goods_num)

    # 定义开始时间和结束时间
    now = datetime.now()
    start_time = (now + timedelta(minutes=1.5)).strftime('%Y-%m-%d %H:%M:%S')
    end_time = (now + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')

    # 定义请求参数
    body = {
        "name": f"半价活动({start_time})",
        "startTime": start_time,
        "endTime": end_time,
        "goodsList": goods_list
    }

    # 请求创建活动接口
    request = common.req.request_post(url='/store/manage/promotion/half-price/saveHalfPrice',
                                      token=admin_token(),
                                      body=body)
    print(body, '\n---------------------------------------\n')
    print(request['text'], '\n', request['rep_time'])


def full_discount(goods_num):
    """
    创建满减活动
    :param goods_num: 商品数量
    :return:
    """
    full_reduction_detail = []
    # 填写满减活动信息
    while 1:
        add_price = input('0: 退出\n输入减免金额: ')
        if add_price == '0':
            break
        reduce_price = input('输入门槛: ')
        full_reduction_detail.append({
            "addPrice": add_price,
            "reducePrice": reduce_price
        })

    # 获取商品数据
    goods_list = get_activity_goods(goods_num)

    # 定义开始时间和结束时间
    now = datetime.now()
    start_time = (now + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
    end_time = (now + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')

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
                                      token=admin_token(),
                                      body=body)
    print(body, '\n---------------------------------------\n')
    print(request['text'])


def flash_sale(time_line, days=0, goods_num=10):
    """
    创建限时抢购活动
    :param days: 活动开始日期, 0代表今天,1代表明天,以此类推
    :param goods_num: 需要添加的商品数量
    :param time_line: 时间段, 格式: '20:30:00-21:30:00'
    :return:
    """

    now = datetime.now()
    start_time = (now + timedelta(days=days)).strftime('%Y-%m-%d')
    goods_list = get_activity_goods(activity_type=2, num=goods_num)
    seckill_name = f"限时抢购{start_time}({time_line})"

    body = {
     "startTime": start_time,
     "seckillName": seckill_name,
     "timeLine": time_line,
     "goodsList": goods_list
    }

    request = common.req.request_post(url='/store/manage/promotion/time-limit/saveTimeLimit',
                                      body=body,
                                      token=admin_token())

    print(f"""
活动【{seckill_name}】添加成功:
商品信息：
{goods_list}
""")


if __name__ == '__main__':
    # half_price_activity(goods_num=500)
    # full_discount(goods_num=500)
    # flash_sale(days=1, time_line='21:30:00-21:59:59')
    flash_sale(time_line='14:41:00-22:59:00')
    # flash_sale(days=1, time_line='23:00:00-23:59:00')

