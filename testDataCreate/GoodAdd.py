# -*- coding: utf-8 -*-
# @Time: 2021/1/4 12:33
# @Author: Waipang

import Config
import common
import random
from testDataCreate.CategoryAdd import get_category_dic
from testDataCreate.BrandAdd import get_brand_id_dic
import time

# 连接老系统数据库
old_db = common.Database()
old_db.database = Config.get_db(env='old_test_goods')

# 链接老系统数据库(用户)
old_db_account = common.Database()
old_db_account.database = Config.get_db(env='old_test_member')

# 获取品牌字典表
brand_dic = get_brand_id_dic()

# 获取分类字典表
category_dic = get_category_dic()

# 系统后台登录
# common.account.admin_login()
# admin_token = common.account.get_admin_token()


def get_parent_category_id(category):
    result = common.db.select_one(sql=f"""
    select parent_id from goods_category where id = {category}
    """)
    parent_id = result[0]
    return parent_id


# 返回商品sku信息VO
def get_specs_item_resp_vo_list(goods_id):
    """
    获取商品所有sku属性以及信息
    :param goods_id:
    :return: {"specName": k, "goodsSpecificationValueReqVO": v}

    """
    result = old_db.select_all(f"""
    SELECT
        specs
    FROM
        es_goods_sku
    WHERE
        es_goods_sku.goods_id = '{goods_id}'
    """)
    if result == () or result[0][0] is None:
        return []
    else:
        spec_dic = {}
        sku_vo = []
        for sku_spec in result:
            i_list_str = sku_spec[0].replace("null", "None")
            sku_spec_list = list(eval(i_list_str))
            for spec_detail in sku_spec_list:
                spec_name = spec_detail["spec_name"]
                spec_value = spec_detail["spec_value"]
                if spec_name not in spec_dic:
                    spec_dic[spec_name] = [{"specValue": spec_value}]
                else:
                    if {"specValue": spec_value} in spec_dic[spec_name]:
                        pass
                    else:
                        spec_dic[spec_name].append({"specValue": spec_value})

        for k, v in spec_dic.items():
            sku_vo.append({"specName": k, "goodsSpecificationValueReqVO": v})
        return sku_vo


def get_goods_sku_req_vo(goods_id):
    goods_sku_req_vo = []
    # 查询商品的sku信息
    result = old_db.select_all(f"""
    SELECT
        specs,price,thumbnail,sn,cost,category_id,enable_quantity, sku_id, goods_id
    FROM
        es_goods_sku
    WHERE
        goods_id = '{goods_id}'
    """)
    count = 0
    # 遍历商品sku查询结果
    for sku in result:
        specs = sku[0]
        price = float(sku[1])
        thumbnail = sku[2]
        sn = sku[3]
        cost = float(sku[4])
        category_id = category_dic[sku[5]]
        enable_quantity = int(sku[6])
        sku_id = sku[7]
        spu_id = sku[8]

        # 往商品sku信息中插入数据
        goods_sku_req_vo.append(
            {
                "cost": cost,  # 供货价
                "price": price,  # 销售价
                "linePrice": round(price * 130 / 100, 0),  # 市场价, 销售价基础+30%
                "retailPrice": price,  # 建议零售价,取零售价
                "profitPrice": cost,  # 成本价,取供货价
                # "retailPrice": round(price * 105 / 100, 2),  # 建议零售价, 销售价基础+5%
                # "profitPrice": round(cost * 110 / 100, 2),  # 成本价, 供货价基础+10%
                # "enableQuantity": 0,  # 库存
                "enableQuantity": enable_quantity,  # 库存
                "name": "",  # sku名称
                "warnQuantity": 20,  # 预警库存
                "categoryId": category_id,
                "sn": sn,
                "thumbnail": thumbnail,
                "goodsSpecificationReqVO": [],
                "oldSku": sku_id,
                "oldSpu": spu_id
            }
        )

        # 如果商品规格表中有数据, 则进行遍历并把对应的值插入goodsSpecificationValueReqVO中
        if specs is not None:
            i_list_str = specs.replace("null", "None")
            sku_spec_list = list(eval(i_list_str))
            for spec_detail in sku_spec_list:
                spec_name = spec_detail["spec_name"]
                spec_value = spec_detail["spec_value"]
                sku_detail = goods_sku_req_vo[count]["goodsSpecificationReqVO"]
                goods_sku_req_vo[count]["name"] += spec_value + "; "
                sku_detail.append({
                    "specName": spec_name,
                    "goodsSpecificationValueReqVO": [{"specName": spec_name, "specValue": spec_value}]
                })
            goods_sku_req_vo[count]["name"] = goods_sku_req_vo[count]["name"][:-2]
            count += 1
        else:
            pass

    return goods_sku_req_vo


def new_get_goods_spu_req_vo(goods_id, goods_type=None):
    """
    生成保存商品接口中商品VO的数据(数据迁移用)
    :param goods_type: 商品类型 0:普通商品;1:臻宝商品;2.VIP商品
    :param goods_id: 老系统商品ID
    :return:
    """
    result = old_db.select_one(sql=f"""
    SELECT
        goods_name, category_id, goods_id, brand_id, mobile_intro, original, sn, goods_type
    FROM
        es_goods
    WHERE
        goods_id = '{goods_id}'
    """)

    name = result[0]
    category_lv3_id = category_dic[result[1]]
    category_lv2_id = get_parent_category_id(category_lv3_id)
    category_lv1_id = get_parent_category_id(category_lv2_id)
    brand_id = brand_dic[result[3]] if result[3] is not None else 0
    detail = []
    original = result[5]
    sn = result[6]
    if goods_type is None:
        goods_type = 0 if result[7] == 'NORMAL' else 1

    if result[4] != '':
        data = result[4]
        data = data.replace('false', '1')
        data = data.replace('true', '1')
        data = data.replace('null', '1')
        image_list = list(eval(data))

        # 查询商品详情页图片,写入detail中
        for goods_detail_image_url in image_list:
            detail_url = goods_detail_image_url["content"]
            detail.append({"url": detail_url})

    # 获取商品主图,写入mainGallery中
    main_image_result = old_db.select_all(sql=f"""
    SELECT original FROM es_goods_gallery WHERE goods_id = '{goods_id}'
    """)
    mainGallery = []
    for goods_main_image_url in main_image_result:
        main_image = goods_main_image_url[0]
        mainGallery.append({'url': main_image})

    vo = {
        "specsItemRespVOList": get_specs_item_resp_vo_list(goods_id=goods_id),
        "name": name,
        "categoryId": category_lv1_id,  # 一级分类ID
        "categoryId2": category_lv2_id,  # 二级分类ID
        "categoryId3": category_lv3_id,  # 三级分类ID
        "sn": sn,  # 老系统sn
        "brandId": brand_id,  # 品牌ID
        "warnQuantity": 10,  # 预警库存
        "transfeeCharge": 0,  # 包邮：0 不包邮：1
        "isSupportAfter": 1,  # 是否支持售后7天 0:否；1:是
        "detail": f'{detail}'.replace("'", '"').replace(' ', ''),  # 商品详情图
        "original": original,
        "type": goods_type,  # 商品类型 0:普通商品;1:臻宝商品;2.VIP商品
        "mainGallery": mainGallery,  # 商品主图,
        "vipGallery": [],  # vip主图
        "remark": goods_id
    }

    # if goods_type == 2:
    #     vo['vipDay'] = random.randint(7, 30)
    #     vo['vipGallery'].append({"url": original})

    return vo


def get_goods_audit_status(goods_id):
    """
    获取商品审核状态
    :param goods_id:
    :return:
    """
    result = old_db.select_one(sql=f"""
    SELECT 
        market_enable, # 上架状态 1上架  0下架
        is_auth, # 0：待审核，1：审核通过，2：审核拒绝
        under_message # 下架原因
    FROM
        es_goods
    where
        goods_id = {goods_id}
    """)
    market_enable = 3 if result[0] == 1 else 4
    is_auth = result[1]
    under_message = result[2]

    return market_enable, is_auth, under_message


def add_goods(goods_id, token, admin_token, audit_type=0, goods_type=None):
    """
    添加商品
    :param goods_type:
    :param goods_id: 老系统商品ID
    :param token: 商家token
    :param audit_type: 审核类型 0: 根据老系统数据库状态 其他: 审核通过
    :param admin_token: 管理后台token
    :return:
    """
    while 1:
        spu_req_vo = new_get_goods_spu_req_vo(goods_id=goods_id, goods_type=goods_type)  # 获取商品信息
        sku_req_vo = get_goods_sku_req_vo(goods_id=goods_id)  # 获取规格信息

        body = {
            "goodsSpuReqVO": spu_req_vo,
            "goodsSkuReqVO": sku_req_vo
        }

        # 调用保存商品接口
        add = common.req.request_post(url="/store/seller/goodsManager/save", token=token, body=body)

        try:
            spu_id = add['data']
            if audit_type == 0:
                status, is_auth, under_message = get_goods_audit_status(goods_id)

                if is_auth != 0:
                    auto_goods_audit(token=admin_token, spu_id=spu_id, audit_status=is_auth, status=status,
                                     under_message=under_message)
            else:
                auto_goods_audit(token=admin_token, spu_id=spu_id, audit_status=1, status=3)

            break
        except KeyError:
            print(f"商品【{spu_req_vo['name']}】添加失败, 尝试重新添加")


def get_shop_goods(shop_id):
    """
    获取指定供应商的商品
    :return:
    """
    goods_list = []
    goods_result = old_db.select_all(sql=f"""
    SELECT 
        goods_id 
    FROM 
        es_goods 
    WHERE 
        seller_id = '{shop_id}'
    """)

    for goods in goods_result:
        goods_id = goods[0]
        goods_list.append(goods_id)
    return goods_list


def get_rand_goods():
    """
    获取老系统随机一个商品ID
    :return:
    """

    result = old_db.select_one(sql=f"""
        SELECT goods_id FROM es_goods order by rand() limit 1
        """)

    goods_id = result[0]
    return goods_id


def shop_create(shop_id):
    """
    注册商家后台账号
    :param shop_id: 老系统商家ID
    :return: 商家名称(用于登录使用)
    """

    old_db_member = common.Database()
    old_db_member.database = Config.get_db(env='old_test_member')
    shop_detail = old_db_member.select_one(sql=f"""
    SELECT
        esd.company_address, esd.company_name, esd.company_phone, esd.company_email, \
        esd.link_phone, esd.legal_name, esd.employee_num, es.member_name
    FROM
        es_shop_detail esd
        left join es_shop es ON es.shop_id = esd.shop_id
    where
        es.shop_id = {shop_id}
    """)

    address = shop_detail[0]
    company_name = shop_detail[1]
    company_phone = shop_detail[2]
    email = shop_detail[3]
    notice_phone = shop_detail[4]
    on_access_name = shop_detail[5]
    staff_num = shop_detail[6]
    shop_name = shop_detail[7]

    body = {
        "address": address,
        "companyName": company_name,
        "companyPhone": company_phone,
        "email": email,
        "inventoryWarn": 100,
        "noticePhone": notice_phone,
        "onAccessName": on_access_name,
        "onAccessPhone": notice_phone,
        "password": "123456",
        "regCapital": 1000000,
        "shopName": shop_name,
        "shopType": "1",
        "staffNum": staff_num,
        "status": "1",
        "username": shop_name
    }

    create = common.req.request_post(url='/store/manage/shop', token=common.admin_token(), body=body)
    if create['code'] == 200:
        print(f'注册成功,账号:{shop_name}, 密码:123456')
        return shop_name
    else:
        print(f"注册失败,{create['text']}")


def auto_goods_audit(token, spu_id, audit_status, status, under_message=None):
    """
    审核商品
    :param token: 管理后台token
    :param spu_id: 商品ID
    :param audit_status: 审核状态 0：待审核，1：审核通过，2：审核拒绝
    :param status: 上下架状态 商品状态 3：上架；4：下架
    :param under_message: 审核不通过信息
    :return:
    """

    url = '/store/manage/goodsManager/upStatus'

    body = {
        'id': spu_id,
        'auditStatus': audit_status,
        'status': status
    }

    if audit_status == 2:
        body['underMessage'] = under_message  # 添加审核备注

    audit = common.req.request_put(url=url, body=body, token=token)
    common.api_print(name='商品审核', url=url, data=body, result=audit)


def get_shop_info():
    result = old_db_account.select_all(sql=f"""
    SELECT
        es_shop.shop_id,
        es_member.uname 
    FROM
        es_shop
        LEFT JOIN es_member ON es_member.member_id = es_shop.member_id 
    WHERE
        es_member.shop_id != 2
    AND
        es_shop.shop_disable != 'WAITSUBMIT'
    """)

    shop_name_list = []
    for data in result:
        shop_id = data[0]
        shop_name = data[1]
        shop_name_list.append({
            'shop_id': shop_id,
            'shop_name': shop_name
        })

    return shop_name_list


def data_transfer():
    shop_list = get_shop_info()
    admin_token = common.admin_token()
    for shop in shop_list:
        shop_id = shop['shop_id']
        shop_name = shop['shop_name']
        print(f'开始添加商家【{shop_name}】商品')
        token = common.shop_token(shop_name=shop_name)
        goods_data_list = get_shop_goods(shop_id)
        for goods_id in goods_data_list:
            add_goods(goods_id=goods_id, token=token, admin_token=admin_token)
        print(f'商家【{shop_name}】商品添加完成')


def goods_detail(token, goods_id):
    """
    管理后台商品详情
    :param token:
    :param goods_id: spu_id
    :return:
    """
    url = f'/store/manage/goodsManager/get?spuId={goods_id}'
    request = common.req.request_get(token=token, url=url)
    data = request['data']
    return data


def goods_update(token, goods_id, goods_type):
    """
    商品信息修改
    :param token:
    :param goods_id: spu_id
    :param goods_type: 商品类型: 0: 普通商品, 1: 臻宝商品, 2: VIP商品
    :return:
    """

    goods_detail_data = goods_detail(token=token, goods_id=goods_id)

    if goods_type == 1:
        for sku in goods_detail_data['goodsSkuReqVO']:
            price = sku['price']
            sku['needPayAmount'] = round(price * 0.1, 2)
            sku['needPayZhenBao'] = int(price * 100)

        goods_detail_data['goodsSpuReqVO']['type'] = 1

        url = '/store/manage/goodsManager'
        update = common.req.request_put(token=token, url=url, body=goods_detail_data)
        print(update['text'])


if __name__ == '__main__':
    # pass
    # 执行数据迁移
    # data_transfer()

    # 供应商账号注册(shop_id: 老系统供应商ID)
    # create_shop = shop_create(shop_id='48')

    # 供应商登录
    # shop_token = common.shop_token('wepn')

    # 根据老系统的商家ID添加商品
    # goods_data = get_shop_goods(shop_id='55', spu_type=0)
    # for data in goods_data:
    #     add_goods(goods_id=data, token=shop_token)

    # 添加任意一个商品
    # for i in range(5):
    #     add_goods(goods_id=get_rand_goods(),
    #               token=shop_token,
    #               admin_token=common.admin_token(),
    #               audit_type=1,
    #               goods_type=2)

    # goods_update(token=common.admin_token(), goods_id=1370618534173884418, goods_type=1)
    auto_goods_audit(token=common.admin_token(), spu_id=1370618534173884418, audit_status=1, status=3)

