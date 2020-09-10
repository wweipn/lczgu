import api_class as a
import time
import random

"""
创建账户组以及账户组下的账户
"""


def create_GroupUser():
    group_count = int(input('账户组数量:'))
    user_count = int(input('账户数量:'))

    """
    创建账户组以及账户组下的账户并充值
    """
    for i in range(group_count):
        num = random.randint(10000, 99999)
        addUserGroup = a.ApiRequests(pf='admin').requests(url='/crm/group/baseSet', content={
            "groupName": num,
            "company": f"com_{num}",
            "accountCurreny": "USD",
            "leverage": 400,
            "lockAble": 0,
            "groupType": 1,
            "lockAbleMarginCalc": 0,
            "maxAccountOrderNum": 0,
            "maxAccountPositionNum": 0,
            "maxAccountSubNum": 0})
        if addUserGroup['code'] == "0000":
            groupId = addUserGroup['data']['id']
            print(f'账户组{num}创建成功')
        elif addUserGroup['code'] != "2010":
            continue
        else:
            print(f'账户组{num}创建异常,详情:\n', addUserGroup)
            break
        getTradeVarity = a.ApiRequests(pf='admin').requests(method='get',
                                                            url=f'/crm/group/getTradeVarity?groupId={groupId}')
        Id = getTradeVarity['data'][0]['id']
        tradeVarityId = getTradeVarity['data'][0]['tradeVarityId']
        a.ApiRequests(pf='admin').requests(url='/crm/group/tradevarietySet', content={
            "groupId": groupId,
            "tradeVarityList": [
                {
                    "id": Id,
                    "tradeVarityId": tradeVarityId,
                    "tradeVarityName": "Forex",
                    "recQuotes": 0,
                    "tradeFlag": 0,
                    "groupId": groupId
                }
            ]
        })
        time.sleep(0.5)

        """
        创建账户
        """
        for j in range(user_count):
            phoneNumHead = random.choice(['130', '131', '132', '133', '134', '135', '136', '137', '138'])
            phoneMain = str(random.randint(10000000, 99999999))
            qq = str(random.randint(10000, 9999999999))
            addUser = a.ApiRequests(pf='admin').requests(url='/crm/account/openAccount', content={
                "groupId": groupId,
                "userName": qq,
                "email": f"{qq}@qq.com",
                "phone": phoneNumHead + phoneMain,
                "country": 45,
                "accountStatus": 0,
                "tradeLimit": 0,
                "password": "a123456"})
            if addUser['code'] == '0000':
                accountNo = addUser['data']['accountNo']
                print(f'账户{qq}创建成功')
            elif addUser['code'] == '3010':
                continue
            else:
                print(f'账户{qq}创建异常,详情:\n{addUser}')
                break
            time.sleep(0.5)

            """
            账户充值
            """
            userCharge = a.ApiRequests(pf='admin').requests(url='/crm/balance/depWithOpr', content={
                "accountNo": f"{accountNo}", "dealType": 0, "operType": 0, "amount": "10000"})
            if userCharge['code'] == '0000':
                print(f'账户{qq}充值成功')
            else:
                print(f'账户{qq}充值失败,详情:\n{userCharge}')
                break
            time.sleep(0.5)


if __name__ == '__main__':
    # 创建账户组和账户
    # create_GroupUser()
    # 开仓
    # a.ApiRequests().openPosition(count=10)
    # time.sleep(20)
    # # 平仓
    # a.ApiRequests().closePosition()
    riskAccountList = a.ApiRequests(pf='manager').requests(url='/manager/account/riskAccountList', content={
        "marginCallLevel": ""
    })
    marginLevel = 0
    for i in riskAccountList['data']:
        print(i['marginLevel'])

