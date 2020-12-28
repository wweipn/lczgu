from Account import Account
from Request import ApiRequests

userAccount = Account()
userRequest = ApiRequests()

# userAccount.user_login(source=0, user_list=['18123929299'])
# token = userAccount.get_user_token(mobile='18123929299')
# getActivityBalanceList = userRequest.request_post(url='/store/api/money/getActivityBalanceList', token=token, body={
#     "currentPage": 1,
#     "pageSize": 10
# })

login = userRequest.request_post(url='/store/api/account/login', params={'code': '111111',
                                                                         'source': 'IOS',
                                                                         'mobile': '17199990008'})
# print(getActivityBalanceList['text'])
print(login['text'])
