# -*- coding: utf-8 -*-
# @Time: 2021/1/4 12:33
# @Author: Waipang

import Config
import common
from testDataCreate.CategoryAdd import get_category_dic
from testDataCreate.BrandAdd import get_brand_id_dic
import time

# 连接老系统数据库
old_db = common.Database()
old_db.database = Config.get_db(env='old_test')

# 获取品牌字典表
brand_dic = get_brand_id_dic()

# 获取分类字典表
category_dic = get_category_dic()

# 系统后台登录
common.account.admin_login()
admin_token = common.account.get_admin_token()


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
        a = {}
        sku_vo = []
        for sku_spec in result:
            i_list_str = sku_spec[0].replace("null", "None")
            sku_spec_list = list(eval(i_list_str))
            for spec_detail in sku_spec_list:
                spec_name = spec_detail["spec_name"]
                spec_value = spec_detail["spec_value"]
                if spec_name not in a:
                    a[spec_name] = [{"specValue": spec_value}]
                else:
                    if {"specValue": spec_value} in a[spec_name]:
                        pass
                    else:
                        a[spec_name].append({"specValue": spec_value})

        for k, v in a.items():
            sku_vo.append({"specName": k, "goodsSpecificationValueReqVO": v})
        return sku_vo


def get_goods_sku_req_vo(goods_id):
    goods_sku_req_vo = []
    # 查询商品的sku信息
    result = old_db.select_all(f"""
    SELECT
        specs,price,thumbnail,sku_id,cost,category_id
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
        old_sku_id = sku[3]
        cost = float(sku[4])
        category_id = category_dic[sku[5]]

        # 往商品sku信息中插入数据
        goods_sku_req_vo.append(
            {
                "cost": cost,  # 供货价
                "price": price,  # 销售价
                "linePrice": round(price * 120 / 100, 2),  # 市场价, 销售价基础+20%
                "retailPrice": round(price * 105 / 100, 2),  # 建议零售价, 销售价基础+5%
                "profitPrice": round(cost * 110 / 100, 2),  # 成本价, 供货价基础+10%
                "enableQuantity": 500,
                "name": "",
                "warnQuantity": 50,
                "categoryId": category_id,
                "sn": old_sku_id,
                "thumbnail": thumbnail,
                "goodsSpecificationReqVO": []
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


def get_goods_spu_req_vo(goods_id, goods_type=0):
    result = old_db.select_one(sql=f"""
    SELECT
        goods_name, category_id, goods_id, brand_id, mobile_intro, original
    FROM
        es_goods
    WHERE
        goods_id = '{goods_id}'
    """)
    name = result[0]
    category_lv3_id = category_dic[result[1]]
    category_lv2_id = get_parent_category_id(category_lv3_id)
    category_lv1_id = get_parent_category_id(category_lv2_id)
    sn_goods_id = result[2]
    brand_id = brand_dic[result[3]] if result[3] is not None else 0
    detail = []
    original = result[5]

    # 判断商品主图列表是否为空或者有布尔值,处理后有图片则写入
    if result[4] != '':
        if result[4].find('false') != -1:
            if result[4].find('true') != -1:
                image_url_list = list(eval(result[4].replace("null", "None").replace("false", "None").
                                           replace("true", "None")))
            else:
                image_url_list = list(eval(result[4].replace("null", "None").replace("false", "None")))
        else:
            image_url_list = list(eval(result[4].replace("null", "None")))
        # 查询商品详情页图片,写入detail中
        for goods_detail_image_url in image_url_list:
            detail_url = goods_detail_image_url["content"]
            detail.append({"url": detail_url})

    # 获取商品主图,写入mainGallery中
    main_image_result = old_db.select_all(sql=f"""
    SELECT big FROM es_goods_gallery WHERE goods_id = '{goods_id}'
    """
                                          )
    mainGallery = []
    for goods_main_image_url in main_image_result:
        main_image = goods_main_image_url[0]
        mainGallery.append({'url': main_image})

    vo = {
        "specsItemRespVOList": get_specs_item_resp_vo_list(goods_id=goods_id),
        "name": name,
        "categoryId": category_lv1_id,
        "categoryId2": category_lv2_id,
        "categoryId3": category_lv3_id,
        "sn": sn_goods_id,
        "brandId": brand_id,  # 品牌ID
        "enableQuantity": 1000,  # 库存总和
        "warnQuantity": 10,  # 预警库存
        "transfeeCharge": 0,  # 包邮：0 不包邮：1
        # "templateId": "1362708019229540354",  # 运费模板ID
        "isSupportAfter": 1,  # 是否支持售后7天 0:否；1:是
        # "specialTitle": ",  # 特殊说明
        # "specialContent": ",  # 特殊内容
        "detail": f'{detail}'.replace("'", '"'),  # 商品详情图
        "original": original,
        "type": goods_type,  # 商品类型 0:普通商品;1:臻宝商品;2.VIP商品
        "mainGallery": mainGallery,  # 商品主图,
        # "vipDay": 30,  # VIP天数
        "vipGallery": []  # vip主图
    }

    if goods_type == 2:
        vo['vipDay'] = 30
        vo['vipGallery'].append({"url": original})

    return vo


def add_goods(goods_id, token, goods_type=0):
    body = {
        "goodsSpuReqVO": get_goods_spu_req_vo(goods_id, goods_type),
        "goodsSkuReqVO": get_goods_sku_req_vo(goods_id)
    }
    add = common.req.request_post(url="/store/seller/goodsManager/save", token=token, body=body)
    if add['code'] == 200:
        print('商品添加成功')
    else:
        print(add['text'])


def get_shop_goods(shop_id):
    goods_list = []
    goods_result = old_db.select_all(sql=f"""
    SELECT goods_id FROM es_goods WHERE seller_id = '{shop_id}'
    """)

    for goods in goods_result:
        goods_id = goods[0]
        goods_list.append(goods_id)
    return goods_list


def get_rand_goods():

    goods_result = old_db.select_one(sql=f"""
        SELECT goods_id FROM es_goods order by rand() limit 1
        """)
    goods_id = goods_result[0]
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
    create = common.req.request_post(url='/store/manage/shop', token=admin_token, body=body)
    if create['code'] == 200:
        print(f'注册成功,账号:{shop_name}, 密码:a123456')
        return shop_name
    else:
        print(f"注册失败,{create['text']}")


if __name__ == '__main__':
    # # 供应商账号注册(shop_id: 老系统供应商ID)
    # create_shop = shop_create(shop_id='63')

    # 供应商登录
    common.account.shop_login(username="Wepn", password='a123456')
    shop_token = common.account.get_shop_token()

    # 根据老系统的商家ID添加商品
    # goods_data = get_shop_goods(shop_id='63')
    # for data in goods_data:
    #     add_goods(goods_id=data, shop_token=token)
    #     time.sleep(1.5)

    # 添加任意一个商品
    add_goods(goods_id=get_rand_goods(), token=shop_token, goods_type=1)
