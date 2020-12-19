import pymysql
import time


class Database:

    def __init__(self, db='trade'):
        self.conn = pymysql.connect(
            host='192.168.1.202',
            port=3306,
            user='root',
            password='neominddevdb',
            database=db,
            charset='utf8')
        self.cursor = self.conn.cursor()

    def select(self, sql):
        self.cursor.execute(sql)
        data = self.cursor.fetchone()
        return data

    def close(self):
        self.cursor.close()
        self.conn.close()
