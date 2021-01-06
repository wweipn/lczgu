# -*- coding: utf-8 -*-
# @Time: 2021/1/4 12:33
# @Author: Waipang

import pytest
import allure
import os


def login(username=None, password=None):
    """模拟登录"""
    user = "linux超"
    pwd = "123456"
    if user == username and pwd == password:
        return {"code": 1001, "msg": "登录成功", "data": None}
    elif "" == password or password is None and username:
        return {"code": 1002, "msg": "密码不能为空", "data": None}
    elif "" == username or username is None and password:
        return {"code": 1003, "msg": "用户名不能为空", "data": None}
    else:
        return {"code": 1004, "msg": "用户名或密码错误", "data": None}


@allure.step("输入用户名")
def input_username(user):
    print("输入用户名")
    return user


@allure.step("输入密码")
def input_password(pwd):
    print("输入密码")
    return pwd


login_success_data = [
    # 测试数据
    {
        "case": "用户名正确, 密码正确",
        "user": "linux超",
        "pwd": "123456",
        "expected": {"code": 1001, "msg": "登录成功", "data": None}
    }
]

login_fail_data = [
    {
        "case": "用户名正确, 密码为空",
        "user": "linux超",
        "pwd": "",
        "expected": {"code": 1002, "msg": "密码不能为空", "data": None}
    },
    {
        "case": "用户名为空, 密码正确",
        "user": "",
        "pwd": "linux超哥",
        "expected": {"code": 1003, "msg": "用户名不能为空", "data": None}
    },
    {
        "case": "用户名错误, 密码错误",
        "user": "linux",
        "pwd": "linux",
        "expected": {"code": 1004, "msg": "用户名或密码错误", "data": None}
    }
]

username_none = [
    {
        "case": "缺省用户名参数",
        "pwd": "123456",
        "expected": {"code": 1003, "msg": "用户名不能为空", "data": None}
    }
]
password_none = [
    {
        "case": "缺省密码参数",
        "user": "linux超",
        "expected": {"code": 1002, "msg": "密码不能为空", "data": None}
    }
]
# 改变输出结果
ids_login_success_data = [
    "测试{}用户名:{}密码{}期望值{}".
        format(data["case"], data["user"], data["pwd"], data["expected"]) for data in login_success_data
]
ids_login_fail_data = [
    "测试{}用户名:{}密码{}期望值{}".
        format(data["case"], data["user"], data["pwd"], data["expected"]) for data in login_fail_data
]
ids_username_none = [
    "测试{}密码{}期望值{}".
        format(data["case"], data["pwd"], data["expected"]) for data in username_none
]
ids_password_none = [
    "测试{}用户名:{}期望值{}".
        format(data["case"], data["user"], data["expected"]) for data in password_none
]


@allure.feature("登录模块")
class TestLogin(object):

    @allure.severity(allure.severity_level.BLOCKER)
    @allure.story("测试登录成功")
    @allure.title("登录成功场景-{data}")
    @pytest.mark.parametrize("data", login_success_data, ids=ids_login_success_data)
    def test_login_success(self, data):
        """测试登录成功"""
        user = input_username(data["user"])
        pwd = input_password(data["pwd"])
        result = login(user, pwd)
        assert result == data["expected"]

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("测试登录失败")
    @pytest.mark.parametrize("data", login_fail_data, ids=ids_login_fail_data)
    def test_login_fail(self, data):
        """测试用户名或密码错误"""
        user = input_username(data["user"])
        pwd = input_password(data["pwd"])
        result = login(user, pwd)
        assert result == data["expected"]

    @allure.severity(allure.severity_level.MINOR)
    @allure.story("测试用户名参数缺失")
    @pytest.mark.parametrize("data", username_none, ids=ids_username_none)
    def test_username_none(self, data):
        """测试缺省用户名"""
        pwd = input_password(data["pwd"])
        result = login(password=pwd)
        assert result == data["expected"]

    @allure.severity(allure.severity_level.MINOR)
    @allure.story("测试密码参数缺失")
    @pytest.mark.parametrize("data", password_none, ids=ids_password_none)
    def test_password_none(self, data):
        """测试缺省密码"""
        user = input_username(data["user"])
        result = login(username=user)
        assert result == data["expected"]

    @allure.severity(allure.severity_level.MINOR)
    @allure.story("测试初始化地址")
    @allure.testcase("https://www.cnblogs.com/linuxchao/", "测试用例地址")
    def test_init_url(self, init_url):
        flag = init_url
        assert flag is True

    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("测试失败用例与用例中添加附件")
    @allure.link("https://www.cnblogs.com/linuxchao/", name="bug链接")
    @allure.description("这是一个一直执行失败的测试用例")
    def test_failed(self):
        """你也可以在这里添加用例的描述信息，但是会被allure.description覆盖"""
        try:
            assert False
        except AssertionError as e:
            with open("attach.png", "rb") as f:
                context = f.read()
                allure.attach(context, "错误图片", attachment_type=allure.attachment_type.PNG)
            raise e

    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.story("测试broken用例")
    @allure.issue("https://www.cnblogs.com/linuxchao/", "错误链接")
    def test_broken(self):
        """broken"""
        with open("broken.json", "r", encoding='utf8') as f:
            f.read()

    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.story("测试无条件跳过测试用例")
    @pytest.mark.skip(reason="无条件跳过")
    def test_skip(self):
        """skip"""
        pass


if __name__ == '__main__':
    pytest.main(["-vsq",
                 "--alluredir", "./allure-results", ])
    os.system(r"allure generate --clean ./allure-results -o ./allure-report")