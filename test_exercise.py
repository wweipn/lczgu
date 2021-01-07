# -*- coding: utf-8 -*-
# @Time: 2021/1/4 12:33
# @Author: Waipang

import common
import os

# body = {'code': 200, 'desc': '请求成功', 'data': [{'id': '1', 'accountId': '1342301836354764801', 'name': 'Waipang', 'provinceId': 640000, 'cityId': 640500, 'countyId': 640522, 'provinceName': '宁夏回族自治区', 'cityName': '中卫市', 'countyName': '海原县', 'addr': '稻兴环球科创中心', 'mobile': '18123929299', 'addressName': '公司地址', 'isDef': 1, 'createTime': '2020-12-30 15:04:28', 'updateTime': '2020-12-31 11:45:10'}, {'id': '2', 'accountId': '1342301836354764801', 'name': 'Waipang', 'provinceId': 510000, 'cityId': 513400, 'countyId': 513434, 'provinceName': '四川省', 'cityName': '凉山彝族自治州', 'countyName': '越西县', 'addr': '稻兴环球科创中心', 'mobile': '18123929299', 'addressName': '公司地址', 'isDef': 0, 'createTime': '2021-01-06 20:11:45', 'updateTime': '2021-01-06 20:11:45'}, {'id': '3', 'accountId': '1342301836354764801', 'name': 'Waipang', 'provinceId': 610000, 'cityId': 610700, 'countyId': 610723, 'provinceName': '陕西省', 'cityName': '汉中市', 'countyName': '洋县', 'addr': '稻兴环球科创中心', 'mobile': '18123929299', 'addressName': '公司地址', 'isDef': 0, 'createTime': '2021-01-06 20:12:40', 'updateTime': '2021-01-06 20:12:40'}, {'id': '4', 'accountId': '1342301836354764801', 'name': 'Waipang', 'provinceId': 430000, 'cityId': 430400, 'countyId': 430407, 'provinceName': '湖南省', 'cityName': '衡阳市', 'countyName': '石鼓区', 'addr': '稻兴环球科创中心', 'mobile': '18123929299', 'addressName': '公司地址', 'isDef': 0, 'createTime': '2021-01-06 20:14:46', 'updateTime': '2021-01-06 20:14:46'}, {'id': '5', 'accountId': '1342301836354764801', 'name': 'Waipang', 'provinceId': 150000, 'cityId': 150200, 'countyId': 150203, 'provinceName': '内蒙古自治区', 'cityName': '包头市', 'countyName': '昆都仑区', 'addr': '稻兴环球科创中心', 'mobile': '18123929299', 'addressName': '公司地址', 'isDef': 0, 'createTime': '2021-01-06 21:50:18', 'updateTime': '2021-01-06 21:50:18'}]}
# common.account.user_login(user_list=['18123929299'])


a, b, c = common.address.get_ran_address_info()
print(a, type(a),
      b,
      c)