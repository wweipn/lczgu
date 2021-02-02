# -*- coding: utf-8 -*-
# @Time: 2021/1/19 15:11
# @Author: Waipang

import common
import time
import Config

# 连接老系统数据库
old_db = common.Database()
old_db.database = Config.get_db(env='old_test')


def add_category():
    # 管理后台登录并获取token
    common.account.admin_login()
    admin_token = common.account.get_admin_token()

    # 查询老系统的一级分类
    lv1_category_result = old_db.select_all(sql="""
    SELECT 
        name 
    FROM 
        es_category 
    WHERE 
        parent_id = '0'
    """)

    # 遍历老系统一级分类并添加一级分类
    for lv1_category in lv1_category_result:
        lv1_category_name = lv1_category[0]
        body = {
            "isShow": 1,
            "level": 1,
            "name": lv1_category_name,
            "sort": 1
        }
        add_lv1_category = common.req.request_post(url='/store/manage/category/save', token=admin_token, body=body)

    # 查询新系统的一级分类
    new_sys_lv1_category_result = common.db.select_all(sql="""
    SELECT
        id,
        name
    FROM
        goods_category 
    WHERE
        level = 1
    """)

    # 遍历新系统的一级分类
    for new_sys_lv1_category in new_sys_lv1_category_result:
        lv1_category_id = new_sys_lv1_category[0]
        lv1_category_name = new_sys_lv1_category[1]
        # print(lv1_category_id, lv1_category_name)

        # 查询老系统二级分类
        second_category_result = old_db.select_all(sql=f"""
        SELECT
            name,
            image
        FROM
            es_category
        WHERE
            parent_id = ( SELECT category_id FROM es_category WHERE `name` = '{lv1_category_name}' )
        """)

        # 遍历老系统二级分类的查询结果, 拼接请求体参数后调用添加分类接口
        for lv2_category in second_category_result:
            lv2_category_name = lv2_category[0]
            lv2_category_image_url = lv2_category[1]
            print({"parentId": lv1_category_id, "name": lv2_category_name, "logo": lv2_category_image_url})
            body = {
                "isShow": 1,
                "level": 2,
                "logo": lv2_category_image_url,
                "name": lv2_category_name,
                "parentId": lv1_category_id,
                "sort": 1
            }
            add_lv2_category = common.req.request_post('/store/manage/category/save', token=admin_token, body=body)
            time.sleep(0.2)
        print(f'【{lv1_category_name}】二级分类添加完成')

    # 查询新系统二级分类
    new_sys_category_result = common.db.select_all(sql=f"""
    SELECT
        id, name
    FROM
        goods_category 
    WHERE
        level = 2
    AND
        create_time >= "2021-01-19 17:48:00"
    """)

    count = 0
    # 遍历新系统二级分类的查询结果
    for new_sys_category in new_sys_category_result:
        new_lv2_category_id = new_sys_category[0]
        new_lv2_category_name = new_sys_category[1]

        # 查询该二级分类在老系统三级分类
        lv3_category_result = old_db.select_all(sql=f"""
        SELECT
            name,
            image
        FROM
            es_category
        WHERE
            parent_id = ( SELECT category_id FROM es_category WHERE name = '{new_lv2_category_name}')
        """)

        # 遍历老系统三级分类的查询结果, 拼接请求体后调用添加分类接口
        for lv3_category in lv3_category_result:
            lv3_category_name = lv3_category[0]
            lv3_category_image_url = lv3_category[1]
            body = {
                "isShow": 1,
                "level": 3,
                "logo": lv3_category_image_url,
                "name": lv3_category_name,
                "parentId": new_lv2_category_id,
                "sort": 1
            }
            add_lv3_category = common.req.request_post('/store/manage/category/save', token=admin_token, body=body)
            count += 1
            time.sleep(0.3)
            print(f'第【{count}】条数据添加成功')


# 获取分类新老系统字典表
def get_category_dic():
    category_dic = {}
    old_category_list = []
    new_category_list = []

    # 查询老系统分类
    old_category_result = old_db.select_all(sql=f"""
    SELECT category_id, name FROM es_category
    """)

    # 遍历老系统分类查询结果, 写入列表
    for old_category in old_category_result:
        category_id = old_category[0]
        brand_name = old_category[1]
        old_category_list.append({brand_name: category_id})

    # 查询新系统分类
    new_category_result = common.db.select_all(sql="""
    SELECT id, name FROM goods_category WHERE name is not null
    """)

    # 遍历新系统分类查询结果, 写入列表
    for new_category in new_category_result:
        category_id = new_category[0]
        brand_name = new_category[1]
        new_category_list.append({brand_name: category_id})

    # 遍历老分类列表
    for o_category in old_category_list:
        # 取出老分类列表每条数据的分类名称和id
        for old_category_name, old_brand_id in o_category.items():
            # 遍历新分类列表
            for n_category in new_category_list:
                # 取出新分类列表每条数据的分类名称和ID
                for n_category_name, n_category_id in n_category.items():
                    if old_category_name == n_category_name:
                        category_dic[old_brand_id] = n_category_id

    return category_dic


if __name__ == '__main__':
    print(get_category_dic())