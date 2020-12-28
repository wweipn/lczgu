import pymysql


def symbol_spread(symbol):
    sql = {"""
        SELECT
            spread_ask,
            spread_bid
        FROM
            symbol
        WHERE
        symbol = 'AUDJPY'
        """}
    conn = pymysql.connect(
        host='192.168.1.202',
        port=3306,
        user='root',
        password='neominddevdb',
        database='trade',
        charset='utf8')
    cursor = conn.cursor()
    # 执行SQL语句
    cursor.execute(sql)
    data = cursor.fetchall()
    for row in data:
        spread_ask = row[0]
        spread_bid = row[1]
    # 关闭光标对象
    cursor.close()
    # 关闭数据库连接
    conn.close()
