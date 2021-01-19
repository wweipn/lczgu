# -*- coding: utf-8 -*-
# @Time: 2021/1/19 15:11
# @Author: Waipang

import common
import time
import Config

# 连接老系统数据库
old_db = common.Database()
old_db.database = Config.get_db(env='old_test')

# 管理后台登录并获取token
common.account.admin_login()
admin_token = common.account.get_admin_token()

# 查询新创建的一级分类
result = common.db.select_all(sql="""
SELECT id, name FROM goods_category WHERE `create_time` > "2021-01-19 17:48:00"
""")

# 遍历新系统的一级分类
for category in result:
    lv1_category_id = category[0]
    lv1_category_name = category[1]
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

