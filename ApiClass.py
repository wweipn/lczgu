import requests
import json
import time
import Config


"""
接口请求类
"""


# todo
class ApiRequests:

    def __init__(self):
        self.headers = {}
        self.host = Config.get_host()

    def request_post(self, url, token=None, params=None, body=None):
        self.headers['Authorization'] = f'Bearer {token}' if not None else 'Bearer '
        if params is not None:
            res = requests.post(f'{self.host}{url}', headers=self.headers, params=params)
        elif body is not None:
            res = requests.post(f'{self.host}{url}', headers=self.headers, json=body)
        else:
            res = requests.post(f'{self.host}{url}', headers=self.headers)
        time.sleep(0.5)
        return {'text': json.loads(res.text),
                'code': res.status_code,
                'url': res.url,
                'header': res.request.headers}

    def request_get(self, url, token=None, params=None, body=None):
        self.headers['Authorization'] = f'Bearer {token}' if not None else 'Bearer '
        if params is not None:
            res = requests.get(f'{self.host}{url}', headers=self.headers, params=params)
        elif body is not None:
            res = requests.get(f'{self.host}{url}', headers=self.headers, json=body)
        else:
            res = requests.get(f'{self.host}{url}', headers=self.headers)
        time.sleep(0.5)
        return {'text': json.loads(res.text),
                'code': res.status_code,
                'url': res.url,
                'header': res.request.headers}


