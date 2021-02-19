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
