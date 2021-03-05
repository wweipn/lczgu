import requests
import Config

"""
接口请求类
"""


class ApiRequests:
    host = Config.get_host()

    def request_post(self, url, token=None, params=None, body=None, data=None, **kwargs):
        """
        POST接口请求方法
        :param url: 接口路径
        :param token: token
        :param params: url参数
        :param body: 请求体参数
        :param data: 表单提交
        :param kwargs: 自定义请求头
        :return:
        """
        headers = {**kwargs}
        if token is not None:
            headers['Authorization'] = f'Bearer {token}'
        else:
            pass
        headers['platform'] = 'ios'
        res = requests.post(f'{self.host}{url}', headers=headers, params=params, json=body, data=data)
        result = {
            'text': res.json(),
            'status_code': res.status_code,
            'code': res.json()['code'],
            'desc': res.json()['desc'],
            'data': res.json()['data'],
            'url': res.url,
            'req_header': res.request.headers,
            'rep_header': res.headers,
            'body': res.request.body
        }
        return result

    def request_put(self, url, token=None, params=None, body=None, data=None, **kwargs):
        """
        PUT接口请求方法
        :param url: 接口路径
        :param token: token
        :param params: url参数
        :param body: 请求体参数
        :param data: 表单提交
        :param kwargs: 自定义请求头
        :return:
        """
        headers = {**kwargs}
        if token is not None:
            headers['Authorization'] = f'Bearer {token}'
        else:
            pass
        headers['platform'] = 'ios'
        res = requests.put(f'{self.host}{url}', headers=headers, params=params, json=body, data=data)
        result = {
            'text': res.json(),
            'status_code': res.status_code,
            'code': res.json()['code'],
            'desc': res.json()['desc'],
            'data': res.json()['data'],
            'url': res.url,
            'req_header': res.request.headers,
            'rep_header': res.headers,
            'body': res.request.body
        }
        return result

    def request_get(self, url, token=None, params=None, body=None, data=None, **kwargs):
        """
        GET接口请求方法
        :param url: 接口路径
        :param token: token
        :param params: url参数
        :param body: 请求体参数
        :param data: 表单提交
        :param kwargs: 自定义请求头
        :return:
        """
        headers = {**kwargs}
        if token is not None:
            headers['Authorization'] = f'Bearer {token}'
        else:
            pass
        headers['platform'] = 'ios'
        res = requests.get(f'{self.host}{url}', headers=headers, params=params, json=body, data=data)
        result = {
            'text': res.json(),
            'code': res.json()['code'],
            'desc': res.json()['desc'],
            'data': res.json()['data'],
            'url': res.url,
            'status_code': res.status_code,
            'req_header': res.request.headers,
            'rep_header': res.headers,
            'body': res.request.body
        }
        return result
