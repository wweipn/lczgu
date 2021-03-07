# -*- coding: utf-8 -*-
# @Time: 2021/3/7 16:17
# @Author: Waipang

import common


def up_status_deliver(token, shop_order_id):
    for order_goods in get_shop_order_delivers_goods(shop_order_id):
        request = common.req.request_post(url='/store/seller/order/upStatusDeliver', body=order_goods)


def get_shop_order_delivers_goods(shop_order_id):
    """
    获取未发货的商品, 包装发货所需数据结构后返回
    :param shop_order_id:
    :return:
    """
    request = common.req.request_post(url='/store/seller/order/getShopOrderDeliverGoods',
                                      params={'shopOrderId': shop_order_id})
    order_goods_list = []
    for goods in request['data']:
        order_goods_list.append({
            'mainOrderCode': goods['mainOrderCode'],  # 主订单Id
            'shopOrderCode': goods['shopOrderCode'],  # 子订单Id
            'id': goods['id'],  # 商品订单Id
            'count': goods['count'],  # 商品数量
            'sku': goods['sku'],  # skuId
            'name': goods['name'],  # 商品名称
            'thumbnail': goods['thumbnail'],  # 商品主图
            'deliverCount': goods['deliverCount'],  # 已发货数量
            'remainCount': goods['remainCount'],  # 剩余可发货数量
            'nowDeliverCount': goods['remainCount'],  # 发货数量
            "logisticsCode": "JD0037980871457",  # 运单编号
            "logisticsName": "京东",  # 快递公司
        })

    return order_goods_list


def get_order_shop_id(order_all_id):
    result = common.db.select_all(sql=f"""
    SELECT
        order_goods.order_shop_id,
        shop_info.shop_name
    FROM
        order_goods
        LEFT JOIN shop_info ON shop_info.id = order_goods.shop_id
    WHERE
        order_id = '{order_all_id}'
    AND
        order_goods.STATUS = 4
    AND
        order_goods.is_deleted = 0
    GROUP BY order_goods.order_shop_id
    """)

    order_shop_id_list = []
    for data in result:
        order_shop_id = data[0]
        shop_name = data[1]
        if shop_name not in order_shop_id_list:
            order_shop_id_list.append({
                shop_name: order_shop_id
            })
        else:
            order_shop_id_list[shop_name].append(order_shop_id)
    return order_shop_id_list


def order_all_shipments(order_all_id):

    order_all_detail = get_order_shop_id(order_all_id=1368501227842715649)
    for data in order_all_detail:
        for shop_name, order_shop_id in data.items():
            shop_token = common.shop_token(shop_name)


if __name__ == '__main__':
    a = get_order_shop_id(order_all_id=1368501227842715649)
    print(a)