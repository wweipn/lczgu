
def get_host(env='prod'):
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
        # return 'http://192.168.1.8:8101'  # 测试环境后台

    elif env == 'test':
        return 'http://192.168.1.8:8101'  # 测试环境后台

    elif env == 'prod':
        return 'https://apistore.lczgu.com'


def get_db(env='dev'):
    """
    获取数据库配置项
    :param env:
    old_test_goods: 老系统测试库商品表
    old_test_member: 老系统测试库用户表
    old_release_goods: 老系统线上库商品表
    old_release_member: 老系统线上库用户表

    :return:
    """

    db_data_dic = {
        'dev': 'store',
        'test': 'store_test',
        'prod': 'store_prod',
        'old_test_goods': 'test_lczgu_shop_goods',
        'old_test_member': 'test_lczgu_shop_member',
        'old_release_goods': 'store_prod_lczgu_shop_goods_prod',
        'old_release_member': 'store_prod_lczgu_shop_member_prod'
    }

    result = db_data_dic[env]

    return result

