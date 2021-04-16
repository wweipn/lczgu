# -*- coding: utf-8 -*-
# @Time: 2021/2/23 19:41
# @Author: Waipang

import common
from testDataCreate import Address
from datetime import datetime
import random


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


def create_cart_data(token, num=10, buy_num=1, sku_tuple=None):
    condition = f'AND sku.id IN {sku_tuple}' if sku_tuple is not None else ''
    result = common.db.select_all(sql=f"""
    SELECT
        sku.id AS 'sku_id'
    FROM
        goods_sku sku
        left join goods_spu spu ON spu.id = sku.goods_id
    WHERE
        spu.audit_status  = 1 -- 审核状态 0：待审核，1：审核通过，2：审核拒绝；
        AND	spu.status = 3 -- '商品状态 3：上架；4：下架'
        AND spu.type = 0 -- '商品类型 0:普通商品;1:臻宝商品;2.VIP商品'
        AND spu.is_deleted = 0
        {condition}
    LIMIT {num}
    """)

    for data in result:
        sku_id = data[0]

        body = {
            "buyNum": buy_num,
            "skuId": sku_id
        }

        half_price_id, full_reduction_id = search_promotions(sku_id=sku_id)
        if half_price_id is not None:
            body['halfId'] = half_price_id
        if full_reduction_id is not None:
            body['fullReductionId'] = full_reduction_id

        common.req.request_post(url='/store/api/order-shopping-cart',
                                token=token,
                                body=body)


def search_promotions(sku_id):
    request = common.req.request_get(url='/store/api/promotion/goods/queryPromotionGoods',
                                     params={'skuId': sku_id})
    half_price_id = None
    full_reduction_id = None

    for detail in request['data']:
        try:
            if detail['type'] == 0:
                half_price_id = detail['id']
            elif detail['type'] == 1:
                full_reduction_id = detail['id']
        except TypeError:
            return None, None

    return half_price_id, full_reduction_id


def set_password(mobile, token):
    """
    设置支付密码
    :param mobile:
    :param token:
    :return:
    """
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


def create_order(token, order_source, coupon_auto_use=0, need_pause=0, buy_num=None, sku_id=None, spu_id=None,
                 team_id=None, activity_type=None, activity_id=None,
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
    :param team_id: 拼团团队Id,参团用
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
            print('购物车没有商品')
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
        if team_id is not None and activity_type == 0:
            body['settleActivityReqVO']['teamId'] = team_id
    # 立即购买
    elif order_source == 2:
        body['orderSettleBuyNowReqVO'] = {
            'buyNum': buy_num,
            'skuId': sku_id,
            'spuId': spu_id,
            'remark': ''
        }
        # 判断是否有传半价ID或者满减ID
        if half_id or full_reduction_id is not None:
            # 判断是否有传半价ID
            if half_id is not None:
                body['orderSettleBuyNowReqVO']['halfId'] = half_id
            # 判断是否有传满减ID
            if full_reduction_id is not None:
                body['orderSettleBuyNowReqVO']['fullReductionId'] = full_reduction_id

        # 如果半价ID和满减ID都没有传的话,自动获取优惠
        else:
            half_id, full_reduction_id = search_promotions(sku_id=sku_id)
            if half_id is not None:
                body['orderSettleBuyNowReqVO']['halfId'] = half_id
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

    # 多出来的配置
    # body['provinceId'] = province_id

    # 获取订单结算信息
    discounts_info = common.req.request_post(url='/store/api/order/getSettleDiscountsInfo',
                                             body=body,
                                             token=token)

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

    try:
        goods_total = discounts_info['data']['goodsTotal']  # 商品合计
        total_dis = discounts_info['data']['totalDis'] if discounts_info['data']['totalDis'] is not None else 0  # 优惠合计
        activity_red = discounts_info['data']['activityAccount']  # 活动余额抵扣
        coupon_red = discounts_info['data']['coupon'] if discounts_info['data']['coupon'] is not None else 0  # 优惠券抵扣
        coupon_id = discounts_info['data']['couponId']  # 优惠券ID
        freight = discounts_info['data']['freight']  # 运费
        zbs = discounts_info['data']['zbs'] if discounts_info['data']['zbs'] is not None else 0  # 臻宝抵扣
        total = discounts_info['data']['allTotal']  # 合计
        result = round((goods_total + freight) - total_dis - activity_red - coupon_red, 2)  # 计算出来的金额
        print(f"""
    【获取订单结算信息】(/store/api/order/getSettleDiscountsInfo)
    请求信息
    {body}

    返回信息
    {discounts_info['text']}

    =======价格信息=======
    商品合计: {goods_total}
    折扣优惠: {total_dis}
    活动余额抵扣: {activity_red}
    优惠券减免金额: {coupon_red}
    优惠券ID: {coupon_id}
    运费: {freight}
    臻宝兑换: {zbs}
    合计: {total}(计算结果:{result})
    =====================
            """.replace("'", '"').replace('None', 'null'))
    except TypeError:
        print(f"""
    【获取订单结算信息】(/store/api/order/getSettleDiscountsInfo)
    请求信息
    {body}

    返回信息
    {discounts_info['text']}
        =====================
            """.replace("'", '"').replace('None', 'null'))

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
        create_order(token=token, buy_num=3, spu_id=spu_id, sku_id=sku_id, coupon_auto_use=1, order_source=2)
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


def get_ran_goods(goods_type):
    """
    随机获取一个商品
    :param goods_type: 商品类型 0:普通商品 1:臻宝商品 2.VIP商品
    :return:
    """
    result = common.db.select_one(sql=f"""
    SELECT
        sku.id AS 'skuId',
        spu.id AS 'spuId'
    FROM
        goods_sku sku
        LEFT JOIN goods_spu spu ON spu.id = sku.goods_id 
    WHERE	
        spu.audit_status = 1 -- 审核状态 0：待审核，1：审核通过，2：审核拒绝；
        AND spu.STATUS = 3 -- '商品状态 3：上架；4：下架'
        AND spu.type = {goods_type} -- '商品类型 0:普通商品;1:臻宝商品;2.VIP商品'
        AND spu.is_deleted = 0 -- 非逻辑删除状态
    ORDER BY rand( ) -- 随机排序
    LIMIT 1
    """)

    skuId = result[0]
    spuId = result[1]
    return skuId, spuId


def get_assemble_sku():
    url = '/store/api/promotion/pintuan/queryAppPintuan'
    date = datetime.now().strftime('%Y-%m-%d')
    params = {
        'startTime': date,
        'currentPage': 1,
        'pageSize': 30
    }

    # 获取今天的拼团商品列表
    request = common.req.request_get(url=url, params=params)

    if len(request['data']['data']) == 0:
        print('拼团商品列表为空')
        return

    else:
        # 随机获取列表中其中一个拼团商品
        ran_int = random.randint(0, int(len(request['data']['data'])) - 1)

        # 取出其中一个拼团商品的skuId和活动Id
        skuId = int(request['data']['data'][ran_int]['skuId'])
        ActivityId = int(request['data']['data'][ran_int]['pintuanId'])
        return skuId, ActivityId


def get_promotion_time_line():
    """
    获取进行中限时抢购活动的日期和时间段
    :return:
    """

    url = '/store/api/promotion/time-limit/time-line'
    request = common.req.request_post(url=url)

    # 取出最前面的活动,判断状态是否为进行中
    try:
        status = request['data'][0]['status']
        if status == 2:
            start_time = request['data'][0]['startTime'][-8:]
            endTime = request['data'][0]['endTime'][-8:]
            date = datetime.now().strftime('%Y-%m-%d')
            time_line = f'{start_time}-{endTime}'
            return date, time_line
    except IndexError:
        return 400


def get_promotion_sku():
    """
    获取限时抢购SKU
    :return:
    """

    url = '/store/api/promotion/time-limit/queryAppTimeLimit'

    date, time_line = get_promotion_time_line()
    params = {
        'startTime': date,
        'timeLine': time_line,
        'currentPage': 1,
        'pageSize': 30
    }

    # 获取最新的限时抢购商品列表
    request = common.req.request_get(url=url, params=params)

    # 随机获取列表中其中一个限时抢购商品
    ran_int = random.randint(1, int(len(request['data']['data'])))

    # 取出其中一个限时抢购商品的skuId和活动Id
    skuId = request['data']['data'][ran_int]['skuId']
    ActivityId = request['data']['data'][ran_int]['seckillId']
    return skuId, ActivityId


def create_promotion_order(token, buy_num, need_pause=0, sku_id=None, activity_id=None):
    """
    创建限时抢购活动订单
    :param token:
    :param buy_num: 购买数量
    :param need_pause: 是否暂停
    :param sku_id: 规格ID
    :param activity_id: 活动ID
    :return:
    """
    if sku_id is None and activity_id is None:
        try:
            sku_id, activity_id = get_promotion_sku()
        except TypeError:
            print('没有进行中的限时抢购活动')

    create_order(token=token, buy_num=buy_num, order_source=1, activity_type=1, need_pause=need_pause,
                 sku_id=sku_id, activity_id=activity_id)


def create_assemble_order(token, buy_num, need_pause=0, sku_id=None, activity_id=None, team_id=None):
    """
    创建拼团活动订单
    :param token: token
    :param buy_num: 购买数量
    :param need_pause: 是否暂停
    :param sku_id: 规格ID
    :param activity_id: 活动ID
    :param team_id: 团队ID
    :return:
    """

    if sku_id is None and activity_id is None:
        try:
            sku_id, activity_id = get_assemble_sku()
        except TypeError:
            print('没有进行中的拼团活动')

    create_order(token=token, buy_num=buy_num, order_source=1, activity_type=0, need_pause=need_pause, team_id=team_id,
                 sku_id=sku_id, activity_id=activity_id)


def create_buy_now_order(goods_type, buy_num, coupon_auto_use=0, need_pause=0, sku_id=None, spu_id=None, share_dynamic_id=None, share_user_id=None):
    """
    创建立即购买订单
    :param goods_type: 商品类型 0:普通商品 1:臻宝商品 2.VIP商品
    :param buy_num: 购买数量
    :param spu_id: 规格ID
    :param sku_id: 商品ID
    :param need_pause: 是否暂停
    :param coupon_auto_use: 自动使用优惠券
    :return:
    """

    if sku_id is None and spu_id is None:
        sku_id, spu_id = get_ran_goods(goods_type=goods_type)

    create_order(token=user_token, buy_num=buy_num, order_source=2, coupon_auto_use=coupon_auto_use,
                 sku_id=sku_id, spu_id=spu_id, share_dynamic_id=share_dynamic_id, share_user_id=share_user_id, need_pause=need_pause)


if __name__ == '__main__':

    # 登录用户账号,并获取token
    user_token = common.user_token(mobile=19216850033)
    # 随机获取商品
    # goods_type: 商品类型 0:普通商品 1:臻宝商品 2.VIP商品
    # sku_id, spu_id = get_ran_goods(goods_type=0)

    for i in range(1):
        # print(f'====================第{i + 1}次执行开始=======================')
        # 立即购买(0:普通商品 1:臻宝商品 2.VIP商品)
        create_buy_now_order(goods_type=0, buy_num=1, coupon_auto_use=0, need_pause=0,
                             sku_id=None, spu_id=None,
                             share_dynamic_id=None, share_user_id=None)

        # 创建随机批量订单
        # batch_order_rand_create(token=user_token, num=5)  # 创建单商品订单

        # 创建拼团订单
        # create_assemble_order(token=user_token, buy_num=1, need_pause=0, sku_id=1370631952964534273,
        #                       activity_id=1382607056850137089, team_id=1382608340495904769)

        # 创建限时抢购订单
        # create_promotion_order(token=user_token, buy_num=5, need_pause=0,
        #                        sku_id=1352086062821847042, activity_id=1379242091527393281)

        # 生成购物车数据
        # data = '(1369128929847152642,1369128930027507713)'
        # create_cart_data(token=user_token, num=2, buy_num=1, sku_tuple=data)
        # 购物车商品创建订单
        # create_order(token=user_token, order_source=0, need_pause=0, coupon_auto_use=1)

        # print(f'====================第{i + 1}次执行结束=======================')
        pass

    #   多账号创建订单
    # common.account.user_login(source=1)
    # user_token_list = common.account.get_user_token()
    # for data in user_token_list:
    #     batch_order_rand_create(token=data[1], num=2)

    # 设置支付密码
    # set_password(mobile=15295993410, token=user_token)
