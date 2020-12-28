import requests
import json
import csv
import Config


"""
登录类
"""


class Account:

    def __init__(self):
        self.host = Config.get_host()

    # 用户注册方法
    def user_register(self,  mobile):
        params = {'code': '111111',  # 验证码
                  'mobile': mobile,  # 手机号
                  'source': 'IOS'}  # ANDROID, H5, IOS, MINI
        res = requests.post(f'{self.host}/store/manage/account/login', params=params)
        response = json.loads(res.text)
        if response['code'] == 200:
            print(f'账号【{mobile}】注册成功')
        else:
            print(f'账号【{mobile}】注册失败，详情: {response}')

    # 管理后台登录方法
    def admin_login(self, username='admin', password='123456'):
        params = {'username': username,
                  'password': password}
        res = requests.post(f'{self.host}/store/manage/account/login', params=params)
        response = json.loads(res.text)
        admin_token = response['data']['access_token']
        with open('D:/admin_token.csv', 'w', newline='', encoding='utf-8') as AdminTokenFiles:
            admin_token_write = csv.writer(AdminTokenFiles)
            admin_token_write.writerow([admin_token])

    # 用户端登录方法
    def user_login(self, source):  # source: 1: 获取文件中的账号, 2: 手输账号密码
        user_dic = []
        # 读取csv文件中的用户账号和密码,并写入user_dic字典中
        if source == 1:
            with open('D:/user_list.csv', 'r', encoding='utf-8') as UserListFile:
                csv_file_read = csv.reader(UserListFile)
                next(csv_file_read)
                for row in csv_file_read:
                    account = row[0]
                    user_dic.append(account)
        # 使用手动输入的手机号码进行登录
        elif source == 0:
            account = input('账号:')
            user_dic.append(account)
        # 从user_dic中取出登录账号,逐一登录完毕后把token储存到csv文件中
        with open('D:/User_token.csv', 'w', newline='', encoding='utf-8') as UserTokenFile:
            csv_file_writer = csv.writer(UserTokenFile)
            csv_file_writer.writerow(['account', 'token'])
            for account in user_dic:
                params = {'mobile': account, 'code': '111111'}
                res = requests.post(f'{self.host}/store/api/account/login', params=params)
                response = json.loads(res.text)
                if res.status_code != 200:
                    print(f'【{account}】登录失败', response)
                else:
                    token = response['data']['accessToken']
                    csv_file_writer.writerow([account, token])

    # 商家登录方法
    def shop_login(self, username, password):
        params = {'username': username,
                  'password': password}
        res = requests.post(f'{self.host}/store/seller/account/login', params=params)
        response = json.loads(res.text)
        shop_token = response['data']['access_token']
        with open('D:/shop_token.csv', 'w', newline='', encoding='utf-8') as shopTokenFiles:
            admin_token_write = csv.writer(shopTokenFiles)
            admin_token_write.writerow([shop_token])

    # 获取商户token方法
    @staticmethod
    def get_shop_token():
        # 读取存储管理后台token的csv文件,并返回token信息
        with open('D:/admin_token.csv', 'r', encoding='utf-8') as ShopTokenRead:
            csv_file_read = csv.reader(ShopTokenRead)
            for row in csv_file_read:
                shop_token = row[0]
        return shop_token

    # 获取用户token方法
    @staticmethod
    def get_user_token(mobile):
        user_token_dic = {}
        # 读取存储token的csv文件,通过传递mobile参数获取文件中存储的token值
        with open('D:/User_token.csv', 'r', encoding='utf-8') as UserTokenRead:
            csv_file_read = csv.reader(UserTokenRead)
            next(csv_file_read)
            for row in csv_file_read:
                account = row[0]
                token = row[1]
                user_token_dic[account] = token
        return user_token_dic[mobile]

    # 获取管理后台token方法
    @staticmethod
    def get_admin_token():
        # 读取存储管理后台token的csv文件,并返回token信息
        with open('D:/admin_token.csv', 'r', encoding='utf-8') as AdminTokenRead:
            csv_file_read = csv.reader(AdminTokenRead)
            for row in csv_file_read:
                admin_token = row[0]
        return admin_token


a = Account()
a.user_register(mobile='17199990000')
