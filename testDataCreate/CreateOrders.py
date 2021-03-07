# -*- coding: utf-8 -*-
# @Time: 2021/2/23 19:41
# @Author: Waipang

import common
import time
import csv
from testDataCreate import Address
from testDataCreate import UserMoney


def pay_password_check(token):
    set_info = common.req.request_get(url='/store/api/account/set-info', token=token)
    has_pay_password = set_info['data']['hasPayPass']
    if has_pay_password is True:
        return
    else:
        # 获取当前账户手机号
        get_mobile = common.req.request_get(url='/store/api/account/userinfo', token=token)
        mobile = get_mobile['data']['mobile']

        # 提交修改密码手机验证码, 获取修改密码的token
        sms_code_valid = common.req.request_get(url='/store/common/sms/valid',
                                                token=token,
                                                params={'mobile': mobile,
                                                        'type': 'SET_PAY_PWD',
                                                        'code': 111111})
        set_password_token = sms_code_valid['data']

        # 设置支付密码
        set_password_body = {
            'codeToken': set_password_token,
            'password': 123456
        }

        common.req.request_post(url='/store/api/account/pay/set-pass', token=token, body=set_password_body)


def get_default_addr(token):
    try:
        request = common.req.request_get(url='/store/api/user/addr/address/default', token=token)
        addr_id = request['data']['id']
        province_id = request['data']['provinceId']
    except TypeError:
        addr_id, province_id = Address.add_address(token=token)

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


def create_order(token, order_source, coupon_auto_use=0, need_pause=0, buy_num=None, sku_id=None,
                 spu_id=None, activity_type=None, activity_id=None,
                 coupon_id=None, half_id=None, full_reduction_id=None,
                 share_dynamic_id=None, share_user_id=None, save_data=None):
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
    :param need_pause: 提交订单前暂停(回车继续)
    :param save_data: 是否返回提交订单所需的数据
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
    elif coupon_auto_use == 0 and coupon_id is None:
        body['isUseCoupon'] = 'false'

    addr_id, province_id = get_default_addr(token)
    body['provinceId'] = province_id

    # 获取订单结算信息
    discounts_info = common.req.request_post(url='/store/api/order/getSettleDiscountsInfo',
                                             body=body,
                                             token=token)
    print(f"""
    【获取订单结算信息】(/store/api/order/getSettleDiscountsInfo)
    请求信息
    {body}

    返回信息
    {discounts_info['text']}
    """.replace("'", '"').replace('None', 'null'))

    # 获取商品结算信息
    goods_info = common.req.request_post(url='/store/api/order/getSettleGoodsInfo',
                                         body=body,
                                         token=token)
    print(f"""
    【获取商品结算信息】(/store/api/order/getSettleGoodsInfo)
    请求信息
    {body}

    返回信息
    {goods_info['text']}
    """.replace("'", '"').replace('None', 'null'))

    # 提交订单前的数据处理操作
    # 购物车方式走以下处理
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

    # 在提交参数中删除省份ID,并添加收货地址
    del body['provinceId']
    body['userAddressId'] = addr_id

    # 获取结算页返回的优惠券
    if coupon_auto_use == 1:
        body['couponId'] = discounts_info['data']['couponId']
        body['isUseCoupon'] = 'true'
    else:
        pass

    # 判断是否需要在提交订单之前中止
    if need_pause == 1:
        print(str(body).replace("'", '"'))
        a = int(input('1:继续提交订单\n'))
        if a == 1:
            pass
        else:
            return

    # 获取管理后台token
    # admin_token = common.admin_token()

    # 修改用户可提现余额/臻宝/活动余额(manual: 0:直接充值可提现余额, 1:手动输入)
    # UserMoney.update_user_money(token=admin_token, mobile=18123929299, update_type=1, money=10, money_type=1)

    # 判断是否储存提交订单数据
    if save_data == 1:
        return token, body
    else:
        pass

    # 提交订单
    confirm_order = common.req.request_post(url='/store/api/order/confirmOrder',
                                            body=body,
                                            token=token)

    print(f"""
    【提交订单】(/store/api/order/confirmOrder)
    请求信息
    {body} 

    返回信息
    {confirm_order['text']}
    """.replace("'", '"').replace('None', 'null'))
    # 取出提交订单接口返回的价格和订单ID
    try:
        price = confirm_order['data']['price']
        order_id = confirm_order['data']['orderCode']
    except TypeError:
        print('支付接口所需数据获取失败')
        return

    # 判断是否需要在提交订单之前中止
    if need_pause == 1:
        b = int(input('1:继续支付\n'))
        if b == 1:
            pass
        else:
            return

    # 调用支付接口
    order_pay(price=price, order_id=order_id, token=token)


def batch_order_rand_create(token, num):
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

    a = 1

    for result in select:
        print(f'===========================第{a}次创建订单===========================')
        sku_id = result[0]
        spu_id = result[1]
        create_order(token=token, buy_num=1, spu_id=spu_id, sku_id=sku_id, coupon_auto_use=1, order_source=2)
        a += 1
        print(f'===================================================================')


def order_pay(price, order_id, token):
    pay_password_check(token=token)
    body = {
        "balancePayAmount": price,
        "orderId": order_id,
        "paymentPassword": "123456",
        "thirdPartyPayAmount": 0,
        "type": 0
    }

    pay = common.req.request_post(url='/store/api/trade/pay', token=token, body=body)

    print(f"""
    【订单支付】(/store/api/trade/pay)
    请求：
    {body}

    响应：
    {pay['text']}
    """)
    # time.sleep(0.5)


if __name__ == '__main__':

    # 登录用户账号,并获取token
    user_token = common.user_token(mobile=18123929299)

    for i in range(1):
        print(f'====================第{i + 1}次执行开始=======================')

        # 立即购买(普通/臻宝/VIP商品订单)
        # create_order(token=user_token, buy_num=1, sku_id=1366289834708074498, spu_id=1366289834699685889,
        #              order_source=2, coupon_auto_use=1, need_pause=1)

        # 创建随机批量订单
        # batch_order_rand_create(token=user_token, num=1)  # 创建单商品订单

        # 创建拼团订单
        # create_order(token=user_token, buy_num=1, sku_id=1353289208831176706,
        #              order_source=1, activity_type=0, activity_id=1368103269305434114, need_pause=0)

        # 创建限时抢购订单
        # create_order(token=user_token, buy_num=1, sku_id=1352097292064174082,
        #              order_source=1, activity_type=1, activity_id=1368102945052180481)

        # 购物车商品创建订单
        create_order(token=user_token, order_source=0, need_pause=0)

        print(f'====================第{i + 1}次执行结束=======================')
        pass

    #   多账号创建订单
    # common.account.user_login(source=1)
    # user_token_list = common.account.get_user_token()
    # for data in user_token_list:
    #     batch_order_rand_create(token=data[1], num=2)

    #   生成压测提交订单接口的数据
    #   登录多个用户账号,并获取token
    # common.account.user_login(source=1)
    # user_token_list = common.account.get_user_token()
    #
    # file = common.get_file_path('stress_testing.csv', 'test_file')
    # with open(file, 'w', newline='', encoding='utf-8') as StressTest:
    #     csv_file_writer = csv.writer(StressTest)
    #     csv_file_writer.writerow(['token', 'body'])
    #     for data in user_token_list:
    #         token1, body = create_order(token=data[1], save_data=1, buy_num=1, sku_id=1353288833893953537,
    #                                     order_source=1, activity_type=1, activity_id=1368102945052180481)
    #         new_body = str(body).replace("'", '"').replace("None", 'null')
    #         csv_file_writer.writerow([token1, new_body])
