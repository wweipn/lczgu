admin_uid = '2d890740-1f28-11eb-ba65-ddb71902b541'
user_uid = '7dd600d0-2343-11eb-aab5-77d5070dc5d4'


def env(env_url='test'):
    if env_url == 'test':
        base_url = 'http://192.168.1.8:7000'
        user_url = 'http://192.168.1.8:7002'
        shop_url = 'http://192.168.1.8:7003'
        admin_url = 'http://192.168.1.8:7004'
    elif env_url == 'pro':
        base_url = 'https://apibase.lczgu.com'
        user_url = 'https://apibuyer.lczgu.com'
        shop_url = 'http://192.168.1.8:7003'
        admin_url = 'http://192.168.1.8:7004'
    return base_url, user_url, shop_url, admin_url
