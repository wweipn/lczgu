# -*- coding: utf-8 -*-
# @Time: 2021/1/5 20:40
# @Author: Waipang

import csv
import os


def testcase_file_read(file_name):
    """
    获取csv文件下的表头和数据的方法
    :param file_name: test_file文件夹下的文件名称(带后缀)
    :return:
    """
    # 定义文件路径
    cur_path = os.path.dirname(os.path.realpath(__file__))
    temp = os.path.dirname(cur_path)
    test_file_path = os.path.join(temp, 'test_file')
    test_file = os.path.join(test_file_path, file_name)
    # 定义空列表
    data_list = []
    # 读取存储数据的csv文件, 写入列表中
    with open(test_file, 'r', encoding='gbk') as FileRead:
        csv_file_read = csv.reader(FileRead)
        for row in csv_file_read:
            data_list.append(row)
        key = ', '.join(data_list[0])
        if len(data_list[1:]) == 1:
            value = data_list[1:][0]
        else:
            value = data_list[1:]
        return key, value
