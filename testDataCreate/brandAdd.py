# -*- coding: utf-8 -*-
# @Time: 2021/1/19 14:34
# @Author: Waipang

import common
import time

admin_login = common.account.admin_login()
admin_token = common.account.get_admin_token()
print(admin_token)
result = common.db.select_all(sql=
                              """
    SELECT name, logo  FROM es_brand  group by es_brand.name
""")

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
    time.sleep(1)