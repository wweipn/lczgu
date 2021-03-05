# -*- coding: utf-8 -*-
# @Time: 2021/1/21 15:02
# @Author: Waipang

import common
import time


def goods_audit(audit_num, supplier_id=None):
    """
    审核商品
    :param supplier_id: 商家ID
    :param audit_num: 审核商品数量
    :return:
    """

    # 登录运营后台, 获取token
    admin_token = common.admin_token()

    # 定义获取审核列表的请求体
    goods_list_body = {
        "auditStatus": 0,
        "currentPage": 1,
        "status": 4,
        "pageSize": audit_num
    }

    if supplier_id is not None:
        goods_list_body['supplierId'] = supplier_id

    # 调用审核商品接口
    get_goods_list = common.req.request_post(url='/store/manage/goodsManager/getPage', body=goods_list_body,
                                             token=admin_token)
    # 定义审核商品列表返回值
    good_list = get_goods_list['data']['records']
    if len(good_list) != 0:
        for audit_goods in good_list:
            goods_id = audit_goods['spuId']
            audit_body = {
                "auditStatus": 1,
                "id": goods_id,
                "status": 3
            }
            audit = common.req.request_put(url='/store/manage/goodsManager/upStatus', body=audit_body, token=admin_token)
            if audit['code'] == 200:
                print(f'goodsId: 【{goods_id}】审核通过')
            else:
                print(audit_body)
                print(f"审核异常: {audit['text']}")
            time.sleep(0.5)
    else:
        print('审核商品列表无数据')


if __name__ == '__main__':
    # 商品审核
    goods_audit(audit_num=10, supplier_id=27)
