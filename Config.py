

"""
这个配置会更改涉及到所有类调用的域名,暂时封装成函数的方式,后续如果有其他配置会再放进来
"""


def get_host(env='dev'):
    url = ''
    if env == 'dev':
        # url = 'http://192.168.1.15:8001'  # 吕文波本地环境
        url = 'http://192.168.1.43:8001'  # 江平本地环境
    elif env == 'test':
        url = 'test_host'  # 暂时还不知道测试环境的地址
    elif env == 'pro':
        url = 'https://apibuyer.lczgu.com'
    return url


