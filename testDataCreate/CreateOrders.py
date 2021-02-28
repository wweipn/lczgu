# -*- coding: utf-8 -*-
# @Time: 2021/2/23 19:41
# @Author: Waipang

import common
import time
import Config
import random
from testDataCreate import Address


def batch_order_create(token, num=100):
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

    for result in select:
        sku_id = result[0]
        spu_id = result[1]

        body = {
            "type": 2,
            "orderSettleBuyNowReqVO": {
                "buyNum": 1,
                "remark": "",
                "skuId": sku_id,
                "spuId": spu_id
            }
        }

        discounts_info = common.req.request_post(url='/store/api/order/getSettleDiscountsInfo',
                                                 body=body,
                                                 token=token)
        body['userAddressId'] = 98
        confirm_order = common.req.request_post(url='/store/api/order/confirmOrder',
                                                body=body,
                                                token=token)
        a += 1
        print(f"""{discounts_info['text']},
              {confirm_order['text']},
              f'已操作第{a}次订单创建""")
        time.sleep(0.5)


if __name__ == '__main__':

    # 登录用户账号,并获取token
    common.account.user_login(['19216850004'])
    user_token = common.account.get_user_token(mobile='19216850004')

    batch_order_create(token=user_token, num=3)  # 创建单商品订单

    # 添加商品评论
    # for data in get_order_goods_id():
    #     add_evaluate(token=user_token, order_goods=data)
    #     time.sleep(0.5)

    # 添加追评
    # add_evaluate(token=user_token, add_type=3)

    # 获取评论
    # print(content_get())


