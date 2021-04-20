from .Database import Database
from .Account import Account
from .Request import ApiRequests
from .FileRead import testcase_file_read
from .FileOper import get_file_path

account = Account()
req = ApiRequests()
db = Database()


def admin_token():
    account.admin_login()
    token = account.get_admin_token()
    return token


def user_token(mobile):
    account.user_login([str(mobile)])
    token = account.get_user_token(mobile=str(mobile))
    return token


def shop_token(shop_name):
    account.shop_login(username=shop_name, password=None)
    token = account.get_shop_token()
    return token


def api_print(name, url, result, data=None):
    """
    打印接口调用信息
    :param name: 接口名
    :param url: 接口路径
    :param data: 请求参数
    :param result: 响应信息
    :return:
    """

    print(f"""
    【{name}】({url})
    请求参数
    {data}

    返回结果
    {result['text']}

    """.replace("'", '"'))
