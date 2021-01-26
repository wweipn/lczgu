# -*- coding: utf-8 -*-
# @Time: 2020/12/31 18:00
# @Author: Waipang

import common
import allure
import time
import pytest


@allure.feature('用户地址')
class TestAddress:
    add_address_k, add_address_v = common.testcase_file_read('add_address_data.csv')

    @pytest.mark.parametrize(add_address_k, add_address_v)
    @allure.title('验证添加收货地址')
    @allure.story('添加收货地址')
    def test_add_address(self, mobile):

        with allure.step('登录账号'):
            common.account.user_login(user_list=[mobile])
            token = common.account.get_user_token(mobile)
            time.sleep(0.5)

        with allure.step('获取地址信息'):
            get_area = common.req.request_get(url='/store/common/area/list/0', token=token)
            allure.attach(f"{get_area['text']}", '返回参数')
            assert get_area['code'] == 200
            time.sleep(0.5)

        with allure.step('添加地址'):
            province_id, city_id, county_id = common.address.get_ran_address_info()
            body = {
                "addr": "稻兴环球科创中心",
                "addressName": "公司地址",
                "isDef": "1",
                "cityId": city_id,
                "countyId": county_id,
                "mobile": mobile,
                "name": "Waipang",
                "provinceId": province_id
            }
            add_address = common.req.request_post(url='/store/api/user/addr/address', token=token, body=body)
            assert add_address['status_code'] == 200, f"接口响应异常, 返回参数{add_address['text']}"
            assert add_address['code'] == 200
            allure.attach(f'{body}', '请求参数')
            allure.attach(f'{add_address}', '返回结果')
            # assert add_address['code'] == 200
            time.sleep(0.5)

        with allure.step('查询收货地址是否添加成功'):
            find_address = common.req.request_get('/store/api/user/addr', token=token)
            allure.attach(f"{find_address['text']}", '返回结果')
            assert find_address['code'] == 200
            address_result = str(find_address['data'])
            assert city_id in address_result, '添加的城市ID不在地址列表中'
            assert county_id in address_result, '添加的区/县ID不在地址列表中'
            assert province_id in address_result, '添加的省份ID不在地址列表中'
            time.sleep(0.5)

