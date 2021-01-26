import common
import allure
import pytest
import time

login_value, login_data = common.file_read(file_path='D:/PythonProject/Lczgu/test_file/login_data.csv')


@allure.feature('账户模块')
class TestAccount:

    @allure.title('验证不绑定关系注册')
    @allure.description('这个是用例的描述内容')
    @allure.story('不绑定关系注册')
    def test_register(self):
        with allure.step('注册'):
            register, mobile = common.account.user_register()
            allure.attach(f"注册账号:{mobile}", '请求参数')
            allure.attach(f"返回结果:{register['text']}", '返回结果')
            assert register['text']['code'] == 200
            assert register['text']['desc'] == '请求成功'
            time.sleep(1)

    @allure.title('验证绑定关系注册')
    @allure.story('绑定关系注册')
    def test_has_recommend_register(self):
        with allure.step('注册'):
            register, mobile = common.account.user_register(r_mobile='18123929299')
            allure.attach(f"注册账号: {mobile}, 邀请人账号: 18123929299", '请求参数')
            allure.attach(f"{register['text']}", '返回结果')
            assert register['text']['code'] == 200
            assert register['text']['desc'] == '请求成功'
            # 查询注册账号的邀请人account_id
            register_recommend_id = common.db.select_one(f"""
            select 
                recommend_id_lv1
            from 
                user_info 
            where 
                account_id = (SELECT id FROM user_account WHERE mobile = '{mobile}')
            """)[0]
            # 查询邀请人的account_id
            r_mobile_account_id = common.db.select_one(f"""
            SELECT id FROM user_account WHERE mobile = '18123929299'
            """)[0]
            assert register_recommend_id == r_mobile_account_id

    @pytest.mark.parametrize(login_value, login_data)
    @allure.title('{text}')
    @allure.story('验证登录功能')
    def test_login(self, url, code, mobile, source, text, test):
        body = {
            'mobile': mobile,
            'code': code,
            'source': source
        }
        with allure.step(f'请求接口{url}'):
            allure.attach(str(body), '请求参数')
            api = common.req.request_post(url=url, body=body)
            allure.attach(str(api['text']), '返回结果')
            assert eval(test)

