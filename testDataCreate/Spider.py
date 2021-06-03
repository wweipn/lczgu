import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import re
import csv
import os


def bs4_request_base(url):
    """
    请求通用方法
    :param url:
    :return:
    """
    headers = {
        'Host': 'book.douban.com',
        'Connection': 'keep-alive',
        'sec-ch-ua': '\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"90\", \"Google Chrome\";v=\"90\"',
        'sec-ch-ua-mobile': '?0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://book.douban.com/subject/35390390/?icn=index-latestbook-subject',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cookie': 'll=\"118282\"; bid=bA6VGhEGuWc; __utma=30149280.485390998.1622726376.1622726376.1622726376.1;'
                  ' __utmz=30149280.1622726376.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmc=30149280;'
                  ' __utmt=1; ap_v=0,6.0; _ga=GA1.2.485390998.1622726376; _gid=GA1.2.1311033439.1622726403;'
                  ' gr_user_id=827bddc8-ed30-4b00-ba6f-ce5c4cd3f451;'
                  ' gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03=b90005a7-81c7-4021-831c-f52383db27c5;'
                  ' gr_cs1_b90005a7-81c7-4021-831c-f52383db27c5=user_id%3A0;'
                  ' _pk_ref.100001.3ac3=%5B%22%22%2C%22%22%2C1622726434%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_ses.100001.3ac3=*;'
                  ' __utmt_douban=1; __utma=81379588.485390998.1622726376.1622726434.1622726434.1;'
                  ' __utmc=81379588; __utmz=81379588.1622726434.1.1.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/;'
                  ' gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03_b90005a7-81c7-4021-831c-f52383db27c5=true;'
                  ' _vwo_uuid_v2=D9134B11AEAEA182B2584339C53269E75|ae1ead1c274fe6a70c7fc8f8cc9d1837;'
                  ' __yadk_uid=DT94dCdr3gxrgauAWk5kq7jZC2Jylxkz; viewed=\"35390390\";'
                  ' __gads=ID=3a1540a314bf081e-22a8155c2ec900fa:T=1622726439:RT=1622726439:S=ALNI_MYOV3ZsD1utAiHTsysDYFXl8QoKKw;'
                  ' __utmb=30149280.5.10.1622726376; __utmb=81379588.4.10.1622726434; _pk_id.100001.3ac3=d57504087e3d39c3.1622726434.1.1622726465.1622726434.'
    }

    first_res = requests.get(url=url, headers=headers)
    base_soup = BeautifulSoup(first_res.text, 'html.parser')
    return base_soup


def get_comment_num(book_id):
    """
    获取书籍评论数
    :param book_id: 书籍ID
    :return:
    """

    # 发起网络请求
    res = bs4_request_base(url=f'https://book.douban.com/subject/{book_id}/comments/?start=0&limit=20&status=P&sort=time')

    # 获取总评论数, 根据总评论数计算页码
    comment_num = int(re.sub('\D', '', res.find('li', class_='is-active').find('span').text))

    # 根据查询到的评论数计算页码
    page_num = int(comment_num / 20)
    return page_num


def get_comment_user_info(book_id):
    """
    爬取评论书籍用户的信息
    :param book_id:
    :return:
    """

    # 获取当前时间
    now = datetime.now().strftime('%Y-%m-%d')

    # 定义文件路径
    cur_path = os.path.dirname(os.path.realpath(__file__))
    temp = os.path.dirname(cur_path)
    test_file_path = os.path.join(temp, 'test_file')

    # 定义存储token的文件
    user_data = os.path.join(test_file_path, f'user_data({now}).csv')

    # 根据查询到的评论数计算页码
    page_num = get_comment_num(book_id) if get_comment_num(book_id) < 10 else 10
    page = 0

    with open(user_data, 'w', newline='', encoding='utf-8') as user_data_file:
        csv_file_writer = csv.writer(user_data_file)
        csv_file_writer.writerow(['head_url', 'user_name'])

        while page <= page_num:

            # 发起网络请求
            res = bs4_request_base(url=f'https://book.douban.com/subject/{book_id}/comments/?start={page * 20}&limit=20&status=P&sort=new_score')
            print(f'https://book.douban.com/subject/{book_id}/comments/?start={page * 20}&limit=20&status=P&sort=new_score')

            # 获取所有评论/遍历数据
            comment_list = res.find('div', class_='comment-list new_score').find('ul').find_all('li', class_='comment-item')

            for data in comment_list:
                # 获取用户头像和昵称
                try:
                    head_url = data.find('div', class_='avatar').find('a').find('img')['src'].replace('/u', '/ul')
                    user_name = data.find('div', class_='avatar').find('a')['title']
                    print(head_url, user_name)
                    csv_file_writer.writerow([head_url, user_name])
                except AttributeError:
                    print(data.text)

            print(f'当前爬取页数（{page + 1}）')
            page += 1
            time.sleep(2)


if __name__ == '__main__':
    get_comment_user_info(book_id=35335514)


