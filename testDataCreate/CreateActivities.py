# -*- coding: utf-8 -*-
# @Time: 2021/2/2 10:02
# @Author: Waipang

import common
from datetime import datetime, timedelta


def get_activity_goods(num):
    """
    生成添加活动时所需的商品数据
    :param num: 需要添加的商品数量
    :return:
    """
    result = common.db.select_all(sql=f"""
    SELECT
        sku.id AS 'skuId',
        spu.id AS 'spuId'
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

    goods_list = []

    # 判断查询结果是否为空
    if result:
        for goods in result:
            sku_id = goods[0]
            spu_id = goods[1]
            goods_list.append({"goodsId": spu_id, "skuId": sku_id})
        return goods_list
    else:
        print('商品列表为空')
        return


def half_price_activity(goods_num):
    """
    创建第二件半价活动
    :param goods_num: 需要添加的商品数量
    :return:
    """
    # 管理后台登录
    common.account.admin_login()
    admin_token = common.account.get_admin_token()

    # 获取商品数据
    goods_list = get_activity_goods(goods_num)

    # 定义开始时间和结束时间
    now = datetime.now()
    start_time = (now + timedelta(minutes=1.5)).strftime('%Y-%m-%d %H:%M:%S')
    end_time = (now + timedelta(minutes=2.5)).strftime('%Y-%m-%d %H:%M:%S')

    # 定义请求参数
    body = {
        "name": f"半价活动({start_time})",
        "startTime": start_time,
        "endTime": end_time,
        "goodsList": goods_list
    }

    # 请求创建活动接口
    request = common.req.request_post(url='/store/manage/promotion/half-price/saveHalfPrice',
                                      token=admin_token,
                                      body=body)
    print(body, '\n---------------------------------------\n')
    print(request['text'])


def full_discount(goods_num):
    full_reduction_detail = []
    # 填写满减活动信息
    while 1:
        add_price = input('0: 退出\n输入减免金额: ')
        if add_price == '0':
            break
        reduce_price = input('输入门槛: ')
        full_reduction_detail.append({
            "addPrice": add_price,
            "reducePrice": reduce_price
        })

    # 管理后台登录
    common.account.admin_login()
    admin_token = common.account.get_admin_token()

    # 获取商品数据
    goods_list = get_activity_goods(goods_num)

    # 定义开始时间和结束时间
    now = datetime.now()
    start_time = (now + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
    end_time = (now + timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S')

    # 定义请求参数
    body = {
        "name": f"满减活动({start_time})",
        "startTime": start_time,
        "endTime": end_time,
        "modeType": 0,
        "goodsList": goods_list,
        "addReduce": full_reduction_detail
    }

    # 请求创建活动接口
    request = common.req.request_post(url='/store/manage/promotion/full-discount/saveFullDiscount',
                                      token=admin_token,
                                      body=body)
    print(body, '\n---------------------------------------\n')
    print(request['text'])


if __name__ == '__main__':
    # half_price_activity(goods_num=10)
    full_discount(goods_num=10)
