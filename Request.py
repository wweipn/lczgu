import requests
import json
import time
import Config


"""
接口请求类
"""


class ApiRequests:

    def __init__(self):
        self.headers = {}
        self.host = Config.get_host()

    def request_post(self, url, token=None, params=None, body=None, data=None):
        if token is not None:
            self.headers['Authorization'] = f'Bearer {token}'
        else:
            pass
        res = requests.post(f'{self.host}{url}', headers=self.headers, params=params, json=body, data=data)
        time.sleep(0.2)
        return {'text': json.loads(res.text),
                'code': res.status_code,
                'url': res.url,
                'header': res.request.headers}

    def request_get(self, url, token=None, params=None, body=None, data=data):
        if token is not None:
            self.headers['Authorization'] = f'Bearer {token}'
        else:
            pass
        res = requests.post(f'{self.host}{url}', headers=self.headers, params=params, json=body)
        time.sleep(0.2)
        return {'text': json.loads(res.text),
                'code': res.status_code,
                'url': res.url,
                'header': res.request.headers}
