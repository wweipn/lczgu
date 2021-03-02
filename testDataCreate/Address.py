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


def add_address(token):
    """
    添加收货地址
    :param token: 用户token
    :return:
    """
    province_id, city_id, county_id = get_ran_address_info()

    get_mobile = common.req.request_get(url='/store/api/account/userinfo', token=token)
    mobile = get_mobile['data']['mobile']
    name = get_mobile['data']['nickname']
    body = {
        "addr": "稻兴环球科创中心B座2001",
        "addressName": "公司地址",
        "cityId": city_id,
        "countyId": county_id,
        "mobile": mobile,
        "name": name,
        "provinceId": province_id,
        "isDef": 1
    }
    res = common.req.request_post('/store/api/user/addr/address', body=body, token=token)
    if res['code'] == 200:
        print(res['text'])
        return res['data']['id'], res['data']['provinceId']
    else:
        print(f"地址添加失败\n{res['text']}")
        return


if __name__ == '__main__':
    # 登录用户账号,并获取token
    user_token = common.user_token(mobile=19216850004)

    # 添加收货地址
    add_address(token=user_token)

