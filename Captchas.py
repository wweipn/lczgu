import requests
import json
import time
import Config


# 图片验证码方法
def captchas(pf, use_for='LOGIN'):  # user_for(验证方式): Register:注册, LOGIN:登录
    base_url = Config.env()[0]
    header = {'Accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8'}
    now_time = str(int(time.time() * 1000))
    if pf == 'user':
        uid = Config.user_uid
    elif pf == 'admin':
        uid = Config.admin_uid
    result = requests.get(f'{base_url}/captchas/{uid}/{use_for}?r={now_time}', headers=header)
    return {'code': result.status_code, 'url': result.url}


if __name__ == '__main__':
    print(captchas(pf='user', use_for='REGISTER'))
