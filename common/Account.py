import requests
import json
import csv
from common.Database import Database
from common.Request import ApiRequests


"""
账户类,包含商家/用户/管理后台的注册/登录以及获取token的方法 
"""


class Account(ApiRequests, Database):

    def get_userinfo(self, **kwargs):
        info = self.request_get('/store/api/account/userinfo', **kwargs)
        recommend_id = info['text']['data']['recommendId']
        return recommend_id

    """
    获取挂关系接口响应头token, 用于传递数据给注册接口的内部方法
    """
    def set_recommend(self, mobile):
        # 调用父类"Database"的查询方法,执行sql语句,获取查询结果
        select_account_id = self.select_one(sql=f"""
        SELECT id FROM user_account WHERE mobile = {mobile}
        """)
        # 通过查询结果的下标获取推荐人的AccountId
        recommend_id = select_account_id[0]
        # # 关闭数据库连接
        # db_content.close()
        # 调用绑定关系接口, 获取响应头的token后返回
        res = self.request_post('/store/api/account/recommend', params={'recommend_id': recommend_id})
        access_token = res.headers['AccessToken']
        return res, access_token

    """
    用户注册方法
    所需参数
        mobile: 注册手机号
        r_mobile: 推荐人手机号
    """
    def user_register(self,  mobile, r_mobile):
        access_token = self.set_recommend(r_mobile)
        body = {
             'code': '111111',  # 验证码(当前测试环境去掉了校验,默认传111111)
             'mobile': mobile,  # 手机号
             'source': 'IOS'  # ANDROID, H5, IOS, MINI
        }
        res = self.request_post('/store/api/account/login', body=body, access_token=access_token)
        if res['text']['code'] == 200:
            print(f'账号【{mobile}】注册成功')
        else:
            print(f"账号【{mobile}】注册失败，详情: {res['text']}")
        return res

    """
    管理后台登录
    """
    def admin_login(self, username='admin', password='123456'):
        params = {'username': username,
                  'password': password}
        res = requests.post(f'{self.host}/store/manage/account/login', params=params)
        response = json.loads(res.text)
        admin_token = response['data']['access_token']
        with open('D:/admin_token.csv', 'w', newline='', encoding='utf-8') as AdminTokenFiles:
            admin_token_write = csv.writer(AdminTokenFiles)
            admin_token_write.writerow([admin_token])

    """
    用户端登录
    所需参数
        source: 0: 获取传入的用户列表, 1: 获取文件中的账号
        user_list: 当source=1时, 需要传参,如:['mobile1', 'mobile2']
    """
    def user_login(self, source, user_list=None):
        login_user_list = []
        # 读取csv文件中的用户账号并写入login_user_list
        if source == 1:
            with open('D:/user_list.csv', 'r', encoding='utf-8') as UserListFile:
                csv_file_read = csv.reader(UserListFile)
                next(csv_file_read)
                for row in csv_file_read:
                    account = row[0]
                    login_user_list.append(account)
        # 将传入的参数直接赋值给login_user_list
        elif source == 0 and user_list is not None:
            login_user_list = user_list
        # 从login_user_list中取出登录账号,逐一登录完毕后把token储存到csv文件中
        with open('D:/User_token.csv', 'w', newline='', encoding='utf-8') as UserTokenFile:
            csv_file_writer = csv.writer(UserTokenFile)
            csv_file_writer.writerow(['account', 'token'])
            for account in login_user_list:
                body = {'mobile': account, 'code': '111111', "source": "ANDROID"}
                res = self.request_post('/store/api/account/login', body=body)
                if res['text']['code'] != 200:
                    print(f'【{account}】登录失败', res['text'])
                else:
                    token = res['text']['data']['accessToken']
                    csv_file_writer.writerow([account, token])

    """
    商家登录
    所需参数
        username: 登录账号
        password: 密码
    """
    def shop_login(self, username, password):
        params = {'username': username,
                  'password': password}
        res = self.request_post('/store/seller/account/login', params=params)
        shop_token = res['text']['data']['access_token']
        with open('D:/shop_token.csv', 'w', newline='', encoding='utf-8') as shopTokenFiles:
            admin_token_write = csv.writer(shopTokenFiles)
            admin_token_write.writerow([shop_token])

    """
    获取商户token
    """
    @staticmethod
    def get_shop_token():
        # 读取存储管理后台token的csv文件,并返回token信息
        with open('D:/admin_token.csv', 'r', encoding='utf-8') as ShopTokenRead:
            csv_file_read = csv.reader(ShopTokenRead)
            for row in csv_file_read:
                shop_token = row[0]
        return shop_token

    """
    获取用户token
    """
    @staticmethod
    def get_user_token(mobile=None):
        user_token_list = []
        # 读取存储token的csv文件,并写入字段user_token_dic中
        with open('D:/User_token.csv', 'r', encoding='utf-8') as UserTokenRead:
            csv_file_read = csv.reader(UserTokenRead)
            next(csv_file_read)
            for row in csv_file_read:
                account = row[0]
                token = row[1]
                user_token_list.append((account, token))
        # 如果没有传入mobile参数,返回user_token_dic,否则返回账户对应的token
        if mobile is None:
            return user_token_list
        else:
            for i in user_token_list:
                if i[0] == mobile:
                    return i[1]

    """
    获取管理后台token
    """
    @staticmethod
    def get_admin_token():
        # 读取存储管理后台token的csv文件,并返回token信息
        with open('D:/admin_token.csv', 'r', encoding='utf-8') as AdminTokenRead:
            csv_file_read = csv.reader(AdminTokenRead)
            for row in csv_file_read:
                admin_token = row[0]
        return admin_token

