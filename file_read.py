import requests
import json
import csv


"""
登录函数(带文件写入)
"""


def login(pf, source=1):  # pf(平台):admin, trade; source(数据来源): 0: 手动输入, 1: 文件获取;
    user_dic = {}
    # 判断所属平台,走不同的请求配置
    if pf == 'admin':
        res = requests.post('http://192.168.1.203/crm/login/login', headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/84.0.4147.105 Safari/537.36"}, json={"accountNo": "admin", "password": "123456"})
        response = json.loads(res.text)
        AdminToken = response['data']
        with open('D:/admin_token.csv', 'w', newline='', encoding='utf-8') as adminTokenFiles:
            adminTokenWrite = csv.writer(adminTokenFiles)
            adminTokenWrite.writerow([AdminToken])
        return AdminToken
    elif pf == 'trade':
        # 读取csv文件中的用户账号和密码,并写入user_dic字典中
        if source == 1:
            with open('D:/user_list.csv', 'r', encoding='utf-8') as userListFile:
                csv_file_read = csv.reader(userListFile)
                next(csv_file_read)
                for row in csv_file_read:
                    accountNo = row[0]
                    password = row[1]
                    user_dic[accountNo] = password
        elif source == 0:
            accountNo = input('账号:')
            password = input('密码:')
            user_dic[accountNo] = password
    # 从user_dic中取出登录账号,逐一登录完毕后把token储存到csv文件中
    with open('D:/TradeUser_token.csv', 'w', newline='', encoding='utf-8') as TradeUser_token:
        csv_file_writer = csv.writer(TradeUser_token)
        csv_file_writer.writerow(['AccountId', 'Token'])
        for accountNo, password in user_dic.items():
            res = requests.post('http://192.168.1.202/trade/login/login', headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                              "like Gecko) "
                              "Chrome/84.0.4147.105 Safari/537.36"},
                                json={"accountNo": accountNo, "password": password})
            response = json.loads(res.text)
            tradeToken = response['data']
            csv_file_writer.writerow([accountNo, tradeToken])
    # 读取存储token的csv文件,并通过字典的方式返回
    with open('D:/TradeUser_token.csv', 'r', encoding='utf-8') as TradeUser_token_read:
        csv_file_read = csv.reader(TradeUser_token_read)
        next(csv_file_read)
        tradeToken_dic = {}
        for row in csv_file_read:
            accountNo = row[0]
            tradeToken = row[1]
            tradeToken_dic[accountNo] = tradeToken
        return tradeToken_dic