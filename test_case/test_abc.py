import Request
import Account
import Captchas


def test_register():
    # res = ApiClass.ApiRequests()  # 实例化请求接口类
    # Account.login()  # 登录
    # get_short_url = res.requests(url='/distribution/su/get-short-url')['text']  # 获取短连接
    # su = get_short_url['message'][-6:]  # 通过下标获取su码
    # Account.user_token_dic = {}  # 清除登录态

    res = Request.ApiRequests()  # 实例化请求接口类1
    su_code_get = res.requests(url=f'/distribution/su/visit?su=2umuia', method='get')  # 挂绑定关系
    assert su_code_get['code'] == 200

    get_captcha = Captchas.captchas(pf='user', use_for='REGISTER')  # 获取图形验证码
    print('获取图形验证码成功') if get_captcha['code'] == 200 else print('获取图形验证码失败', get_captcha)

    send_sms_code = res.requests(url='/passport/register/smscode/17199990340')  # 获取短信验证码
    # print('获取短信验证码成功') if send_sms_code['code'] == 200 else print('获取短信验证码失败')
    print(send_sms_code['url'], '\n', send_sms_code['header'], '\n')

    register_result = res.requests(url='/passport/smscode/17199990340?scene=REGISTER&sms_code=1111', method='get')  # 注册
    print('注册成功') if register_result['code'] == 200 else print('注册失败', register_result['text'])


def test_kwargs(a, b, **kwargs):
    print(a, b)
    print(kwargs['content'], kwargs[kwargs.keys()])


test_kwargs(1, 2, content=2)


