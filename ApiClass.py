import requests
import json
import csv
import time
import Config
import Captchas


base_url, user_url, shop_url, admin_url = Config.env()

"""
登录函数
"""


def login(pf='user'):  # pf(平台):admin, user; source(数据来源): 0: 手动输入, 1: 文件获取;
    admin_uid = Config.admin_uid
    user_uid = Config.user_uid
    user_dic = {}
    user_token_dic = {}
    # 判断所属平台,走不同的请求配置
    if pf == 'admin':
        Captchas.captchas(pf=pf)
        res = requests.get(f'{admin_url}/admin/systems/admin-users/login?username=wuweipeng&password=e10adc3949ba59abbe56e057f20f883e'
                           f'&scene=LOGIN&uuid={admin_uid}&captcha=1111', headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/84.0.4147.105 Safari/537.36"})
        response = json.loads(res.text)
        admin_token = response['access_token']
        return admin_token
    elif pf == 'user':
        # 读取csv文件中的用户账号和密码,并写入user_dic字典中
        with open('D:/user_list.csv', 'r', encoding='utf-8') as userListFile:
            csv_file_read = csv.reader(userListFile)
            next(csv_file_read)
            for row in csv_file_read:
                account = row[0]
                password = row[1]
                user_dic[account] = password
        time_num = 0 if len(user_dic) == 1 else 0.2
        for account, password in user_dic.items():
            Captchas.captchas(pf=pf)
            res = requests.post(f'{user_url}/passport/login?scene=LOGIN&username={account}'
                                f'&password={password}&captcha=1111&uuid={user_uid}',
                                headers={
                                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                                  "like Gecko) "
                                                  "Chrome/84.0.4147.105 Safari/537.36"})
            response = json.loads(res.text)
            if res.status_code == 200:
                user_token = response['access_token']
                user_token_dic[account] = user_token
                print(f'账号: {account}登录成功!')
            else:
                print(f'账号: {account}登录失败!\n返回内容: {res.text}')
                continue
            time.sleep(time_num)
        return user_token_dic


"""
接口请求类
"""


class ApiRequests:
    def __init__(self, pf='user', source=1):
        self.pf = pf
        self.source = source
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/84.0.4147.105 Safari/537.36"}
        if pf == 'admin':
            self.host = admin_url
            self.AdminToken = login(pf)
        elif pf == 'user':
            self.host = user_url
        elif pf == 'shop':
            self.host = shop_url

    def requests(self, url, content=None, method='post'):
        # 遍历user_dic里面的所有数据,并参数化请求头中的token实现多用户调用
        if self.pf == "user":
            trade_token_dic = login(self.pf, self.source)
            for user in trade_token_dic.items():
                self.headers['token'] = user[1]
                if method == 'post':
                    res = requests.post(f'{self.host}{url}', headers=self.headers, json=content)
                elif method == 'get':
                    res = requests.get(f'{self.host}{url}', headers=self.headers, json=content)
                time.sleep(0.5)
        elif self.pf == 'admin':
            self.headers['token'] = self.AdminToken
            if method == 'post':
                res = requests.post(f'{self.host}{url}', headers=self.headers, json=content)
            elif method == 'get':
                res = requests.get(f'{self.host}{url}', headers=self.headers, json=content)
            response = json.loads(res.text)
            return response


if __name__ == '__main__':
    login(pf='user')
