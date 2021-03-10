# -*- coding: utf-8 -*-
# @Time: 2021/2/2 19:35
# @Author: Waipang

import common
from datetime import datetime, timedelta
import random
import csv


def get_category(num=5):
    """
    随机获取十个三级分类
    :return: 分类字符串
    """
    result = common.db.select_all(sql=f"""
    SELECT
        id
    FROM
        goods_category
    WHERE 
        level = 3
    ORDER BY RAND()
    LIMIT {num}
    """)
    category_detail = ''
    for category in result:
        category_id = category[0]
        category_detail += str(category_id) + ','
    return category_detail[:-1]


def get_goods(num=30):
    """
    随机获取十个sku
    :return: sku字符串
    """
    result = common.db.select_all(sql=f"""
    SELECT
        sku.id AS 'skuId'
    FROM
        goods_sku sku
        left join goods_spu spu ON spu.id = sku.goods_id
    WHERE
        spu.audit_status  = 1
    AND	spu.status = 3
    AND spu.type = 0   
        ORDER BY RAND()
    LIMIT {num}
        """)

    goods_detail = ''
    for goods in result:
        sku_id = goods[0]
        goods_detail += str(sku_id) + ','
    return goods_detail[:-1]


def coupon_create(vip=None):
    """
    添加优惠券
    :return:
    """
    time_type = int(input('时间类型(0: 固定时间, 1: 相对时间): \n'))
    coupon_type = int(input('获取方式(0: 商品详情页领取, 1: VIP赠送到账, 2: 注册赠送到账, 3: 后台发放): \n'))
    use_scope = int(input('使用范围(0: 全品, 1: 分类, 2: 商品): \n'))

    coupon_price = random.randint(10, 30)
    coupon_threshold_price = random.randint(40, 100)
    # coupon_price = int(input('请输入优惠券金额:\n'))
    # coupon_threshold_price = int(input('请输入优惠券门槛:\n'))

    body = {
        "title": f"{coupon_price}元优惠券（满{coupon_threshold_price}元可用）",
        "couponPrice": coupon_price,
        "couponThresholdPrice": coupon_threshold_price,
        "scopeDescription": "优惠券使用范围描述",
        "activityDescription": "优惠券描述",
        "useScope": use_scope,
        "type": coupon_type
    }

    # 优惠券时间类型
    if time_type == 1:
        # 相对时间, 时间长度为7天
        body['timeType'] = 1
        body['timeValue'] = 7

    elif time_type == 0:
        # 固定时间, 开始时间为当前时间+1分钟, 结束时间为当前时间+7天
        now = datetime.now()
        start_time = (now + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
        end_time = (now + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
        body['timeType'] = 0
        body['startTime'] = start_time
        body['endTime'] = end_time

    else:
        print('时间类型有误')
        return

    # 优惠券获取方式
    if coupon_type == 0:
        # 商品详情页获取, 默认限领数量为1, 发放数量为100
        body['userType'] = 0 if vip is None else 1
        body['createNum'] = 10
        body['limitNum'] = 1

    # 优惠券使用范围
    if use_scope == 0:
        # 全品
        body['scopeId'] = 0

    elif use_scope == 1:
        # 部分分类
        body['scopeId'] = get_category()

    elif use_scope == 2:
        # 部分商品
        body['scopeId'] = get_goods()

    common.account.admin_login()
    admin_token = common.account.get_admin_token()
    print(str(body).replace("'", '"'))
    request = common.req.request_post(url='/store/manage/promotion/coupon/addSaveCoupon',
                                      token=admin_token,
                                      body=body)
    data = request['data']

    print(f"""
    【优惠券创建成功】
    标题: {data['title']}
    金额: {data['couponPrice']}元
    门槛: {data['couponThresholdPrice']}元
    开始时间: {data['startTime']}
    结束时间: {data['endTime']}
    获取方式: {data['type']}
    适用范围: {data['useScope']}
    使用详情（分类/商品ID）: {body['scopeId']}
    """)


def receive_coupon(token, coupon_id, save_data=None):
    url = f'/store/api/promotion/member-coupon/{coupon_id}/receive'
    request = common.req.request_get(url=url, token=token)

    if save_data == 1:
        return token, url

    print(request['text'])


if __name__ == '__main__':
    # 优惠券创建
    # while 1:
    #     coupon_create()
    user_token = common.user_token(15295993410)

    coupon_list = [1369620430599606273,
                   1369620419635695617,
                   1369620413277130753,
                   1369620405786103809,
                   1369620399519813633,
                   1369620392930562050,
                   1369620386211287041,
                   1369620380377010178,
                   1369620368419049474,
                   1369620359325798402,
                   1369620354850476033,
                   1369620349955723266,
                   1369620246041841666,
                   1369620241457467394,
                   1369620236785012738,
                   1369620232175472642,
                   1369620227339440130,
                   1369620222666985473,
                   1369620218036473858,
                   1369620212164448258,
                   1369620207236141058,
                   1369620202521743361,
                   1369620197715070977,
                   1369620193189416962,
                   1369620188214972417,
                   1369620183538323457,
                   1369620178496770049,
                   1369620173606211585,
                   1369620168942145537,
                   1369620163888009217,
                   1369620158468968450,
                   1369620152538222594,
                   1368812996960305154,
                   1368812949006827522,
                   1368812827028078593,
                   1356418215324213249,
                   1356229435497701378,
                   1356229265875853314,
                   1356226697401524225,
                   1354352442908610561,
                   1354351655771967489,
                   1354350616423436289,
                   1348461351852650498,
                   1347719933488033794]

    for i in coupon_list:
        receive_coupon(token=user_token, coupon_id=i)

    # 生成压测数据
    # common.account.user_login(source=1)
    # user_token_list = common.account.get_user_token()
    # file = common.get_file_path('batch_receive_coupon.csv', 'test_file')
    # with open(file, 'w', newline='', encoding='utf-8') as StressTest:
    #     csv_file_writer = csv.writer(StressTest)
    #     csv_file_writer.writerow(['token', 'url'])
    #     for data in user_token_list:
    #         token1, body = receive_coupon(token=data[1], save_data=1, coupon_id=1367814438450647041)
    #         new_body = str(body).replace("'", '"')
    #         csv_file_writer.writerow([token1, new_body])
