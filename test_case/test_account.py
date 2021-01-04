import common
import allure
import pytest

# 获取数据库中最新的登录账号
last_number = common.db.select_one(sql="""
SELECT mobile FROM user_account WHERE mobile LIKE '1719999%' ORDER BY mobile desc LIMIT 1
""")[0]
register_account_list = [str(int(last_number) + 1)]
print(register_account_list)


@pytest.mark.parametrize('mobile', register_account_list)
@allure.feature('账户模块')
class TestAccount:
    @allure.story('注册功能')
    def test_register(self, mobile):
        with allure.step(f'账号注册【{mobile}】'):
            body = {'source': 'ANDROID', 'mobile': mobile, 'code': '111111'}
            allure.attach(f'请求参数:{body}', f'请求接口(/store/api/account/login)')  # attach可以打印一些附加信息
            login = common.req.request_post('/store/api/account/login', body=body)
            allure.attach(f"返回结果:{login['text']}", '返回参数')
            assert login['text']['code'] == 200
            assert login['text']['desc'] == '请求成功'

