from common.Request import ApiRequests
import random
import common


def get_ran_address_info():
    """
    随机生成收货地址ID
    :return:
    """
    # 调用查询地址接口获取省份列表, 随机取其中一条数据
    province_list = common.req.request_get('/store/common/area/list/0')
    province = random.choice(province_list['text']['data'])
    province_id = province['id']

    # 调用查询地址接口获取城市列表, 随机取其中一条数据
    city_list = common.req.request_get(f"/store/common/area/list/{province_id}")
    city = random.choice(city_list['text']['data'])
    city_id = city['id']

    # 调用查询地址接口获取区列表, 随机取其中一条数据
    county_list = common.req.request_get(f"/store/common/area/list/{city_id}")
    county = random.choice(county_list['text']['data'])
    county_id = county['id']
    return province_id, city_id, county_id


def add_address(mobile):
    """
    添加收货地址
    :param mobile: 手机号
    :return:
    """
    common.account.user_login([mobile])
    user_token = common.account.get_user_token(mobile)
    province_id, city_id, county_id = get_ran_address_info()
    body = {
        "addr": "稻兴环球科创中心",
        "addressName": "公司地址",
        "cityId": city_id,
        "countyId": county_id,
        "mobile": mobile,
        "name": f'test_{mobile[-3:]}',
        "provinceId": province_id
    }
    res = common.req.request_post('/store/api/user/addr/address', body=body, token=user_token)
    return res


if __name__ == '__main__':
    address_add = add_address('17199990001')
    print(address_add['text'])