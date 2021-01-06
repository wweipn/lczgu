# -*- coding: utf-8 -*-
# @Time: 2020/12/31 18:00
# @Author: Waipang

import common
import allure
import pytest


@allure.feature('验证收货地址功能')
class TestAddress:

    @allure.title('测试正常添加收货地址')
    def test_add_address(self):
        login = common.account.user_login()
        api = common.address.add_address()
        assert api['code'] == 200
        assert common.db.select_one()