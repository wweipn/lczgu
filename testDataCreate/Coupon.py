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
    time_type = int(input('时间类型(1: 相对时间, 0: 固定时间): \n'))
    coupon_type = int(input('获取方式(1: 商品详情页领取, 2: 新用户注册赠送, 3: VIP赠送, 4: 后台发放): \n'))
    use_scope = int(input('使用范围(1: 全品, 2: 分类, 3: 商品): \n'))

    coupon_price = random.randint(10, 50)
    coupon_threshold_price = random.randint(100, 200)
    body = {
        "title": f"{coupon_price}元优惠券",
        "couponPrice": coupon_price,
        "couponThresholdPrice": coupon_threshold_price,
        "scopeDescription": "这个是范围描述",
        "activityDescription": "优惠券活动描述"
    }

    # 优惠券时间类型
    if time_type == 1:
        # 相对时间, 时间长度为7天
        body['timeType'] = 1
        body['timeValue'] = 7

    elif time_type == 0:
        # 固定时间, 开始时间为当前时间+30秒, 结束时间为当前时间+7天
        now = datetime.now()
        start_time = (now + timedelta(seconds=30)).strftime('%Y-%m-%d %H:%M:%S')
        end_time = (now + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
        body['timeType'] = 0
        body['startTime'] = start_time
        body['endTime'] = end_time

    else:
        print('时间类型有误')
        return

    # 优惠券获取方式
    if coupon_type == 1:
        # 商品详情页获取, 默认限领数量为1, 发放数量为100
        body['type'] = "FREE_GET"
        body['userType'] = 0 if not vip else 1
        body['createNum'] = 100
        body['limitNum'] = 1

    elif coupon_type == 2:
        # 新用户注册赠送
        body['type'] = "NEW_USER_CIRCLE"

    elif coupon_type == 3:
        # VIP券
        body['type'] = "VIP_USER_CIRCLE"

    elif coupon_type == 4:
        # 后台指定用户发放
        body['type'] = "PROVIDE_USER_COUPON"

    else:
        print('优惠券获取方式有误')
        return

    # 优惠券使用范围
    if use_scope == 1:
        # 全品
        body['useScope'] = "ALL"
        body['scopeId'] = 0
    elif use_scope == 2:
        # 部分分类
        body['useScope'] = "CATEGORY"
        body['scopeId'] = get_category()

    elif use_scope == 3:
        # 部分商品
        body['useScope'] = "SOME_GOODS"
        body['scopeId'] = get_goods()

    common.account.admin_login()
    admin_token = common.account.get_admin_token()
    request = common.req.request_post(url='/store/manage/promotion/coupon/addSaveCoupon',
                                      token=admin_token,
                                      body=body)
    print(request['text'])


if __name__ == '__main__':
    coupon_create()
