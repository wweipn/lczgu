# -*- coding: utf-8 -*-
# @Time: 2021/3/7 16:17
# @Author: Waipang

import common
import time
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

    # 遍历未发货商品,分别调用接口请求
    shop_order_delivers_goods = get_shop_order_delivers_goods(token=shop_token, order_shop_id=order_shop_id)

    # 判断是否存在未发货的商品,没有则返回
    if len(shop_order_delivers_goods) == 0:
        print(f'商家【{shop_name}】当前订单(order_shop_id: {order_shop_id})没有待发货的商品')
        return

    for order_goods in shop_order_delivers_goods:
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
        # random_int = random.randint(1000000000, 9999999999)
        order_goods_list.append({
            'mainOrderCode': goods['mainOrderCode'],  # 主订单Id
            'shopOrderCode': goods['shopOrderCode'],  # 子订单Id
            'id': goods['id'],  # 商品订单Id
            "logisticsName": "京东",  # 物流公司
            # "logisticsCode": "JD00" + str(random_int),  # 运单编号
            "logisticsCode": 'JD0037980871457',  # 运单编号
            'nowDeliverCount': goods['remainCount'],  # 发货数量
            # 'nowDeliverCount': 1,  # 发货数量
            # 'count': goods['count'],  # 商品数量
            # 'sku': goods['sku'],  # skuId
            # 'name': goods['name'],  # 商品名称
            # 'thumbnail': goods['thumbnail'],  # 商品主图
            # 'deliverCount': goods['remainCount'],  # 已发货数量
            # 'remainCount': goods['remainCount'],  # 剩余可发货数量
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

    # 根据主订单ID获取子订单ID
    order_all_detail = get_order_shop_id(order_all_id=order_all_id)
    for data in order_all_detail:
        for shop_name, order_shop_id in data.items():
            # 子订单发货
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
        "pageSize": 10,  # 每页数量
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
        "receiving": 'true'  # false: 所有商品 true：未收货商品
    }

    request = common.req.request_post(token=token, url='/store/api/order/getLogistics', body=body)

    logistics_code_list = []

    for data in request['data']['logisticsListRespVOS']:
        logistics_code = data['logisticsCode']
        logistics_code_list.append(logistics_code)

    return logistics_code_list


def goods_receiving(token, order_all_id=None):
    """
    确认收货
    :param order_all_id: None: 获取所有未收货订单 并全部收货  not None:确认收货指定的订单
    :param token: 用户token
    :return:
    """

    if order_all_id is not None:

        # 获取主订单下的物流单号
        logistics_list = get_logistics(token=token, order_all_id=order_all_id)

        if len(logistics_list) > 0:
            receive_function(token, logistics_list, order_all_id)
        else:
            print(f"订单【{order_all_id}】没有待收货的物流信息")

    else:
        # 获取已发货订单
        not_sign_order_all_id = get_order_all_id(token=token)

        # 遍历所有未发货订单
        for order_all_id in not_sign_order_all_id:

            # 获取订单下的物流单号
            logistics_list = get_logistics(token=token, order_all_id=order_all_id)

            if len(logistics_list) > 0:
                receive_function(token, logistics_list, order_all_id)
            else:
                print(f"订单【{order_all_id}】没有待收货的物流信息")


def receive_function(token, logistics_list, order_all_id):
    """
    确认收货方法
    :param token:
    :param logistics_list:
    :param order_all_id:
    :return:
    """

    url = '/store/api/order/userReceiving'

    # 定义请求参数
    body = {'logisticsCode': logistics_list,
            'orderCode': order_all_id}

    # 调用确认收货接口
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
    # order_all_list = [1370757844571299842,
    #                   1370757840767066113,
    #                   1370757836853780481,
    #                   1370757828930740226,
    #                   1370757832659476482,
    #                   1370757824988094465,
    #                   1370757821049643009,
    #                   1370757817383821314,
    #                   1370757813680250881,
    #                   1370757809444003841,
    #                   1370757805732044801,
    #                   1370757801919422466,
    #                   1370757798471704577,
    #                   1370757791026814978,
    #                   1370757794751356929,
    #                   1370757787084169218,
    #                   1370757783233798145,
    #                   1370757779433758721,
    #                   1370757775637913601,
    #                   1370757771980480513,
    #                   1370757768063000577,
    #                   1370757764342652930,
    #                   1370757760987209729,
    #                   1370757753299050498,
    #                   1370757757111672833,
    #                   1370757749457068033,
    #                   1370757745292124161,
    #                   1370757741743742977,
    #                   1370757738027589634,
    #                   1370757734399516674,
    #                   1370757730897272834,
    #                   1370757727365668865,
    #                   1370757720285683713,
    #                   1370757723800510466,
    #                   1370757716816994306,
    #                   1370757713134395393,
    #                   1370757709292412929,
    #                   1370757705345572865,
    #                   1370757702094987266,
    #                   1370757695006613506,
    #                   1370757698458525698,
    #                   1370757691336597505,
    #                   1370757687595278337,
    #                   1370757683707158529,
    #                   1370757679886147586,
    #                   1370757676362932225,
    #                   1370757672797773826,
    #                   1370757668922236929,
    #                   1370757661083082753,
    #                   1370757664727932930,
    #                   1370755359790112770,
    #                   1370755355495145473,
    #                   1370755351468613634,
    #                   1370755347492413442,
    #                   1370755343168086017,
    #                   1370755338545963010,
    #                   1370755334427156482,
    #                   1370755330241241089,
    #                   1370755325967245313,
    #                   1370755321651306498,
    #                   1370755316991434754,
    #                   1370755312675495938,
    #                   1370755308418277378,
    #                   1370755304203001858,
    #                   1370755299836731393,
    #                   1370755295550152706,
    #                   1370755291137744897,
    #                   1370755286972801026,
    #                   1370755282795274241,
    #                   1370755278491918337,
    #                   1370755273978847233,
    #                   1370755269159591937,
    #                   1370755264810098689,
    #                   1370755260582240258,
    #                   1370755256434073601,
    #                   1370755252118134785,
    #                   1370755247827361793,
    #                   1370755243310096385,
    #                   1370755238939631618,
    #                   1370755234258788353,
    #                   1370755230458748929,
    #                   1370755226323165185,
    #                   1370755221956894721,
    #                   1370755217301217281,
    #                   1370755213178216449,
    #                   1370755208950358017,
    #                   1370755204483424258,
    #                   1370755199978741762,
    #                   1370755195822186498,
    #                   1370755191590133761,
    #                   1370755187328720898,
    #                   1370755183167971329,
    #                   1370755178596179970,
    #                   1370755174372515841,
    #                   1370755170043994114,
    #                   1370755165736443906,
    #                   1370755161282093057,
    #                   1370755157050040322,
    #                   1370755152469860353,
    #                   1370755148049063938]
    # for order_all_id in order_all_list:
    #     order_all_delivery(order_all_id=order_all_id)
    #     time.sleep(0.2)

    # 确认收货
    # user_token = search_order_account(order_all_id=1370708910620553217)
    # goods_receiving(token=user_token, order_all_id=1370708910620553217)

    # 所有订单确认收货
    user_token = common.user_token(19216850028)
    goods_receiving(token=user_token, order_all_id=None)
    # print(get_order_all_id(token=user_token))
