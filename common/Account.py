import csv
from common.Database import Database
from common.Request import ApiRequests
import os


class Account(ApiRequests, Database):
    """
    账户类,包含商家/用户/管理后台的注册/登录以及获取token的方法
    """
    # 定义文件路径
    cur_path = os.path.dirname(os.path.realpath(__file__))
    temp = os.path.dirname(cur_path)
    test_file_path = os.path.join(temp, 'test_file')

    # 定义存储token的文件
    user_list_file = os.path.join(test_file_path, 'user_list.csv')
    user_token_file = os.path.join(test_file_path, 'user_token.csv')
    shop_token_file = os.path.join(test_file_path, 'shop_token.csv')
    admin_token_file = os.path.join(test_file_path, 'admin_token.csv')

    def get_userinfo(self, mobile):
        """
        查询用户信息(目前返回值只有推荐码ID的参数,后期需要再进行调整)
        :param mobile: 手机号
        :return: 推荐码
        """
        body = {
            "code": "111111",
            "mobile": mobile,
            "source": "ANDROID"
        }
        login = self.request_post(url='/store/api/account/login', body=body)
        token = login['rep_header']['accessToken']
        get_info = self.request_get('/store/api/account/userinfo', token=token)
        recommend_id = get_info['text']['data']['recommendId']
        return recommend_id

    def get_new_mobile(self):
        """
        获取数据库中最新的登录账号
        """
        last_number = self.select_one(sql="""
        SELECT 
            mobile 
        FROM 
            user_account 
        WHERE 
            mobile LIKE '19216850%' 
        ORDER BY mobile desc LIMIT 1
        """)[0]
        new_mobile = str(int(last_number) + 1)
        return new_mobile

    def set_recommend(self, mobile):
        """
        获取注册绑定关系的token
        :param mobile: 传入推荐人手机号后,调用get_userinfo方法获取推荐码
        :return : 返回的access_token用于登录接口的请求头的token,传入后会绑定用户关系
        """
        recommend_id = self.get_userinfo(mobile)
        # 调用绑定关系接口, 获取响应头的AccessToken
        res = self.request_post('/store/api/account/recommend', params={'recommendId': recommend_id})
        access_token = res['rep_header']['AccessToken']
        return access_token

    def user_register(self, r_mobile=None):
        """
        用户注册
        :param r_mobile: 推荐人手机号
        :return: res: 参考request_post方法返回值, mobile: 从get_new_mobile方法获取到的最新手机号
        """
        mobile = self.get_new_mobile()
        access_token = None
        if r_mobile is not None:
            access_token = self.set_recommend(r_mobile)
        else:
            pass
        body = {
            'code': '111111',  # 验证码(当前测试环境去掉了校验,默认传111111)
            'mobile': mobile,  # 手机号
            'source': 'IOS'  # ANDROID, H5, IOS, MINI
        }
        res = self.request_post('/store/api/account/login', body=body, token=access_token)
        print(f'账号【{mobile}】注册成功，邀请人手机号：{r_mobile}')
        return res

    def admin_login(self, username='admin', password='123456'):
        """
        管理后台登录
        :param username: 管理后台账号
        :param password: 管理后台密码
        :return:
        """
        body = {'username': username,
                'password': password}
        res = self.request_post('/store/manage/account/login', body=body)
        admin_token = res['rep_header']['AccessToken']
        with open(self.admin_token_file, 'w', newline='', encoding='utf-8') as AdminTokenFiles:
            admin_token_write = csv.writer(AdminTokenFiles)
            admin_token_write.writerow([admin_token])

    def user_login(self, user_list=None, source=0):
        """
        用户端登录
        :param source: 0: 获取传入的用户列表, 1: 获取文件中的账号
        :param user_list: 当source=0时, 需要传参,如:['mobile1', 'mobile2']
        :return:
        """
        login_user_list = []
        # 读取csv文件中的用户账号并写入login_user_list
        if source == 1:
            with open(self.user_list_file, 'r', encoding='utf-8') as UserListFile:
                csv_file_read = csv.reader(UserListFile)
                next(csv_file_read)
                for row in csv_file_read:
                    account = row[0]
                    login_user_list.append(account)
        # 将传入的参数直接赋值给login_user_list
        elif source == 0 and user_list is not None:
            login_user_list = user_list
        # 从login_user_list中取出登录账号,逐一登录完毕后把token储存到csv文件中
        with open(self.user_token_file, 'w', newline='', encoding='utf-8') as UserTokenFile:
            csv_file_writer = csv.writer(UserTokenFile)
            csv_file_writer.writerow(['account', 'token'])
            for account in login_user_list:
                body = {'mobile': account, 'code': '111111', "source": "ANDROID"}
                res = self.request_post('/store/api/account/login', body=body)
                if res['text']['code'] != 200:
                    print(f'【{account}】登录失败', res['text'])
                else:
                    token = res['rep_header']['AccessToken']
                    csv_file_writer.writerow([account, token])

    def shop_login(self, username, password):
        """
        商家登录
        :param username: 商家账号
        :param password: 商家密码
        :return:
        """
        body = {'username': username,
                'password': password}
        res = self.request_post('/store/seller/account/login', body=body)
        shop_token = res['rep_header']['AccessToken']
        with open(self.shop_token_file, 'w', newline='',
                  encoding='utf-8') as shopTokenFiles:
            shop_token_write = csv.writer(shopTokenFiles)
            shop_token_write.writerow([shop_token])

    def get_shop_token(self):
        """
        获取商家token
        :return: 商家token
        """
        # 读取存储管理后台token的csv文件,并返回token信息
        with open(self.shop_token_file, 'r', encoding='utf-8') as ShopTokenRead:
            csv_file_read = csv.reader(ShopTokenRead)
            for row in csv_file_read:
                shop_token = row[0]
        return shop_token

    def get_user_token(self, mobile=None):
        """
        获取用户token
        :param mobile: 查询所有token: 不传, 查询指定账号token: 传手机号
        :return: 没有传手机号: 返回token列表, 传手机号: 返回token
        """
        user_token_list = []
        # 读取存储token的csv文件,并写入字段user_token_dic中
        with open(self.user_token_file, 'r', encoding='utf-8') as UserTokenRead:
            csv_file_read = csv.reader(UserTokenRead)
            next(csv_file_read)
            for row in csv_file_read:
                account = row[0]
                token = row[1]
                user_token_list.append((account, token))
        # 如果没有传入mobile参数,返回user_token_list,否则返回账户对应的token
        if mobile is None:
            return user_token_list
        else:
            for i in user_token_list:
                if i[0] == mobile:
                    return i[1]

    def get_admin_token(self):
        """
        获取管理后台token
        :return:
        """
        # 读取存储管理后台token的csv文件,并返回token信息
        with open(self.admin_token_file, 'r', encoding='utf-8') as AdminTokenRead:
            csv_file_read = csv.reader(AdminTokenRead)
            for row in csv_file_read:
                admin_token = row[0]
        return admin_token
