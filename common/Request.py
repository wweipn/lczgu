import requests
import json
import Config

"""
接口请求类
"""


class ApiRequests:
    host = Config.get_host()

    """
    基于requests框架封装,提供给post请求方式的接口所使用的方法
    """

    def request_post(self, url, token=None, params=None, body=None, data=None, **kwargs):
        headers = {**kwargs}
        if token is not None:
            headers['Authorization'] = f'Bearer {token}'
        else:
            pass
        res = requests.post(f'{self.host}{url}', headers=headers, params=params, json=body, data=data)
        result = {
            'text': json.loads(res.text),
            'status_code': res.status_code,
            'code': json.loads(res.text)['code'],
            'desc': json.loads(res.text)['desc'],
            'data': json.loads(res.text)['data'],
            'url': res.url,
            'req_header': res.request.headers,
            'rep_header': res.headers,
            'body': res.request.body

        }
        return result

    """
        基于requests框架封装,提供给put请求方式的接口所使用的方法
    """

    def request_put(self, url, token=None, params=None, body=None, data=None, **kwargs):
        headers = {**kwargs}
        if token is not None:
            headers['Authorization'] = f'Bearer {token}'
        else:
            pass
        res = requests.put(f'{self.host}{url}', headers=headers, params=params, json=body, data=data)
        result = {
            'text': json.loads(res.text),
            'status_code': res.status_code,
            'code': json.loads(res.text)['code'],
            'desc': json.loads(res.text)['desc'],
            'data': json.loads(res.text)['data'],
            'url': res.url,
            'req_header': res.request.headers,
            'rep_header': res.headers,
            'body': res.request.body

        }
        return result

    """
       基于requests框架封装,提供给get请求方式的接口所使用的方法
    """

    def request_get(self, url, token=None, params=None, body=None, data=None, **kwargs):
        headers = {**kwargs}
        if token is not None:
            headers['Authorization'] = f'Bearer {token}'
        else:
            pass
        res = requests.get(f'{self.host}{url}', headers=headers, params=params, json=body, data=data)
        result = {
            'text': json.loads(res.text),
            'status_code': res.status_code,
            'url': res.url,
            'req_header': res.request.headers,
            'rep_header': res.headers
        }
        return result
