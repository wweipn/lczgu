"""
测试用例执行文件
"""

import pytest
from common import Shell

if __name__ == '__main__':
    args = ['-s', 'D:\\PythonProject\\Lczgu\\test_case\\test_account.py', '--alluredir', './report/reportallure/']
    # args = ['-s', 'D:\\PythonProject\\Lczgu\\test_exercise.py', '--alluredir', './report/reportallure/']
    # args = ['-s', '-q']
    pytest.main(args)
    try:
        shell = Shell.Shell()
        cmd = 'allure generate %s -o %s --clean' % ('./report/reportallure/', './report//reporthtml/')
        # logger.info("开始执行报告生成")
        print("开始执行报告生成")
        shell.invoke(cmd)
        # logger.info("报告生成完毕")
        print("报告生成完毕")
    except Exception as e:
        print("报告生成失败，请重新执行", e)
        # logger.error("报告生成失败，请重新执行", e)
        # log.error('执行用例失败，请检查环境配置')
        raise
