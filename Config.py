

def get_host(env='dev'):
    if env == 'test':
        url = ''
    elif env == 'dev':
        url = 'http://192.168.1.15:8001'  # 吕文波本地环境
        # url = 'http://192.168.1.43:8001'  # 江平本地环境
    elif env == 'pro':
        url = 'https://apibuyer.lczgu.com'
    return url


