# -*- coding: utf-8 -*-
# @Time: 2021/2/2 19:35
# @Author: Waipang

import common
from datetime import datetime, timedelta
import random
import time
import csv


def get_category(num=100):
    """
    随机获取十个三级分类
    :return: 分类字符串
    """
    result = common.db.select_all(sql=f"""
    SELECT
        id
    FROM
        goods_category
    WHERE 
        level = 3
    # ORDER BY RAND()
    # LIMIT {num}
    and id in (13515060933055774,13515062230521774,13515056768405504,13515062259336642,13515060168308326,
13515060470256271,13515059996719349,13515060068400005,13515061609932554,13515060586019061,13515061551254241,
13515062071977082,13515062316085575,13515060268552192,13515061712231628,13515060614750044,13515060297157345,
13515058669641564,13515060182736732,13515060053971599,13515060484684677,13515061106196643,13515061220659200,
13515061176744837,13515062244782407,13515062202084392,13515061669407784,13515060097214873,13515061034180444,
13515062173437296,13515062301782999,13515061464222433,13515058843705180,13515061091516579,13515061697803223,
13515065764013178,13515058640239493,13515061507633479,13515058742664396,13515060412752363,13515060398533672,
13515062043246100,13515060239947038,13515066285281280,13515059968114196,13515062187739873,13515060890273873,
13515067366195363,13515057331406929,13515061826694184,13515061421146931,13515061941198684,13515059491221831,
13515061726366433,13515058712759009,13515059693471170) 
    """)
    category_detail = ''
    for category in result:
        category_id = category[0]
        category_detail += str(category_id) + ','
    return category_detail[:-1]


def get_goods(num=30):
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
    LIMIT {num}
        """)

    goods_detail = ''
    for goods in result:
        sku_id = goods[0]
        goods_detail += str(sku_id) + ','
    return goods_detail[:-1]


def coupon_create(vip=None, limit_num=None, create_num=None):
    """
    添加优惠券
    :return:
    """
    # time_type = int(input('时间类型(0: 固定时间, 1: 相对时间): \n'))
    time_type = random.randint(0, 1)
    # coupon_type = int(input('获取方式(0: 商品详情页领取, 1: VIP赠送到账, 2: 注册赠送到账, 3: 后台发放): \n'))
    coupon_type = 0
    # use_scope = int(input('使用范围(0: 全品, 1: 分类, 2: 商品): \n'))
    use_scope = random.randint(0, 2)

    coupon_price = random.randint(10, 50)
    coupon_threshold_price = random.randint(51, 200)
    # coupon_price = float(input('请输入优惠券金额:\n'))
    # coupon_threshold_price = float(input('请输入优惠券门槛:\n'))

    body = {
        "title": f"{coupon_price}元优惠券",
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
        body['timeValue'] = random.randint(1, 7)
        # body['timeValue'] = 31

    elif time_type == 0:
        # 固定时间, 开始时间为当前时间+1分钟, 结束时间为当前时间+7天
        now = datetime.now()
        start_time = (now + timedelta(minutes=0.2)).strftime('%Y-%m-%d %H:%M:%S')
        end_time = (now + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
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
        # is_show = int(input('是否展示在领券中心(0: 显示, 1: 隐藏)'))
        is_show = 0
        body['isShow'] = is_show
        body['createNum'] = create_num if create_num is not None else 10
        body['limitNum'] = limit_num if limit_num is not None else 1

    # 优惠券使用范围
    if use_scope == 0:
        # 全品
        body['scopeId'] = 0
        body['title'] = body['title'] + '(全品)'

    elif use_scope == 1:
        # 部分分类
        body['scopeId'] = get_category()
        body['title'] = body['title'] + '(分类)'

    elif use_scope == 2:
        # 部分商品
        body['scopeId'] = get_goods()
        body['title'] = body['title'] + '(部分商品)'

    common.account.admin_login()
    admin_token = common.account.get_admin_token()
    print(str(body).replace("'", '"'))
    request = common.req.request_post(url='/store/manage/promotion/coupon/addSaveCoupon',
                                      token=admin_token,
                                      body=body)
    common.api_print(name='创建优惠券', url=request['url'], data=body, result=request)


def receive_coupon(token, coupon_id, save_data=None):
    url = f'/store/api/promotion/member-coupon/{coupon_id}/receive?receiveSource=0'
    request = common.req.request_get(url=url, token=token)

    if save_data == 1:
        return token, url

    print(request['text'])


def send_coupon(coupon_id, account_id):
    token = common.admin_token()
    url = '/store/manage/promotion/coupon-user/saveInfoCoupon'
    body = {
        "memberIds": account_id,
        "couponId": coupon_id,
        "memberStatus": 1,
        "operateReason": "wepn_send"
    }
    request = common.req.request_post(url=url, body=body, token=token)
    common.api_print(name='发放优惠券', url=url, result=request, data=body)


if __name__ == '__main__':
    "优惠券创建"
    for i in range(32):
        coupon_create(vip=None, create_num=None, limit_num=None)
        time.sleep(0.2)

    "领取优惠券"
    # coupon_list = []
    # user_token = common.user_token(19216850293)
    #
    # for i in coupon_list:
    #     receive_coupon(token=user_token, coupon_id=i)
    #     time.sleep(0.2)
