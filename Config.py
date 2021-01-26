import os


def get_host(env='dev'):
    """
    获取域名配置
    :param env:
    :return:
    """
    url = ''
    if env == 'dev':
        # url = 'http://192.168.1.15:8001'  # 吕文波本地环境
        # url = 'http://192.168.1.43:8001'  # 江平本地环境
        # url = 'http://192.168.1.39:8001'  # 何星本地环境
        url = 'http://192.168.1.8:8001'  # 开发环境后台

    elif env == 'test':
        url = 'http://192.168.1.8:8101'
    elif env == 'pro':
        url = ''  # 线上环境,展示用不上
    return url


def get_db(env='dev'):
    """
    获取数据库配置项
    :param env:
    :return:
    """
    database = ''
    if env == 'dev':
        database = 'store'
    elif env == 'test':
        database = 'store_test'
    elif env == 'old_test':
        database = 'test_lczgu_shop_goods'
    elif env == 'old_test_member':
        database = 'test_lczgu_shop_member'
    return database


def test_file_path():
    path = os.path.abspath('.')
    return path
