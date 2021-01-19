# -*- coding: utf-8 -*-
# @Time: 2021/1/19 14:34
# @Author: Waipang

import common
import time
import Config

# 连接老系统数据库
old_db = common.Database()
old_db.database = Config.get_db(env='old_test')

# 系统后台登录并获取token
admin_login = common.account.admin_login()
admin_token = common.account.get_admin_token()

# 查询老系统品牌表
result = old_db.select_all(sql="""
    SELECT 
        name, logo  
    FROM 
        es_brand  
    group by name
""")

# 遍历老系统品牌表查询结果,调用添加品牌结果添加数据
for brand in result:
    name = brand[0]
    logo = brand[1] if brand[1] != '' else 'logo_url'
    body = {
        'name': name,
        'logo': logo
    }
    add_brand = common.req.request_post('/store/manage/goodsBrand/save', body=body, token=admin_token)
    if add_brand['code'] == 200:
        print(f'品牌{name}添加成功')
    else:
        print(f'品牌{name}添加失败, {add_brand["text"]}')
    time.sleep(0.3)
