
"""
这个配置会更改涉及到所有类调用的域名,暂时封装成函数的方式,后续如果有其他配置会再放进来
"""


def get_host(env='dev'):
    url = ''
    if env == 'dev':
        # url = 'http://192.168.1.15:8001'  # 吕文波本地环境
        # url = 'http://192.168.1.43:8001'  # 江平本地环境
        url = 'http://192.168.1.8:8001'  # 开发环境后台

    elif env == 'test':
        url = 'http://192.168.1.8:8101'
    elif env == 'pro':
        url = ''  # 线上环境,展示用不上
    return url


"""
用于数据库类获取当前环境的配置项
"""


def get_db(env='dev'):
    database = ''
    if env == 'dev':
        database = 'store'
    elif env == 'test':
        database = 'store_test'
    return database
