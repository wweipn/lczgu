# -*- coding: utf-8 -*-
# @Time: 2021/1/27 9:40
# @Author: Waipang

import os


def get_file_path(file_name, parent_path='test_case'):
    """
    获取文件完整路径
    :param file_name: 文件名(带后缀)
    :param parent_path: 文件的前置路径
    :return:
    """
    # 获取当前所在的路径, 比如: D:\PythonProject\Lczgu\common
    cur_path = os.path.dirname(os.path.realpath(__file__))

    # 获取上一级路径(也就是该项目的根目录), 比如: D:\PythonProject\Lczgu
    temp = os.path.dirname(cur_path)

    # 传入文件夹名称,与根目录进行拼接, 比如: D:\PythonProject\Lczgu\test_case
    test_file_path = os.path.join(temp, parent_path)

    # 与文件名进行拼接后返回, 比如: D:\PythonProject\Lczgu\test_case\test_account.py
    test_file = os.path.join(test_file_path, file_name)
    return test_file
