# -*- coding: utf-8 -*-
# @Time: 2021/3/14 1:17
# @Author: Waipang

import common


def apply_refund(token, order_goods):
    result = common.db.select_one(sql=f"""
    SELECT
        order_goods.order_id AS 'order_id', -- 主订单ID
        order_goods.order_shop_id AS 'order_shop_id',  -- 子订单ID
        order_goods.id AS 'order_goods_id', -- 商品订单ID
        order_goods.sku_id AS 'sku_id',  -- 规格ID
        order_goods.pay_price AS 'pay_price' -- 实付金额
    FROM
        order_goods
    WHERE
        order_goods.id = {order_goods} -- 商品订单ID
    LIMIT 1
    """)

    order_id = result[0]
    order_shop_id = result[1]
    order_goods_id = result[2]
    sku_id = result[3]
    pay_price = result[4]

    url = '/store/api/orderRefund/appOrderRefund'
    body = {
        "orderId": order_id,
        "orderShopId": order_shop_id,
        "orderGoodsId": order_goods_id,
        "skuId": sku_id,
        "money": float(pay_price),
        "type": 1,
        "note": "Wepn_apply",
        "unreceivedRefundReason": 1
    }

    request = common.req.request_post(token=token, url=url, body=body)
    common.api_print(name='申请退款', url=url, data=body, result=request)


def apply_post_sale(token, order_goods, post_sale_type):
    """
    申请售后
    :param token:
    :param order_goods:
    :param post_sale_type: 售后类型: 1: 退款, 2: 退货退款, 3: 换货
    :return:
    """
    result = common.db.select_one(sql=f"""
    SELECT
        order_goods.order_id AS 'order_id', -- 主订单ID
        order_goods.order_shop_id AS 'order_shop_id',  -- 子订单ID
        order_goods.id AS 'order_goods_id', -- 商品订单ID
        order_goods.sku_id AS 'sku_id',  -- 规格ID
        order_goods.pay_price AS 'pay_price' -- 实付金额
    FROM
        order_goods
    WHERE
        order_goods.id = {order_goods} -- 商品订单ID
    LIMIT 1
    """)

    order_id = result[0]
    order_shop_id = result[1]
    order_goods_id = result[2]
    sku_id = result[3]
    pay_price = result[4]

    url = '/store/api/PostSale/addOrderPostSaleList'
    body = {
        "orderId": order_id,
        "orderShopId": order_shop_id,
        "orderGoodsId": order_goods_id,
        "skuId": sku_id,
        "money": float(pay_price),
        "type": post_sale_type,
        "note": "Wepn_apply",
    }

    sale_type_str = ''
    if post_sale_type == 1:
        body['receivedRefundReason'] = 1
        sale_type_str = '退款'
    elif post_sale_type == 2:
        body['refundReturnReason'] = 1
        sale_type_str = '退货退款'
    elif post_sale_type == 3:
        body['barterReason'] = 1
        sale_type_str = '换货'

    request = common.req.request_post(token=token, url=url, body=body)
    common.api_print(name=f'申请售后({sale_type_str})', url=url, data=body, result=request)


if __name__ == '__main__':

    "申请退款"
    apply_refund(token=common.user_token(18123929299), order_goods=1390550214411612161)

    "申请售后: 1: 退款, 2: 退货退款, 3: 换货"
    # apply_post_sale(token=common.user_token(18123929299), order_goods=1390550214411612161, post_sale_type=1)
