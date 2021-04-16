import pymysql
import Config

"""
数据库操作封装类, 支持单条，多条数据查询操作
"""


class Database:
    database = Config.get_db()

    def __init__(self):
        """
        初始化数据库连接
        """
        self.conn = pymysql.connect(
            host='rm-wz9v045a7509h21e7zo.mysql.rds.aliyuncs.com',
            # host='192.168.1.10',
            port=3306,
            user='wuweipeng',
            password='Wuweipeng997',
            database=self.database,
            charset='utf8')

        self.cursor = self.conn.cursor()

    def select_one(self, sql):
        """
        单条数据查询方法
        :param sql: 传入sql
        :return: 返回的值需要取下标
        """
        self.__init__()
        self.cursor.execute(sql)
        select_result = self.cursor.fetchone()
        self.close()
        return select_result

    def select_all(self, sql):
        """
        多条数据查询方法
        :param sql: 传入sql
        :return: 会返回多条查询结果,需要遍历处理
        """
        self.__init__()
        self.cursor.execute(sql)
        select_result = self.cursor.fetchall()
        self.close()
        return select_result

    def close(self):
        """
        关闭数据库连接方法,完成所有数据库增删改查操作后调用
        """
        self.cursor.close()
        self.conn.close()
