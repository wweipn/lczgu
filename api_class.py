import requests
import json
import csv
import time
import random
import datetime
import mysql_setting as ms
import exchange_rate as er

"""
登录函数
"""


def login(pf, source=1):  # pf(平台):admin, trade; source(数据来源): 0: 手动输入, 1: 文件获取;
    user_dic = {}
    tradeToken_dic = {}
    # 判断所属平台,走不同的请求配置
    if pf == 'admin':
        res = requests.post('http://192.168.1.203/crm/login/login', headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/84.0.4147.105 Safari/537.36"}, json={"accountNo": "admin", "password": "123456"})
        response = json.loads(res.text)
        AdminToken = response['data']
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
        # 手动输入账号
        elif source == 0:
            while True:
                accountNo = input('账号:(输入0结束输入)')
                password = 'a123456'
                if accountNo == 0:
                    break
                user_dic[accountNo] = password
        for accountNo, password in user_dic.items():
            res = requests.post('http://192.168.1.202/trade/login/login', headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                              "like Gecko) "
                              "Chrome/84.0.4147.105 Safari/537.36"},
                                json={"accountNo": accountNo, "password": password})
            response = json.loads(res.text)
            tradeToken = response['data']
            tradeToken_dic[accountNo] = tradeToken
        return tradeToken_dic


def openPositionData():
    orderType = random.choice(['1', '2'])  # 市价单:orderType=1 限价单:orderType=2
    side = random.choice(['1', '2'])  # 买:1, 卖:2
    symbol = random.choice(
        ['AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURJPY',
         'EURUSD', 'GBPAUD', 'GBPCAD', 'GBPCHF', 'GBPJPY', 'GBPNZD', 'GBPUSD', 'NZDJPY', 'NZDUSD',
         'USDJPY', 'USDCAD', 'EURGBP'])
    orderQty = random.randint(1, 200) / 100
    # 通过当前时间、交易货币对查询当前市价
    presentTime = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    ask, bid = er.rate(symbol, presentTime)
    symbolSel = ms.Database().select(sql=f"""
        SELECT
            min_order_offset * min_quote_unit AS 'limit',
            spread_ask AS 'spread_ask',
            spread_bid AS 'spread_bid'
        FROM
            symbol
        WHERE
            symbol = '{symbol}'""")
    priceLimit = symbolSel[0]
    spreadAsk = symbolSel[1]
    spreadBid = symbolSel[2]

    # 根据订单类型/交易方向提供不同的价格 订单类型 1 = 市价  2 = 限价
    if orderType == '1':
        # 市价单,加点差
        if side == '1':
            orderPrice = ask + spreadAsk
        else:
            orderPrice = bid + spreadBid
    elif orderType == '2':
        # 限价单,除了点差以外另外加上了下单偏移量
        if side == '1':
            orderPrice = ask + spreadAsk - priceLimit * 1.5
        else:
            orderPrice = bid + spreadBid + priceLimit * 1.5
    return orderType, side, symbol, orderQty, orderPrice


class ApiRequests:
    def __init__(self, pf='trade', source=1):
        self.pf = pf
        self.source = source
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/84.0.4147.105 Safari/537.36"}
        if pf == 'admin':
            self.host = 'http://192.168.1.203'
            self.AdminToken = login(pf)
        elif pf == 'trade':
            self.host = 'http://192.168.1.202'
        elif pf == 'manager':
            self.host = 'http://192.168.1.202:5005'
            self.AdminToken = login(pf='admin')

    def requests(self, url, content=None, method='post'):
        # 遍历user_dic里面的所有数据,并参数化请求头中的token实现多用户调用
        if self.pf == "trade":
            tradeToken_dic = login(self.pf, self.source)
            for user in tradeToken_dic.items():
                self.headers['token'] = user[1]
                if method == 'post':
                    res = requests.post(f'{self.host}{url}', headers=self.headers, json=content)
                elif method == 'get':
                    res = requests.get(f'{self.host}{url}', headers=self.headers, json=content)
                time.sleep(0.5)
        elif self.pf == 'admin' or self.pf == 'manager':
            self.headers['token'] = self.AdminToken
            if method == 'post':
                res = requests.post(f'{self.host}{url}', headers=self.headers, json=content)
            elif method == 'get':
                res = requests.get(f'{self.host}{url}', headers=self.headers, json=content)
            response = json.loads(res.text)
            return response

    # 批量开仓用, D盘user_list文件添加用户, count为每个用户的调用次数
    def openPosition(self, count=1):
        for i in range(count):
            # 遍历user_dic里面的所有数据,并参数化请求头中的token实现多用户调用
            tradeToken_dic = login(self.pf, self.source)
            for user in tradeToken_dic.items():
                self.headers['token'] = user[1]
                orderType, side, symbol, orderQty, orderPrice = openPositionData()
                requests.post(f'{self.host}/trade/trade/placeOrder', headers=self.headers, json={
                    "orderType": orderType,
                    "symbol": symbol,
                    "side": orderType,
                    "orderQty": orderQty,
                    "orderPrice": orderPrice,
                    "orderSource": 1,
                    "takeProfit": "0.000",
                    "stopLoss": "0.000"
                })

    # 平仓
    def closePosition(self):
        tradeToken_dic = login(self.pf, self.source)
        for user in tradeToken_dic.items():
            self.headers['token'] = user[1]
            requests.post(f'{self.host}/trade/closed/closeOutAll', headers=self.headers)


if __name__ == '__main__':
    pass
