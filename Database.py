import pymysql

"""
数据库操作封装类, 支持单条，多条数据查询操作
"""


class Database:

    """
    初始化数据库连接
    """
    def __init__(self):
        self.conn = pymysql.connect(
            host='192.168.1.10',
            port=3306,
            user='wuweipeng',
            password='Wuweipeng997',
            database='store',
            charset='utf8')
        self.cursor = self.conn.cursor()

    """
    单条查询方法,传入sql参数后会返回一条查询结果,可直接下标取值
    """
    def select_one(self, sql):
        self.cursor.execute(sql)
        select_result = self.cursor.fetchone()
        return select_result

    """
    多条查询方法,传入sql参数后会返回多条查询结果,需要遍历处理
    """
    def select_all(self, sql):
        self.cursor.execute(sql)
        select_result = self.cursor.fetchall()
        return select_result

    """
    关闭数据库连接方法,完成所有数据库增删改查操作后调用
    """
    def close(self):
        self.cursor.close()
        self.conn.close()


