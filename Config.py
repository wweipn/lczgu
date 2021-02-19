
def get_host(env='dev'):
    """
    获取域名配置
    :param env:
    :return:
    """
    if env == 'dev':
        # return 'http://192.168.1.15:8001'  # 吕文波本地环境
        # return 'http://192.168.1.43:8001'  # 江平本地环境
        # return 'http://192.168.1.39:8001'  # 何星本地环境
        # return 'http://192.168.1.117:8001'  # 汤升本地环境
        return 'http://192.168.1.8:8001'  # 开发环境后台

    elif env == 'test':
        return 'http://192.168.1.8:8101'  # 测试环境后台

    elif env == 'pro':
        return ''  # 线上环境,展示用不上


def get_db(env='dev'):
    """
    获取数据库配置项
    :param env:
    :return:
    """
    if env == 'dev':
        return 'store'

    elif env == 'test':
        return 'store_test'

    elif env == 'old_test':
        return 'test_lczgu_shop_goods'

    elif env == 'old_test_member':
        return 'test_lczgu_shop_member'

