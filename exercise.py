# -*- coding: utf-8 -*-
# @Time: 2021/1/4 12:33
# @Author: Waipang

import common
import pytest

token_list = common.account.get_user_token()
select_account = common.db.select_all(sql="""
    SELECT id, mobile FROM `store`.`user_account` LIMIT 0,1000
    """)


# @pytest.mark.parametrize('mobile, token', token_list)
# def test_select_address(mobile, token):
#     get_address = common.req.request_get(url='/store/api/user/addr', token=token)
#     print(get_address['text'])

@pytest.mark.parametrize('account_id, mobile', select_account)
def test_select_address(account_id, mobile):
    common.account.user_login(source=0, user_list=[mobile])


if __name__ == '__main__':
    pytest.main(['-s', 'exercise.py'])
    # select_account = common.db.select_all(sql="""
    # SELECT id, mobile FROM `store`.`user_account` LIMIT 0,1000
    # """)
    # print(select_account)