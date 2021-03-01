# -*- coding: utf-8 -*-
# @Time: 2021/2/23 19:41
# @Author: Waipang

import common
import time
from testDataCreate import Address


def get_default_addr(token):

    try:
        request = common.req.request_get(url='/store/api/user/addr/address/default', token=token)
        addr_id = request['data']['id']
        province_id = request['data']['provinceId']
    except TypeError:
        add_addr = Address.add_address(token=token)
        addr_id = add_addr['data']['id']
        province_id = add_addr['data']['provinceId']

    return addr_id, province_id


def get_cart_list(token):
    """
    获取购物车数据
    :param token: 用户token
    :return:
    """
    get_cart = common.req.request_get(url='/store/api/order-shopping-cart', token=token)
    buy_list = get_cart['data']['buyListRespVOS']
    cart_list = []
    for cart in buy_list:
        cart_id = cart['id']
        cart_list.append(int(cart_id))
    return cart_list


def create_order(token, order_source, coupon_auto_use=0, buy_num=None, sku_id=None,
                 spu_id=None, activity_type=None, activity_id=None,
                 coupon_id=None, half_id=None, full_reduction_id=None,
                 share_dynamic_id=None, share_user_id=None):
    """
    创建订单
    :param token: 用户token
    :param buy_num: 购买数量
    :param sku_id: 规格ID
    :param spu_id: 商品ID
    :param order_source: 0: 购物车, 1: 拼团/限时抢购, 2: 立即购买
    :param coupon_auto_use: 自动使用优惠券 0: 否, 1: 是
    :param coupon_id: 优惠券ID, order_source=2时选填
    :param share_dynamic_id: 种草内容分享人ID, order_source=2时选填
    :param share_user_id:  分享人ID, order_source=2时选填
    :param half_id: 半价活动ID, order_source=2时选填
    :param full_reduction_id: 满减活动ID, order_source=0, 2时选填
    :param activity_type: 0: 拼团, 1: 限时抢购
    :param activity_id: 活动ID
    :return:
    """
    if order_source not in (0, 1, 2):
        print('订单类型有误')
        return

    body = {
        'type': order_source
    }

    # 购物车
    if order_source == 0:
        cart_list = get_cart_list(token=token)
        if not cart_list:
            return
        else:
            body['shoppingCartDisReqVO'] = {"id": cart_list}
    # 活动
    elif order_source == 1:
        body['settleActivityReqVO'] = {
            'buyNum': buy_num,
            'skuId': sku_id,
            'type': activity_type,
            'activityId': activity_id,
            'remark': ''
        }
    # 立即购买
    elif order_source == 2:
        body['orderSettleBuyNowReqVO'] = {
            'buyNum': buy_num,
            'skuId': sku_id,
            'spuId': spu_id,
            'remark': ''
        }
        # 判断是否有传半价ID
        if half_id is not None:
            body['orderSettleBuyNowReqVO']['halfId'] = half_id
        # 判断是否有传满减ID
        if full_reduction_id is not None:
            body['orderSettleBuyNowReqVO']['fullReductionId'] = full_reduction_id
        # 判断是否有传动态分享人ID
        if share_dynamic_id is not None:
            body['orderSettleBuyNowReqVO']['shareDynamicId'] = share_dynamic_id
        # 判断是否有传分享人ID
        if share_user_id is not None:
            body['orderSettleBuyNowReqVO']['shareUserId'] = share_user_id

    # 判断是否有传优惠券
    if coupon_id is not None and order_source in (0, 2):
        body['couponId'] = coupon_id
        body['isUseCoupon'] = 'true'
    else:
        body['isUseCoupon'] = 'false'

    # 判断是否自动使用优惠券
    if coupon_auto_use == 1:
        body['isUseCoupon'] = 'true'
    else:
        body['isUseCoupon'] = 'false'

    addr_id, province_id = get_default_addr(token)
    body['provinceId'] = province_id

    # 获取订单结算信息
    discounts_info = common.req.request_post(url='/store/api/order/getSettleDiscountsInfo',
                                             body=body,
                                             token=token)
    print(f"""
    【获取订单结算信息】
    请求信息
    {body}
    返回信息
    {discounts_info['text']}
    """.replace("'", '"').replace('None', 'null'))
    time.sleep(0.5)

    # 获取商品结算信息
    goods_info = common.req.request_post(url='/store/api/order/getSettleGoodsInfo',
                                             body=body,
                                             token=token)
    print(f"""
    【获取商品结算信息】
    请求信息
    {body}
    返回信息
    {goods_info['text']}
    """.replace("'", '"').replace('None', 'null'))
    time.sleep(0.5)

    if order_source == 0:
        cart_list = []
        del body['shoppingCartDisReqVO']
        for cart_id in get_cart_list(token=token):
            cart_list.append({
                'id': cart_id,
                'remark': ''
            })
        body['orderConfirmCartReqVO'] = {
            'cartList': cart_list
        }

    # 在提交参数中删除省份ID,添加收货地址
    del body['provinceId']
    body['userAddressId'] = addr_id

    # 判断是否自动使用优惠券
    if coupon_auto_use == 1:
        body['couponId'] = discounts_info['data']['couponId']
        body['isUseCoupon'] = 'true'

    # 提交订单
    confirm_order = common.req.request_post(url='/store/api/order/confirmOrder',
                                            body=body,
                                            token=token)

    print(f"""
    【提交订单】
    请求信息
    {body} 
    返回信息
    {confirm_order['text']}
    ==============================================================================================================
    """.replace("'", '"').replace('None', 'null'))


def batch_order_rand_create(token, num=100):
    """
    单个用户创建多个订单
    :return:
    """
    select = common.db.select_all(sql=f"""
    SELECT
        sku.id AS 'sku_id',
        spu.id AS 'spu_id'
    FROM
        goods_sku sku
    LEFT JOIN goods_spu spu ON spu.id = sku.goods_id
    WHERE
        spu.audit_status  = 1
        AND	spu.status = 3
        AND spu.type = 0
        AND sku.is_deleted = 0
        AND spu.supplier_id is not NULL
        AND sku.price > 0
    ORDER BY RAND()
    LIMIT {num}""")

    a = 0
    addr_id, province_id = get_default_addr(token)

    for result in select:
        sku_id = result[0]
        spu_id = result[1]

        body = {
            "type": 2,
            "orderSettleBuyNowReqVO": {
                "buyNum": 1,
                "remark": "",
                "skuId": sku_id,
                "spuId": spu_id,
                "provinceId": province_id
            }
        }

        # 获取订单结算信息
        discounts_info = common.req.request_post(url='/store/api/order/getSettleDiscountsInfo',
                                                 body=body,
                                                 token=token)

        # 提交订单
        del body['provinceId']  # 删除省份信息
        body['userAddressId'] = addr_id  # 添加地址信息字段
        confirm_order = common.req.request_post(url='/store/api/order/confirmOrder',
                                                body=body,
                                                token=token)
        a += 1

        print(f"""
        请求：
        {body}
        【获取订单结算金额】
        响应：
        {discounts_info['text']},
        【提交订单】  
        返回
        {confirm_order['text']},
        第{a}次订单创建
        ------------------------------------
        """)
        time.sleep(0.5)


if __name__ == '__main__':
    # 登录用户账号,并获取token
    user_token = common.user_token(mobile=19216850004)

    # 创建随机批量订单
    # batch_order_rand_create(token=user_token, mobile=19216850004, num=20)  # 创建单商品订单

    # 创建拼团订单
    # create_order(token=user_token, buy_num=1, sku_id=1353289069920022530,
    #              order_source=1, activity_type=0, activity_id=1365861771373568002)

    # 创建限时抢购订单
    # create_order(token=user_token, buy_num=1, sku_id=1353289298035634177,
    #              order_source=1, activity_type=1, activity_id=1366198754356539393)

    # 立即购买(普通/臻宝/VIP商品订单)
    create_order(token=user_token, buy_num=2, spu_id=1366289834699685889, sku_id=1366289834708074498, order_source=2,
                 coupon_auto_use=0)

    # 购物车商品创建订单
    # create_order(token=user_token, order_source=0)
