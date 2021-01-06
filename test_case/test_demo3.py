# -*- coding: utf-8 -*-
# @Time: 2021/1/4 10:18
# @Author: Waipang

def setup_module():
    print("\nsetup_module，只执行一次，当有多个测试类的时候使用")


def teardown_module():
    print("\nteardown_module，只执行一次，当有多个测试类的时候使用")


class TestPytest1(object):

    @classmethod
    def setup_class(cls):
        print("\nsetup_class1，只执行一次")

    @classmethod
    def teardown_class(cls):
        print("\nteardown_class1，只执行一次")

    def setup_method(self):
        print("\nsetup_method1，每个测试方法都执行一次")

    def teardown_method(self):
        print("teardown_method1，每个测试方法都执行一次")

    def test_three(self):
        print("test_three，测试用例")

    def test_four(self):
        print("test_four，测试用例")


class TestPytest2(object):

    @classmethod
    def setup_class(cls):
        print("\nsetup_class2，只执行一次")

    @classmethod
    def teardown_class(cls):
        print("\nteardown_class2，只执行一次")

    def setup_method(self):
        print("\nsetup_method2，每个测试方法都执行一次")

    def teardown_method(self):
        print("teardown_method2，每个测试方法都执行一次")

    def test_two(self):
        print("test_two，测试用例")

    def test_one(self):
        print("test_one，测试用例")
