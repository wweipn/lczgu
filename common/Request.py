import requests
import json
import time
import Config


"""
接口请求类
"""


class ApiRequests:
    host = Config.get_host()

    def request_post(self, url, token=None, params=None, body=None, data=None, **kwargs):
        headers = {**kwargs}
        if token is not None:
            headers['Authorization'] = f'Bearer {token}'
        else:
            pass
        res = requests.post(f'{self.host}{url}', headers=headers, params=params, json=body, data=data)
        return {'text': json.loads(res.text),
                'code': res.status_code,
                'url': res.url,
                'header': res.request.headers}

    def request_get(self, url, token=None, params=None, body=None, data=None, **kwargs):
        headers = {**kwargs}
        if token is not None:
            headers['Authorization'] = f'Bearer {token}'
        else:
            pass
        res = requests.get(f'{self.host}{url}', headers=headers, params=params, json=body, data=data)
        state_code = res.status_code
        url = res.url
        text = json.loads(res.text)
        if state_code == 200:
            return {'text': json.loads(res.text),
                    'code': res.status_code,
                    'url': res.url,
                    'header': res.request.headers}
        else:
            print(f'''
                    调用异常
                    state_code: {state_code}
                    url: {url}
                    text: {text}
            ''')
