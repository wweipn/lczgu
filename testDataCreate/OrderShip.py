# -*- coding: utf-8 -*-
# @Time: 2021/3/7 16:17
# @Author: Waipang

import common
import random


def order_shop_delivery(order_shop_id):
    """
    子订单发货
    :param order_shop_id: 子订单ID
    :return:
    """

    # 获取商家名称
    shop_name = get_shop_name(order_shop_id=order_shop_id)
    if shop_name == 400:
        print(f'子订单({order_shop_id})没有待发货的商品')
        return

    # 商家登录
    shop_token = common.shop_token(shop_name)

    # 遍历未发货商品， 分别调用接口请求
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
        random_int = random.randint(1000000000, 9999999999)
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
            "logisticsCode": "JD00" + str(random_int),  # 运单编号
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


def get_order_all_id(token):
    """
    获取已发货订单
    :param token: token
    :return:
    """
    order_id_list = []
    body = {
        "currentPage": 1,
        "pageSize": 100,  # 每页数量
        "status": 3  # 状态 : 0.全部 ；1.待付款，2：待发货; 3.待收货；4.待评价
    }

    request = common.req.request_post(token=token, url='/store/api/order/myOrder', body=body)

    for data in request['data']['records']:
        order_all_id = data['orderCode']
        order_id_list.append(order_all_id)

    return order_id_list


def get_logistics(token, order_all_id):
    """
    获取主订单下的物流单号
    :param token: token
    :param order_all_id: 主订单ID
    :return:
    """
    body = {
        "orderCode": order_all_id,
        "receiving": 'true'
    }
    request = common.req.request_post(token=token, url='/store/api/order/getLogistics', body=body)

    logistics_code_list = []

    for data in request['data']:
        logistics_code = data['logisticsCode']
        logistics_code_list.append(logistics_code)

    return logistics_code_list


def goods_receiving(token, order_all_id=None):
    """
    确认收货
    :param order_all_id:
    :param token:
    :return:
    """
    url = '/store/api/order/userReceiving'
    if not order_all_id:
        logistics_list = get_logistics(token=token, order_all_id=order_all_id)
        body = {'logisticsCode': logistics_list,
                'orderCode': order_all_id}
        request = common.req.request_post(token=token, url=url, body=body)
        print(f"""
        【确认收货】({url})
        请求
        {body}

        返回
        {request['text']}
        """.replace("'", '"'))

    else:
        for order_all_id in get_order_all_id(token=token):

            # 确认收货
            logistics_list = get_logistics(token=token, order_all_id=order_all_id)
            body = {'logisticsCode': logistics_list,
                    'orderCode': order_all_id}
            request = common.req.request_post(token=token, url=url, body=body)

            print(f"""
            【确认收货】({url})
            请求
            {body}
        
            返回
            {request['text']}
            """.replace("'", '"'))


if __name__ == '__main__':
    pass
    # 子订单发货
    # order_shop_delivery(order_shop_id=1368501227842715650)

    # 主订单发货
    # order_all_delivery(order_all_id=1368841200169136129)

    # order_all_list = []
    #
    # for i in order_all_list:
    #     order_all_delivery(order_all_id=i)

    user_token = common.user_token(15295993410)
    # print(get_order_all_id(token=user_token))
    # get_logistics(token=user_token, order_all_id=1369625196465606657)
    goods_receiving(token=user_token, order_all_id=1369625196465606657)
