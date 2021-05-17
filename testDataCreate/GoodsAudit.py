# -*- coding: utf-8 -*-
# @Time: 2021/1/21 15:02
# @Author: Waipang

import common
import time
import csv


def goods_audit(audit_num=100, shop_name=None, audit_type=1, spu_id=None):
    """
    审核商品
    :param spu_id:
    :param audit_type: 审核类型: 0:批量下架 1: 批量上架
    :param shop_name: 商家ID
    :param audit_num: 审核商品数量
    :return:
    """

    # 登录运营后台, 获取token
    admin_token = common.admin_token()

    currentPage = 1
    while 1:
        # 定义获取审核列表的请求体
        goods_list_body = {
            "currentPage": currentPage,  # 当前页数
            "pageSize": audit_num  # 每页数量
        }
        if audit_type == 0:
            goods_list_body['status'] = 3  # 商品状态 3：上架

        elif audit_type == 1:
            goods_list_body['auditStatus'] = 0  # 商品审核状态 0：待审核

        if spu_id is not None:
            goods_list_body['spuId'] = spu_id

        if shop_name is not None:
            goods_list_body['supplierName'] = shop_name

        # 调用审核商品接口
        get_goods_list = common.req.request_post(url='/store/manage/goodsManager/getPage', body=goods_list_body,
                                                 token=admin_token)
        # 定义审核商品列表返回值
        good_list = get_goods_list['data']['records']
        if len(good_list) != 0:

            audit_body = {}

            if audit_type == 0:
                audit_body['auditStatus'] = 1  # 商品审核状态维持为审核通过
                audit_body['status'] = 4  # 更改商品状态为下架
                audit_body['underMessage'] = '商品下架'  # 添加审核备注

            elif audit_type == 1:
                audit_body['auditStatus'] = 1  # 商品审核状态更改为审核通过
                audit_body['status'] = 3  # 更改商品状态为上架

            for audit_goods in good_list:
                goods_id = audit_goods['spuId']
                audit_body['id'] = goods_id
                audit = common.req.request_put(url='/store/manage/goodsManager/upStatus', body=audit_body,
                                               token=admin_token)
                if audit['code'] == 200:
                    if audit_type == 1:
                        print(f'【goodsId:{goods_id}】审核通过')
                    elif audit_type == 0:
                        print(f'【goodsId:{goods_id}】下架成功')
                else:
                    print(audit_body)
                    print(f"审核异常: {audit['text']}")
            currentPage += 1

        else:
            print('审核商品列表无数据')
            return


def goods_audit_batch():
    file_path = common.get_file_path(file_name='id.csv', parent_path='test_file')
    with open(file_path, 'r', encoding='utf-8') as GoodsData:
        spu = csv.reader(GoodsData)
        next(spu)
        data_list = []
        for data in spu:
            spu_id = data[0]
            data_list.append(spu_id)
        return data_list


def batch_audit():
    data = goods_audit_batch()
    admin_token = common.admin_token()
    for spu_id in data:
        url = '/store/manage/goodsManager/upStatus'
        body = {
            'id': spu_id,
            'auditStatus': 1,
            'status': 3,
            'underMessage': 'VIP商品上架'
        }
        audit = common.req.request_put(url=url, body=body,
                                       token=admin_token)
        common.api_print(name='商品审核', url='/store/manage/goodsManager/upStatus', result=audit, data=body)
        time.sleep(0.2)


if __name__ == '__main__':
    # shop_list = []

    # 商品审核
    # goods_audit(audit_num=100, audit_type=0, shop_name=None, spu_id=None)

    batch_audit()
