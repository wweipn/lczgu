import requests
import json
import time
import Config

base_url = Config.env()[0]
header = {'Accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8'}


def captchas(pf, uf='login', uid=None):
    now_time = str(int(time.time() * 1000))
    if uf == 'login':
        if pf == 'user':
            uid = Config.user_uid
        elif pf == 'admin':
            uid = Config.admin_uid
        requests.get(f'{base_url}/captchas/{uid}/LOGIN?r={now_time}', headers=header)
    else:
        return '验证类型异常,请填写正确的参数'