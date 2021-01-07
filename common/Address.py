from common.Request import ApiRequests
import random


class Address(ApiRequests):

    # 随机获取地址方法
    def get_ran_address_info(self):
        # 调用查询地址接口获取省份列表, 随机取其中一条数据
        province_list = self.request_get('/store/common/area/list/0')
        province = random.choice(province_list['text']['data'])
        province_id = str(province['id'])

        # 调用查询地址接口获取城市列表, 随机取其中一条数据
        city_list = self.request_get(f"/store/common/area/list/{province_id}")
        city = random.choice(city_list['text']['data'])
        city_id = str(city['id'])

        # 调用查询地址接口获取区列表, 随机取其中一条数据
        county_list = self.request_get(f"/store/common/area/list/{city_id}")
        county = random.choice(county_list['text']['data'])
        county_id = str(county['id'])
        return province_id, city_id, county_id

    # 添加地址方法
    def add_address(self, token=None):
        province_id, city_id, county_id = self.get_ran_address_info()
        body = {
            "addr": "稻兴环球科创中心",
            "addressName": "公司地址",
            "cityId": city_id,
            "countyId": county_id,
            "mobile": "18123929299",
            "name": "Waipang",
            "provinceId": province_id
        }
        add_address = self.request_post('/store/api/user/addr/address', body=body, token=token)
        return add_address


