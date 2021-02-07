# -*- coding: utf-8 -*-
# @Time: 2021/2/2 19:35
# @Author: Waipang

import common
from datetime import datetime, timedelta
import random


def get_category():
    """
    随机获取十个三级分类
    :return: 分类字符串
    """
    result = common.db.select_all(sql="""
    SELECT
        id
    FROM
        goods_category
    WHERE 
        level = 3
    ORDER BY RAND()
    LIMIT 10
    """)
    category_detail = ''
    for category in result:
        category_id = category[0]
        category_detail += str(category_id) + ','
    return category_detail[:-1]


def get_goods():
    """
    随机获取十个sku
    :return: sku字符串
    """
    result = common.db.select_all(sql=f"""
    SELECT
        sku.id AS 'skuId'
    FROM
        goods_sku sku
        left join goods_spu spu ON spu.id = sku.goods_id
    WHERE
        spu.audit_status  = 1
    AND	spu.status = 3
    AND spu.type = 0   
        ORDER BY RAND()
    LIMIT 10
        """)

    goods_detail = ''
    for goods in result:
        sku_id = goods[0]
        goods_detail += str(sku_id) + ','
    return goods_detail[:-1]


def coupon_create(vip=None):
    """
    添加优惠券
    :return:
    """
    time_type = int(input('时间类型(0: 固定时间, 1: 相对时间): \n'))
    coupon_type = int(input('获取方式(0: 商品详情页领取, 1: 新用户注册赠送, 2: VIP赠送, 3: 后台发放): \n'))
    use_scope = int(input('使用范围(0: 全品, 1: 分类, 2: 商品): \n'))

    coupon_price = random.randint(10, 60)
    coupon_threshold_price = random.randint(100, 300)
    body = {
        "title": f"{coupon_price}元优惠券（满{coupon_threshold_price}元可用）",
        "couponPrice": coupon_price,
        "couponThresholdPrice": coupon_threshold_price,
        "scopeDescription": "优惠券使用范围描述",
        "activityDescription": "优惠券描述",
        "useScope": use_scope,
        "type": coupon_type
    }

    # 优惠券时间类型
    if time_type == 1:
        # 相对时间, 时间长度为7天
        body['timeType'] = 1
        body['timeValue'] = 7

    elif time_type == 0:
        # 固定时间, 开始时间为当前时间+1分钟, 结束时间为当前时间+7天
        now = datetime.now()
        start_time = (now + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
        end_time = (now + timedelta(minutes=3)).strftime('%Y-%m-%d %H:%M:%S')
        body['timeType'] = 0
        body['startTime'] = start_time
        body['endTime'] = end_time

    else:
        print('时间类型有误')
        return

    # 优惠券获取方式
    if coupon_type == 0:
        # 商品详情页获取, 默认限领数量为1, 发放数量为100
        body['userType'] = 0 if vip is None else 1
        body['createNum'] = 100
        body['limitNum'] = 1

    # 优惠券使用范围
    if use_scope == 0:
        # 全品
        body['scopeId'] = 0
    elif use_scope == 1:
        # 部分分类
        body['scopeId'] = get_category()

    elif use_scope == 2:
        # 部分商品
        body['scopeId'] = get_goods()

    common.account.admin_login()
    admin_token = common.account.get_admin_token()
    print(str(body).replace("'", '"'))
    request = common.req.request_post(url='/store/manage/promotion/coupon/addSaveCoupon',
                                      token=admin_token,
                                      body=body)
    data = request['data']

    print(f"""
【优惠券创建成功】
标题: {data['title']}
金额: {data['couponPrice']}元
门槛: {data['couponThresholdPrice']}元
开始时间: {data['startTime']}
结束时间: {data['endTime']}
获取方式: {data['type']}
适用范围: {data['useScope']}
使用详情（分类/商品ID）: {body['scopeId']}
    """)


if __name__ == '__main__':
    coupon_create()
