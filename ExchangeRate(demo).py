import pymysql
import json
import time

"""
根据传入的货币对名称和最后报价时间获取行情报价
"""


def rate(symbol, date_time):
    # 根据货币对名称查询指定时间最新的报价
    sql = f"""
    SELECT 
        * 
    FROM 
        {symbol}_tick_his 
    WHERE 
        `date_time` <= '{date_time}' ORDER BY `date_time` 
    DESC LIMIT 1 
    """
    # 连接数据库
    conn = pymysql.connect(
        host='192.168.1.202',
        port=3306,
        user='root',
        password='neominddevdb',
        database='mkdhandle',
        charset='utf8')
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()  # 执行完毕返回的结果集默认以元组显示
    # 执行SQL语句
    cursor.execute(sql)
    data = cursor.fetchall()
    for row in data:
        ask = float(json.loads(row[4])[-1][0])
        bid = float(json.loads(row[3])[0][0])
        return round(ask, 5), round(bid, 5)
    # 关闭光标对象
    cursor.close()
    # 关闭数据库连接
    conn.close()


"""
根据订单列表的数据计算平仓后的盈亏
"""


def close_detail(order_no):
    sql = f"""
            SELECT
                symbol,
                side,
                open_Price,
                close_price,
                close_qty,
                create_dt
            FROM
                trade_order 
            WHERE
                order_no = '{order_no}'
            AND
                comment = 'customer closed manually'
                """
    # 连接database
    conn = pymysql.connect(
        host='192.168.1.202',
        port=3306,
        user='root',
        password='neominddevdb',
        database='trade',
        charset='utf8')
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()  # 执行完毕返回的结果集默认以元组显示
    # 执行SQL语句
    cursor.execute(sql)
    data = cursor.fetchall()
    for row in data:
        symbol = row[0]  # 货币对名称
        side = row[1]   # 交易方向,1:买,2:卖
        open_Price = float(row[2])  # 开仓价
        close_price = float(row[3])  # 平仓价
        close_qty = float(row[4])  # 平仓手数
        create_dt = row[5]  # 创建时间

        # if side == '1':
        #     P_L = (close_price - open_Price) * 100000 * close_qty
        # elif side == '2':
        #     P_L = (close_price - open_Price) * 100000 * close_qty * -1
        # # 货币对中没有包含交易货币时,获取对应报价的货币对进行汇率转换
        # if 'USD' not in symbol:
        #     try:
        #         select_symbol = 'USD'+symbol[3:]
        #         ss_ask, ss_bid = rate(select_symbol, create_dt)
        #         # 买方向的单, 最终盈亏计算公式: (平仓价 - 开仓价) * 100000 * 平仓手数 / {交易货币}{报价货币}的bid价格
        #         if side == '1':
        #             return ((close_price - open_Price) * 100000 * close_qty) / ss_bid
        #         # 卖方向的单, 最终盈亏计算公式: (开仓价 - 平仓价) * 100000 * 平仓手数 / {交易货币}{报价货币}的ask价格
        #         elif side == '2':
        #             return ((open_Price - close_price) * 100000 * close_qty) / ss_ask
        #     except:
        #         select_symbol = 'USD'+symbol[3:]
        #         ss_ask, ss_bid = rate(select_symbol, create_dt)
        #         # 买方向的单, 最终盈亏计算公式: (平仓价 - 开仓价) * 100000 * 平仓手数 / {交易货币}{报价货币}的bid价格
        #         if side == '1':
        #             return ((close_price - open_Price) * 100000 * close_qty) / ss_bid
        #         # 卖方向的单, 最终盈亏计算公式: (开仓价 - 平仓价) * 100000 * 平仓手数 / {交易货币}{报价货币}的ask价格
        #         elif side == '2':
        #             return ((open_Price - close_price) * 100000 * close_qty) / ss_ask
        #
        # # 报价货币等于交易货币(现在默认将USD作为交易货币)
        # elif symbol[3:] == 'USD':
        #     # 买方向的单, 最终盈亏计算公式: (平仓价 - 开仓价) * 100000 * 平仓手数
        #     if side == '1':
        #         return (close_price - open_Price) * 100000 * close_qty
        #     # 卖方向的单, 最终盈亏计算公式: (开仓价 - 平仓价) * 100000 * 平仓手数
        #     elif side == '2':
        #         return (open_Price - close_price) * 100000 * close_qty

        # print(f'{symbol}, {side}, {close_price}, {close_qty}, {create_dt}')
    # 关闭光标对象
    cursor.close()
    # 关闭数据库连接
    conn.close()


if __name__ == '__main__':
    print(rate('AUDNZD', '2020-08-27 10:50:17'))



