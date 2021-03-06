# -*- coding: utf-8 -*-
# @Time: 2021/3/7 16:17
# @Author: Waipang

import common
import csv


def order_shop_delivery(order_shop_id, logistics_name='京东物流', logistics_code='JD0036682565810'):
    """
    子订单发货
    :param logistics_code: 快递单号
    :param logistics_name: 物流公司
    :param order_shop_id: 子订单ID
    :return:
    """

    # 获取商家名称
    shop_name = get_shop_name(order_shop_id=order_shop_id)

    # 商家登录
    shop_token = common.shop_token(shop_name)

    # 遍历未发货商品,分别调用接口请求
    shop_order_delivers_goods = get_shop_order_delivers_goods(token=shop_token,
                                                              order_shop_id=order_shop_id,
                                                              logistics_name=logistics_name,
                                                              logistics_code=logistics_code)

    # 判断是否存在未发货的商品,没有则返回
    if len(shop_order_delivers_goods) == 0:
        print(f'商家【{shop_name}】当前订单(order_shop_id: {order_shop_id})没有待发货的商品')
        return

    # 定义发货请求参数, 并调用发货接口
    body = {'orderDeliverRespVOS': shop_order_delivers_goods}

    request = common.req.request_post(url='/store/seller/order/upStatusDeliver',
                                      body=body,
                                      token=shop_token)
    common.api_print(name=f'供应商-{shop_name}发货', url=request['url'], data=body, result=request)


def get_shop_order_delivers_goods(token, order_shop_id, logistics_name='京东物流', logistics_code='JD0036682565810'):
    """
    获取未发货的商品, 包装成发货接口所需数据结构后返回
    :param logistics_code: 物流单号
    :param logistics_name: 物流公司名称
    :param token: 商家token
    :param order_shop_id: 子订单Id
    :return:
    """
    request = common.req.request_post(url='/store/seller/order/getShopOrderDeliverGoods',
                                      token=token,
                                      params={'shopOrderId': order_shop_id})
    order_goods_list = []
    logistics_name_value, logistics_code_value, logistics_name_code = get_logistics_info(
        logistics_name=logistics_name, logistics_code=logistics_code)
    # 遍历接口返回的商品信息,依次写入order_goods_list列表中
    for goods in request['data']:
        order_goods_list.append({
            'mainOrderCode': goods['mainOrderCode'],  # 主订单ID
            'shopOrderCode': goods['shopOrderCode'],  # 子订单ID
            'id': goods['id'],  # 商品订单ID
            "logisticsName": logistics_name_value,  # 物流公司
            "logisticsCode": logistics_code_value,  # 运单编号
            "logisticsNameCode": logistics_name_code,  # 物流公司编号
            'nowDeliverCount': goods['remainCount'],  # 发货数量
        })

    return order_goods_list


def get_shop_name(order_shop_id):
    """
    根据子订单ID查询商家名称
    :param order_shop_id: 子订单ID
    :return:
    """
    result = common.db.select_one(sql=f"""
    SELECT username from user_account where id = (
    SELECT
        shop_info.account_id
    FROM
        order_goods
        LEFT JOIN shop_info ON shop_info.id = order_goods.shop_id
    WHERE
        order_shop_id = '{order_shop_id}' limit 1)
    """)

    shop_name = result[0]

    return shop_name


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
    GROUP BY order_goods.order_shop_id
    """)

    order_shop_id_list = []

    # 遍历查询到的结果,把子订单ID和商家名称写入列表中
    for data in result:
        order_shop_id = data[0]
        shop_name = data[1]
        # 如果列表中不存在对应商家的字典,则添加字典并写入
        order_shop_id_list.append({
            shop_name: order_shop_id
        })

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
    common.api_print(name='确认收货', url=request['url'], data=body, result=request)


def form_file_get_order_shop():
    file_path = common.get_file_path(file_name='order_shop_ship_data.csv', parent_path='test_file')
    with open(file_path, 'r', encoding='utf-8') as OrderAll:
        order_all = csv.reader(OrderAll)
        next(order_all)
        data_list = []
        for data in order_all:
            order_shop = data[0]
            logistics_code = data[1]
            logistics_name = data[2]
            data_list.append({
                'order_shop_id': order_shop,
                'logistics_code': logistics_code,
                'logistics_name': logistics_name
            })
        return data_list


def batch_delivery():
    """
    供应商批量发货
    :return:
    """
    order_shop_ship_data_list = form_file_get_order_shop()
    for order_shop_data in order_shop_ship_data_list:
        order_shop_id = order_shop_data['order_shop_id']
        logistics_code = order_shop_data['logistics_code']
        logistics_name = order_shop_data['logistics_name']
        # 子订单发货
        print(order_shop_id, logistics_code, logistics_name)
        # order_shop_delivery(order_shop_id=order_shop_id, logistics_code=logistics_code, logistics_name=logistics_name)


def get_logistics_info(logistics_name, logistics_code):
    """
    获取物流公司编号
    :param logistics_name: 物流公司
    :param logistics_code: 物流单号
    :return:
    """
    logistics_com_dic = {
        '圆通速递': 'yuantong',
        '顺丰速运': 'shunfeng',
        '韵达快递': 'yunda',
        '中通快递': 'zhongtong',
        '邮政快递包裹': 'youzhengguonei',
        '京东物流': 'jd',
        '申通快递': 'shentong',
        '百世快递': 'huitongkuaidi',
        'EMS': 'ems',
        '极兔速递': 'jtexpress',
        '邮政标准快递': 'youzhengbk',
        '德邦': 'debangwuliu',
        '德邦快递': 'debangkuaidi',
        '百世快运': 'baishiwuliu',
        '宅急送': 'zhaijisong',
        '天天快递': 'tiantian',
        '圆通快运': 'yuantongkuaiyun',
        '优速快递': 'youshuwuliu',
        '韵达快运': 'yundakuaiyun',
        'D速快递': 'dsukuaidi',
        '联昊通': 'lianhaowuliu'
    }

    logistics_name_code = logistics_com_dic[logistics_name]
    return logistics_name, logistics_code, logistics_name_code


def finish_order(token, order_id):
    body = {
        "orderCode": order_id
    }
    request = common.req.request_post(url='/store/api/order/CSFinishOrder', token=token, body=body)
    common.api_print(name='手动完成订单', url=request['url'], data=body, result=request)


if __name__ == '__main__':

    "子订单发货"
    # order_shop_delivery(order_shop_id=1396715867231780866, logistics_code='4313855422819', logistics_name='韵达快递')

    "批量发货"
    # batch_delivery()

    order_all_ids = [
        1397113366492745729
    ]
    user_token = common.user_token(18123929299)
    for i in order_all_ids:
        "主订单发货"
        order_all_delivery(order_all_id=i)

        "确认收货"
        # goods_receiving(token=user_token, order_all_id=i)

        "完成订单"
        # finish_order(token=user_token, order_id=i)
