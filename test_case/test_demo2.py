import allure


@allure.feature('这是一个测试')
def test_al():
    print('hello world')
    assert 1 > 2
