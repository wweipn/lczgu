import common
import allure


@allure.feature('查询账号余额')
class TestAccount:
    @allure.story('登录')
    def test_login(self):
        account = common.Account()
        req = common.ApiRequests()
        account.user_login(source=0, user_list=['18123929299'])
        token_list = account.get_user_token()
        for mobile, token in token_list.items():
            get_address = req.request_get('/store/api/user/addr', token=token)
            with allure.step("查询收货地址"):  # 步骤1
                allure.attach('返回状态码', get_address['code'])
                allure.attach('返回参数', get_address['text'])
                # assert get_address['code'] == 200
                # assert get_address['text']['data'] != []
