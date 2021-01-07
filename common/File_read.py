# -*- coding: utf-8 -*-
# @Time: 2021/1/5 20:40
# @Author: Waipang

import csv

"""
获取csv文件下的表头和数据的方法
参数:file_path, 
"""


def file_read(file_path):
    data_list = []
    # 读取存储数据的csv文件
    with open(file_path, 'r', encoding='gbk') as FileRead:
        csv_file_read = csv.reader(FileRead)
        for row in csv_file_read:
            data_list.append(row)
        key = ', '.join(data_list[0])
        if len(data_list[1:]) == 1:
            value = data_list[1:][0]
        else:
            value = data_list[1:]
        return key, value
