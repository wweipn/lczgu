# -*- coding: utf-8 -*-
# @Time: 2021/2/27 13:32
# @Author: Waipang

import common
import Config
import time
import random

# 连接老系统数据库
old_db = common.Database()
old_db.database = Config.get_db(env='old_test')

old_db_member = common.Database()
old_db_member.database = Config.get_db(env='old_test_member')


def content_get():
    content_result = old_db_member.select_one(sql="""
    SELECT
        DISTINCT content
    FROM
        es_member_comment
    WHERE
        content NOT LIKE"%好评%"
    ORDER BY RAND()
    LIMIT 1
    """)

    for result in content_result:
        return result


def get_order_goods_id(token, status):
    """
    获取待评价的商品
    :param status:
    :param token:
    :return:
    """

    order_goods_list = []
    page_num = 1
    body = {
        "evaluateStatus": status,
        "currentPage": page_num,
        "pageSize": 10
    }
    while 1:
        request = common.req.request_post(url='/store/api/evaluate/getEvaluateForOrderGoodsList',
                                          token=token,
                                          body=body)
        get_evaluate = request['data']['records']
        currentPage = int(request['data']['pages'])
        for evaluate in get_evaluate:
            order_goodsId = evaluate['orderGoodsId']
            order_goods_list.append(order_goodsId)

        if page_num == currentPage:
            return order_goods_list
        else:
            page_num += 1


def add_evaluate(token, add_type=1):
    """
    添加评论/追评
    :param token: 用户token
    :param add_type: 评价类型 1: 初评 3: 追评
    :return:
    """

    if add_type == 1:
        for order_goods_id in get_order_goods_id(token=token, status=0):
            body = {
                "content": content_get(),
                "goodsEvaluateImageAddReqVOs": get_goods_url(),
                # "isAnonymous": random.randint(0, 1),
                "isAnonymous": random.randint(0, 1),
                "level": random.randint(1, 5),
                "orderGoodsId": order_goods_id,
                "type": add_type
            }
            request = common.req.request_post(url='/store/web/evaluate/addEvaluate',
                                              body=body,
                                              token=token)

            print(f"""
            ----------------------------------------------
            {body}
            {request['text']}
            ----------------------------------------------

            """.replace("'", '"'))

    elif add_type == 3:
        for order_goods_id in get_order_goods_id(token=token, status=1):

            # 获取评价详情页数据
            get_evaluate_detail = common.req.request_get(url=f'/store/api/evaluate/getEvaluateDetail',
                                                         params={'orderGoodsId': order_goods_id},
                                                         token=user_token)
            main_id = get_evaluate_detail['data']['evaluateId']

            body = {
                "content": content_get(),
                "goodsEvaluateImageAddReqVOs": get_goods_url(),
                "isAnonymous": random.randint(0, 1),
                "level": random.randint(1, 5),
                'mainId': main_id,
                'orderGoodsId': order_goods_id,
                "type": add_type
            }

            # 发起追评
            request = common.req.request_post(url='/store/web/evaluate/addEvaluate',
                                              body=body,
                                              token=token)
            time.sleep(0.5)

            print(f"""
            ----------------------------------------------
            {body}
            {request['text']}
            ----------------------------------------------

            """.replace("'", '"'))


def get_goods_url():
    """
    获取评价图片(现在是从老库里面拉的)
    :return:
    """
    image_list = []
    image_num = random.randint(0, 9)
    main_image_result = old_db.select_all(sql=f"""
        SELECT
            big 
        FROM
            es_goods_gallery es_goods_gallery
        RIGHT JOIN ( SELECT goods_id FROM es_goods_gallery ORDER BY RAND( ) LIMIT 1 ) AS b ON 
            b.goods_id = es_goods_gallery.goods_id 
        """
                                          )
    count = 0
    for goods_main_image_url in main_image_result:
        if count < image_num:
            main_image = goods_main_image_url[0]
            image_list.append({
                    "height": 800,
                    "original": main_image,
                    "width": 800
                })
            count += 1
        else:
            break

    return image_list


if __name__ == '__main__':
    # 登录用户账号,并获取token
    common.account.user_login(['19216850004'])
    user_token = common.account.get_user_token(mobile='19216850004')

    # 添加评论/追评(add_type 1: 评价, 3: 追评 )
    add_evaluate(token=user_token, add_type=1)
