# -*- coding: utf-8 -*-
# @Time: 2021/1/4 12:33
# @Author: Waipang

import common


a = {"addNum": 2, "limitNum": 10, "chiefType": 0, "teamType": 0, "startDate": "2021-03-02", "name": "拼团活动(2021-03-02)", "title": "拼团活动(2021-03-02)", "goodsList": [{"activityNum": 10, "goodsId": 1353289358207119361, "price": 75.6, "skuId": 1353289360463654914, "sort": 99}, {"activityNum": 10, "goodsId": 1352064895671119874, "price": 20.93, "skuId": 1352064895679508481, "sort": 99}, {"activityNum": 10, "goodsId": 1353284848801837058, "price": 278.6, "skuId": 1353284848818614274, "sort": 99}, {"activityNum": 10, "goodsId": 1353289418403770370, "price": 66.5, "skuId": 1353289418810617857, "sort": 99}, {"activityNum": 10, "goodsId": 1353288909244624898, "price": 48.3, "skuId": 1353288909366259714, "sort": 99}, {"activityNum": 10, "goodsId": 1353289328767299585, "price": 66.5, "skuId": 1353289329694240769, "sort": 99}, {"activityNum": 10, "goodsId": 1353289297083527170, "price": 62.3, "skuId": 1353289298366984193, "sort": 99}, {"activityNum": 10, "goodsId": 1353288992883240962, "price": 62.3, "skuId": 1353288993302671362, "sort": 99}, {"activityNum": 10, "goodsId": 1353289377895182337, "price": 52.5, "skuId": 1353289378012622850, "sort": 99}, {"activityNum": 10, "goodsId": 1353289307254714369, "price": 279.3, "skuId": 1353289307384737794, "sort": 99}, {"activityNum": 10, "goodsId": 1353289297083527170, "price": 62.3, "skuId": 1353289299075821569, "sort": 99}, {"activityNum": 10, "goodsId": 1353289138136182785, "price": 48.3, "skuId": 1353289138324926466, "sort": 99}, {"activityNum": 10, "goodsId": 1353288892802953217, "price": 47.6, "skuId": 1353288893083971585, "sort": 99}, {"activityNum": 10, "goodsId": 1352065005553496065, "price": 17.5, "skuId": 1352065005561884673, "sort": 99}, {"activityNum": 10, "goodsId": 1353289095396225025, "price": 62.3, "skuId": 1353289096067313666, "sort": 99}, {"activityNum": 10, "goodsId": 1352798812506206209, "price": 70.0, "skuId": 1352798812518789122, "sort": 99}, {"activityNum": 10, "goodsId": 1353289189927448578, "price": 62.3, "skuId": 1353289190191689730, "sort": 99}, {"activityNum": 10, "goodsId": 1353289164941979650, "price": 59.5, "skuId": 1353289165420130305, "sort": 99}, {"activityNum": 10, "goodsId": 1352064919243108353, "price": 20.93, "skuId": 1352064919251496962, "sort": 99}, {"activityNum": 10, "goodsId": 1353289418403770370, "price": 66.5, "skuId": 1353289419536232449, "sort": 99}]}

a_list = []
for i in a["goodsList"]:
    sku_id = i['skuId']
    a_list.append(sku_id)

print(a_list)