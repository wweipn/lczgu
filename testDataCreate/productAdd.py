# -*- coding: utf-8 -*-
# @Time: 2021/1/4 12:33
# @Author: Waipang

import common
import Config

# 链接老系统数据库
old_db = common.Database()
old_db.database = Config.get_db(env='old_test')


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


def get_goods_sku_req_vo(goods_id, category_id=13509962146858926):
    goods_sku_req_vo = []
    result = old_db.select_all(f"""
    SELECT
        specs,price,thumbnail,sku_id,cost
    FROM
        es_goods_sku
    WHERE
        goods_id = '{goods_id}'
    """)
    count = 0
    for sku in result:

        i_list_str = sku[0].replace("null", "None")
        sku_spec_list = list(eval(i_list_str))
        price = float(sku[1])
        thumbnail = sku[2]
        old_sku_id = sku[3]
        cost = float(sku[4])

        goods_sku_req_vo.append(
            {
                "categoryId": category_id,
                "cost": cost,
                "enableQuantity": 500,
                "name": "",
                "price": price,
                "warnQuantity": 50,
                "sn": old_sku_id,
                "thumbnail": thumbnail,
                "goodsSpecificationReqVO": []
            }
        )

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
    return goods_sku_req_vo


def get_goods_spu_req_vo(goods_id):
    result = old_db.select_one(sql=f"""
    SELECT
        goods_name, category_id, goods_id, brand_id, mobile_intro, original
    FROM
        es_goods
    WHERE
        goods_id = '{goods_id}'
    """)
    name = result[0]
    category_id = result[1]
    sn_goods_id = result[2]
    brand_id = result[3]
    image_url_list = list(eval(result[4].replace("null", "None")))
    original = result[5]
    mainGallery = []
    detail = []

    # 查询商品详情页图片,写入detail中
    for goods_detail_image_url in image_url_list:
        detail_url = goods_detail_image_url["content"]
        detail.append({'url': detail_url})

    # 获取商品主图,写入mainGallery中
    main_image_result = old_db.select_all(sql=
                                             f"""
        SELECT thumbnail FROM es_goods_gallery WHERE goods_id = '{goods_id}'
        """
                                             )
    for goods_main_image_url in main_image_result:
        main_image = goods_main_image_url[0]
        mainGallery.append({'url': main_image})

    vo = {
        "specsItemRespVOList": get_specs_item_resp_vo_list(goods_id=goods_id),
        "name": name,
        "categoryId": 0,
        "categoryId2": 134952418106245,
        "categoryId3": 13509962146858926,
        "sn": sn_goods_id,
        "brandId": 0,  # 品牌ID
        "enableQuantity": 1000,  # 库存总和
        "warnQuantity": 10,  # 预警库存
        "transfeeCharge": 1,  # 是否为买家承担运费 否：0 是：1
        # "templateId": ",  # 运费模板ID
        "isSupportAfter": 1,  # 是否支持售后7天 0:否；1:是
        # "specialTitle": ",  # 特殊说明
        # "specialContent": ",  # 特殊内容
        "detail": str(detail),  # 商品详情图
        # "detail": '',  # 商品详情图
        "original": original,
        "mainGallery": mainGallery,  # 商品主图
        "vipGallery": []  # vip主图
    }

    return vo





if __name__ == '__main__':
    # common.account.shop_login(username="shop_test_01", password="a123456")
    # shop_token = common.account.get_shop_token()
    # body = {
    #     "goodsSpuReqVO": get_goods_spu_req_vo(goods_id='1172'),
    #     "goodsSkuReqVO": get_goods_sku_req_vo(goods_id='1172')
    # }
    # add_goods = common.req.request_post(url="/store/seller/goodsManager/save", token=shop_token, body=body)
    print(set_brand_id_dic())
