# -*- coding: utf-8 -*-
# @Time: 2021/2/18 18:16
# @Author: Waipang

import common


def half_price_close():
    """
    关闭所有进行中的第二件半价活动
    :return:
    """
    admin_token = common.admin_token()
    request = common.req.request_get('/store/manage/promotion/half-price/queryHalfPriceList',
                                     params={"pageSize": 30, "currentPage": 1, "status": 2},
                                     token=admin_token)
    for activity in request['data']['records']:
        activity_id = activity['id']
        common.req.request_post('/store/manage/promotion/half-price/closeSingleHalfPrice',
                                params={'id': activity_id},
                                token=admin_token)


def pintuan_close():
    """
    关闭所有拼团活动
    :return:
    """
    admin_token = common.admin_token()
    request = common.req.request_get('/store/manage/promotion/pintuan/queryPintuanList',
                                     params={"pageSize": 30, "currentPage": 1, "status": 1},
                                     token=admin_token)
    for activity in request['data']['records']:
        activity_id = activity['id']
        common.req.request_post('/store/manage/promotion/pintuan/closePintuan',
                                params={'id': activity_id},
                                token=admin_token)


if __name__ == '__main__':

    pintuan_close()  # 关闭拼团活动
    half_price_close()  # 关闭半价活动
