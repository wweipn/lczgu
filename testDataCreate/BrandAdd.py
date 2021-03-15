# -*- coding: utf-8 -*-
# @Time: 2021/1/19 14:34
# @Author: Waipang

import common
import time
import Config

# 连接老系统数据库
old_db = common.Database()
old_db.database = Config.get_db(env='old_release_goods')


def add_brand():
    """
    从老系统获取品牌数据后添加到新系统
    :return:
    """

    # 查询老系统品牌表
    result = old_db.select_all(sql="""
        SELECT 
            name, logo  
        FROM 
            es_brand
    """)

    # 系统后台登录并获取token
    admin_token = common.admin_token()
    url = '/store/manage/goodsBrand/save'

    # 遍历老系统品牌表查询结果,调用添加品牌结果添加数据
    for brand in result:
        name = brand[0]
        logo = brand[1] if brand[1] != '' else 'url'
        body = {
            'name': name,
            'logo': logo
        }
        add = common.req.request_post(url=url, body=body, token=admin_token)
        print(f"""
        【添加品牌】
        请求
        {body}
        
        返回
        {add['text']}
        """)
        time.sleep(0.1)


def get_brand_id_dic():
    """
    获取品牌新老系统字典表
    :return:
    """
    brand_dic = {}
    old_brand_list = []
    new_brand_list = []

    # 查询老系统品牌
    old_brand_result = old_db.select_all(sql=f"""
    SELECT brand_id, name FROM es_brand
    """)

    # 遍历老系统品牌查询结果, 写入列表
    for old_brand in old_brand_result:
        brand_id = old_brand[0]
        brand_name = old_brand[1]
        old_brand_list.append({brand_name: brand_id})

    # 查询新系统品牌
    new_brand_result = common.db.select_all(sql="""
    SELECT id, name FROM goods_brand WHERE name is not null
    """)

    # 遍历新系统品牌查询结果, 写入列表
    for new_brand in new_brand_result:
        brand_id = new_brand[0]
        brand_name = new_brand[1]
        new_brand_list.append({brand_name: brand_id})

    # 遍历老品牌列表
    for o_brand in old_brand_list:
        # 取出老品牌列表每条数据的品牌名称和id
        for old_brand_name, old_brand_id in o_brand.items():
            # 遍历新品牌列表
            for n_brand in new_brand_list:
                # 取出新品牌列表每条数据的品牌名称和ID
                for n_brand_name, n_brand_id in n_brand.items():
                    if old_brand_name == n_brand_name:
                        brand_dic[old_brand_id] = n_brand_id

    return brand_dic


if __name__ == '__main__':
    add_brand()
    # print(get_brand_id_dic())
