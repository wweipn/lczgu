# -*- coding: utf-8 -*-
# @Time: 2021/1/4 12:33
# @Author: Waipang

import common

admin_token = common.admin_token()
user_token = common.user_token(18123929299)

coupon_list = [1368812827028078593, 1368812949006827522, 1368812996960305154, 1368813027486449665, 1368813047686217729,
               1368813059811950594, 1368813072080289793, 1368813081286787073, 1368813093739675649]
for coupon in coupon_list:
    # body = {"couponId": coupon}
    request = common.req.request_get(url=f'/store/api/promotion/member-coupon/{coupon}/receive', token=user_token)
    print(request['text'])
