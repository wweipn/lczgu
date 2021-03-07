# -*- coding: utf-8 -*-
# @Time: 2021/3/7 16:17
# @Author: Waipang

import common


def order_shop_delivery(order_shop_id):
    """
    子订单发货
    :param order_shop_id: 子订单ID
    :return:
    """
    shop_name = get_shop_name(order_shop_id=order_shop_id)
    if shop_name == 400:
        print(f'子订单({order_shop_id})没有待发货的商品')
        return

    shop_token = common.shop_token(shop_name)
    for order_goods in get_shop_order_delivers_goods(token=shop_token, order_shop_id=order_shop_id):
        body = {
            'orderDeliverRespVOS': [order_goods]
        }

        request = common.req.request_post(url='/store/seller/order/upStatusDeliver',
                                          body=body,
                                          token=shop_token)
        print(f"""
        商家【{shop_name}】发货(/store/seller/order/upStatusDeliver)
        请求：
        {body}

        返回：
        {request['text']}
        """.replace("'", '"').replace('None', 'null'))


def get_shop_order_delivers_goods(token, order_shop_id):
    """
    获取未发货的商品, 包装成发货接口所需数据结构后返回
    :param token: 商家token
    :param order_shop_id: 子订单Id
    :return:
    """
    request = common.req.request_post(url='/store/seller/order/getShopOrderDeliverGoods',
                                      token=token,
                                      params={'shopOrderId': order_shop_id})
    order_goods_list = []
    # 遍历接口返回的商品信息,依次写入order_goods_list列表中
    for goods in request['data']:
        order_goods_list.append({
            'mainOrderCode': goods['mainOrderCode'],  # 主订单Id
            'shopOrderCode': goods['shopOrderCode'],  # 子订单Id
            'id': goods['id'],  # 商品订单Id
            'count': goods['count'],  # 商品数量
            'sku': goods['sku'],  # skuId
            'name': goods['name'],  # 商品名称
            'thumbnail': goods['thumbnail'],  # 商品主图
            'deliverCount': goods['remainCount'],  # 已发货数量
            'remainCount': goods['remainCount'],  # 剩余可发货数量
            'nowDeliverCount': goods['remainCount'],  # 发货数量
            "logisticsCode": "JD0037980871457",  # 运单编号
            "logisticsName": "京东",  # 快递公司
        })

    return order_goods_list


def get_shop_name(order_shop_id):
    """
    根据子订单ID查询商家名称
    :param order_shop_id: 子订单ID
    :return:
    """
    result = common.db.select_one(sql=f"""
    SELECT
        shop_info.shop_name
    FROM
        order_goods
        LEFT JOIN shop_info ON shop_info.id = order_goods.shop_id
    WHERE
        order_shop_id = '{order_shop_id}'
    AND
        order_goods.STATUS = 4
    AND
        order_goods.is_deleted = 0
    GROUP BY order_goods.order_shop_id
    """)

    # 查询子订单ID下是否存在未发货的商品,如果没有,则返回400
    try:
        shop_name = result[0]
        return shop_name

    except TypeError:
        return 400


def get_order_shop_id(order_all_id):
    """
    根据主订单ID获取子订单ID
    :param order_all_id:
    :return:
    """

    # 通过订单商品表查询所有子订单ID和商家名称
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

    # 遍历查询到的结果
    for data in result:
        order_shop_id = data[0]
        shop_name = data[1]
        # 如果列表中不存在对应商家的字典,则添加字典并写入
        if shop_name not in order_shop_id_list:
            order_shop_id_list.append({
                shop_name: order_shop_id
            })
        else:
            order_shop_id_list[shop_name].append(order_shop_id)
    return order_shop_id_list


def order_all_delivery(order_all_id):
    """
    主订单发货
    :param order_all_id: 主订单ID
    :return:
    """
    order_all_detail = get_order_shop_id(order_all_id=order_all_id)
    for data in order_all_detail:
        for shop_name, order_shop_id in data.items():
            order_shop_delivery(order_shop_id=order_shop_id)


if __name__ == '__main__':

    # 子订单发货
    # order_shop_delivery(order_shop_id=1368501227842715650)

    # 主订单发货
    order_all_delivery(order_all_id=1368487894049636354)
