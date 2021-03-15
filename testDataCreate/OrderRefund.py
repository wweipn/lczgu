# -*- coding: utf-8 -*-
# @Time: 2021/3/14 1:17
# @Author: Waipang

import common


def apply_refund(token, order_all):
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
        order_goods.order_id = {order_all} -- 主订单ID
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
    print(f"""
    【申请退款】（{url}）
    请求
    {body}

    返回
    {request['text']}
    """)


if __name__ == '__main__':
    token = common.user_token(19216850035)
    apply_refund(token=token, order_all=1370789701996261378)
