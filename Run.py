"""
测试用例执行文件
"""

import pytest
from common import get_file_path
from common import Shell

if __name__ == '__main__':
    test_file = get_file_path('test_account.py')
    args = ['-s', test_file, '--alluredir', './report/reportallure/']
    # args = ['-s', test_files, '--alluredir', './report/reportallure/']
    # args = ['-s', '-q']
    pytest.main(args)
    try:
        shell = Shell.Shell()
        folder1 = './report/reportallure/'
        folder2 = './report//reporthtml/'
        cmd = f'allure generate {folder1} -o {folder2} --clean'
        print("开始执行报告生成")
        shell.invoke(cmd)
        print("报告生成完毕")
    except Exception as e:
        print("报告生成失败，请重新执行", e)
        raise


