# -*- coding: utf-8 -*-
# @Time: 2021/2/23 19:41
# @Author: Waipang

import common
from testDataCreate import Address
from datetime import datetime
import random


def pay_password_check(token):
    """
    校验是否有设置支付密码, 没有则设为123456
    :param token:
    :return:
    """
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


def get_default_address(token):
    """
    获取默认地址, 没有则随机设置一个
    :param token:
    :return:
    """
    try:
        request = common.req.request_get(url='/store/api/user/addr/address/default', token=token)
        address_id = request['data']['id']
        province_id = request['data']['provinceId']
    except TypeError:
        address_id, province_id = Address.add_address(token=token)

    return address_id, province_id


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


def create_cart_data(token, num=10, buy_num=1, sku_ids=None):
    """
    加入购物车
    :param token: 用户token
    :param num: 购物车商品数量
    :param buy_num: 购买数量
    :param sku_ids: sku_id, 传字符串集合
    :return:
    """
    condition = f'AND sku.id IN ({sku_ids})' if sku_ids is not None else ''
    limit = f'LIMIT {num}' if sku_ids is None else ''
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
    {limit}
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

        common.req.request_post(url='/store/api/order-shopping-cart', token=token, body=body)


def search_promotions(sku_id):
    """
    查询商品是否参加半价/满减活动
    :param sku_id:
    :return:
    """
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
    :param mobile: 手机号
    :param token: 用户token
    :return:
    """
    sms_code_valid = common.req.request_get(url='/store/common/sms/valid', token=token, params={'mobile': mobile,
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
                 share_dynamic_id=None, share_user_id=None):
    """
    创建订单
    :param token: 用户token
    :param buy_num: 购买数量
    :param sku_id: skuId
    :param spu_id: spuId
    :param order_source: 订单入口 0: 购物车, 1: 拼团/限时抢购, 2: 立即购买
    :param coupon_auto_use: 是否默认使用优惠券 0: 否, 1: 是
    :param coupon_id: 优惠券ID
    :param share_dynamic_id: 动态ID
    :param share_user_id:  分享人accountId
    :param half_id: 半价活动ID
    :param full_reduction_id: 满减活动ID
    :param activity_type: 活动类型 0: 拼团, 1: 限时抢购
    :param activity_id: 活动ID
    :param team_id: 拼团团队Id
    :param need_pause: 是否提交订单/支付前暂停
    :return:
    """

    body = {
        'type': order_source
    }

    # 订单入口判断 - 购物车
    if order_source == 0:
        cart_list = get_cart_list(token=token)
        if not cart_list:
            print('购物车为空')
            return
        else:
            body['shoppingCartDisReqVO'] = {"id": cart_list}
    # 订单入口判断 - 活动
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
    # 订单入口判断 - 活动
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

    address_id, province_id = get_default_address(token)
    body['provinceId'] = province_id

    # 获取订单结算信息
    discounts_info = common.req.request_post(url='/store/api/order/getSettleDiscountsInfo',
                                             body=body,
                                             token=token)

    # 获取商品结算信息
    goods_info = common.req.request_post(url='/store/api/order/getSettleGoodsInfo',
                                         body=body,
                                         token=token)
    common.api_print(name='获取商品结算信息', url=goods_info['url'], data=body, result=goods_info)
    common.api_print(name='获取订单结算信息', url=discounts_info['url'], data=body, result=discounts_info)

    # 订单信息打印
    try:
        goods_total = discounts_info['data']['goodsTotal']  # 商品合计
        total_dis = discounts_info['data']['totalDis'] if discounts_info['data']['totalDis'] is not None else 0  # 优惠合计
        activity_red = discounts_info['data']['activityAccount']  # 活动余额抵扣
        need_pay_zhen_bao = discounts_info['data']['needPayZhenBao']  # 臻宝抵扣
        coupon_red = discounts_info['data']['coupon'] if discounts_info['data']['coupon'] is not None else 0  # 优惠券抵扣
        coupon_id = discounts_info['data']['couponId']  # 优惠券ID
        freight = discounts_info['data']['freight']  # 运费
        total = discounts_info['data']['allTotal']  # 合计
        result = round((goods_total + freight) - total_dis - activity_red - coupon_red, 2)  # 计算出来的金额
        discounts_detail = ''
        # 判断返回的优惠明细是否为空,不为空则解析这个列表
        if discounts_info['data']['activityDiscountInfoVOS'] is not None:
            for discount_list in discounts_info['data']['activityDiscountInfoVOS']:
                for discounts_key, discounts_value in discount_list.items():
                    discounts_detail += f'{discounts_value} '
        # print(f"""
        # =======价格信息=======
        # 商品合计: {goods_total}
        # {f'''---------------------------
        # 优惠明细
        # {discounts_detail}''' if discounts_detail != '' else ''}
        # {f'''总优惠: {total_dis}
        # ---------------------------''' if total_dis > 0 else ''}
        # {f'优惠后金额: {goods_total - total_dis}' if total_dis > 0 else ''}
        # {f'活动余额抵扣: {activity_red}, 抵扣比例: {round(activity_red / (goods_total - total_dis) * 100, 2)}%' if activity_red > 0 else ''}
        # {f'臻宝抵扣: {need_pay_zhen_bao}' if need_pay_zhen_bao is not None else ''}
        # {f'优惠券减免金额: {coupon_red}' if coupon_red > 0 else ''}
        # {f'优惠券ID: {coupon_id}' if coupon_id is not None else ''}
        # {f'运费: {freight}' if freight > 0 else ''}
        # 合计: {total}(计算结果:{result})
        # =====================
        # """.replace("'", '"').replace('None', 'null'))

        if discounts_detail != '':
            print(f"""
            优惠明细
            {discounts_detail}
            总优惠: {total_dis}
            优惠后金额: {goods_total - total_dis}
            """)

        if activity_red > 0:
            print(f'''
            活动余额抵扣: {activity_red}, 抵扣比例: {round(activity_red / (goods_total - total_dis) * 100, 2)}%
            ''')

        if need_pay_zhen_bao is not None:
            print(f'臻宝抵扣: {need_pay_zhen_bao}')

        if coupon_red > 0:
            print(f'''
            优惠券减免金额: {coupon_red}
            优惠券ID: {coupon_id}
            ''')
        if freight > 0:
            print(f"""
            运费: {freight}
            """)
    except TypeError:
        print('下单失败')
        return

    # 提交订单前的数据处理

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

    # 删除省份ID,添加收货地址ID
    del body['provinceId']
    body['userAddressId'] = address_id

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

    # 提交订单
    confirm_order = common.req.request_post(url='/store/api/order/confirmOrder', body=body, token=token)
    common.api_print(name='提交订单', url=confirm_order['url'], data=body, result=confirm_order)

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


def order_pay(price, order_id, token):
    """
    订单支付
    :param price: 支付金额
    :param order_id: 主订单ID
    :param token:
    :return:
    """
    pay_password_check(token=token)
    body = {
        "balancePayAmount": price,
        "orderId": order_id,
        "paymentPassword": "123456",
        "thirdPartyPayAmount": 0,
        "type": 0
    }

    pay = common.req.request_post(url='/store/api/trade/pay', token=token, body=body)

    common.api_print(name='订单支付', url=pay['url'], data=body, result=pay)


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
        AND sku.is_deleted = 0 -- 非逻辑删除状态
    ORDER BY rand( ) -- 随机排序
    LIMIT 1
    """)

    sku_id = result[0]
    spu_id = result[1]
    return sku_id, spu_id


def get_assemble_sku():
    """
    获取拼团sku
    :return:
    """
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
        sku_id = int(request['data']['data'][ran_int]['skuId'])
        activity_id = int(request['data']['data'][ran_int]['pintuanId'])
        return sku_id, activity_id


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
            end_time = request['data'][0]['endTime'][-8:]
            date = datetime.now().strftime('%Y-%m-%d')
            time_line = f'{start_time}-{end_time}'
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
    sku_id = request['data']['data'][ran_int]['skuId']
    activity_id = request['data']['data'][ran_int]['seckillId']
    return sku_id, activity_id


def create_activity_order(activity_type, **kwargs):
    """
    创建活动订单
    :param activity_type: 0: 拼团, 1: 限时抢购
    :return:
    """
    if 'sku_id' not in kwargs or 'activity_id' not in kwargs:
        try:
            sku_id, activity_id = get_assemble_sku() if activity_type == 0 else get_promotion_sku()
            create_order(sku_id=sku_id, activity_id=activity_id, order_source=1, activity_type=activity_type, **kwargs)
        except TypeError:
            print(f'没有进行中的{"拼团" if activity_type == 0 else "限时抢购"}活动')
            return
    else:
        create_order(order_source=1, activity_type=activity_type, **kwargs)


def create_buy_now_order(goods_type, **kwargs):
    """
    创建普通订单
    :param goods_type: 商品类型 0:普通商品 1:臻宝商品 2.VIP商品
    :return:
    """

    if 'sku_id' not in kwargs or 'spu_id' not in kwargs:
        sku_id, spu_id = get_ran_goods(goods_type=goods_type)
        create_order(sku_id=sku_id, spu_id=spu_id, order_source=2, **kwargs)

    else:
        create_order(order_source=2, **kwargs)


if __name__ == '__main__':

    "登录用户账号,并获取token"
    user_token = common.user_token(mobile=18123929299)
    # user_token = common.user_token(mobile=19216850009)

    for i in range(1):

        "立即购买(0:普通商品 1:臻宝商品 2.VIP商品)"
        create_buy_now_order(token=user_token, goods_type=0, coupon_auto_use=0, need_pause=1, buy_num=1)

        "创建拼团订单"
        # create_activity_order(token=user_token, activity_type=0, buy_num=1, need_pause=1)

        "创建限时抢购订单"
        # create_activity_order(token=user_token, activity_type=1, buy_num=1, need_pause=0, activity_id=1394202793421680642, sku_id=1370631960673665025)

        "生成购物车数据"
        # data = '(1369128930027507713,1369128970133442562)'
        # create_cart_data(token=user_token, num=2, buy_num=1, sku_tuple=data)
        "购物车商品创建订单"
        # create_order(token=user_token, order_source=0)

    "多账号创建订单"
    # common.account.user_login(source=1)
    # user_token_list = common.account.get_user_token()
    # for data in user_token_list:
    #     batch_order_rand_create(token=data[1], num=2)

    "设置支付密码"
    # set_password(mobile=15295993410, token=user_token)
