# -*- coding: utf-8 -*-
# @Time: 2021/1/4 12:33
# @Author: Waipang

import common
import Config
import json
import time
import testDataCreate.productAdd

# 连接老系统数据库
old_db = common.Database()
old_db.database = Config.get_db(env='old_test')

data = "[{'url': 'http://lczgushop.oss-cn-shenzhen.aliyuncs.com/staticsueditor/B9402CDA62224195A7566587DDACF7A0.jpeg'}, {'url': 'http://lczgushop.oss-cn-shenzhen.aliyuncs.com/staticsueditor/F1A3EF4A442A4BE1A4A7F3B159E43551.jpeg'}, {'url': 'http://lczgushop.oss-cn-shenzhen.aliyuncs.com/staticsueditor/19FA6628DD9D4A72BDB17AFFD713003A.jpeg'}, {'url': 'http://lczgushop.oss-cn-shenzhen.aliyuncs.com/staticsueditor/9416F4F6B4CD45A48B12617E025BF7DF.jpeg'}, {'url': 'http://lczgushop.oss-cn-shenzhen.aliyuncs.com/staticsueditor/2F335F28715849EE8312746A5D1550FE.jpeg'}]"

data_1 = json.dumps(data)
print(data_1.replace("'", '"'))
