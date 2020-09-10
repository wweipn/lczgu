from exchange_rate import rate
import pymysql
import json

"""
根据订单ID获取货币对的名称、交易方向、开仓价、持仓手数、利息结算时间
"""


def sel_order(order_id):
    sql = f"""
    SELECT
        symbol,
        side,
        open_Price,
        open_qty,
        swap_settlment_time
    FROM
        trade_order 
    WHERE
        order_no = '{order_id}'
    """
    # 连接数据库
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
        symbol = row[0],
        side = row[1],
        open_Price = float(row[2]),
        open_qty = float(row[3]),
        swap_settlment_time = row[4]
        return symbol, side, open_Price, open_qty, swap_settlment_time
    # 关闭光标对象
    cursor.close()
    # 关闭数据库连接
    conn.close()


def swap():  # 持仓数量 * 合约单位 * (买或卖年利率 / 100 / 360)
    order_id = input('输入订单编号:')
    symbol, side, price, lots, swap_settlment_time = sel_order(order_id)
    # 根据交易方向决定利率
    if side[0] == 1:
        swap_value = -3.5
    else:
        swap_value = 2.5
    # print(symbol[0], type(symbol[0]), symbol[0][3:].lower())
    # 持仓货币对不包含USD情况,计算汇率
    if 'USD' not in symbol[0]:
        try:
            ask, bid = rate('usd' + symbol[0][3:].lower(), str(swap_settlment_time))  # 查询USD{报价货币}结算时间时的最新报价
            # 计算公式: 手数 * 合约单位 * 买/卖方向的利率 * 开仓价 / 100 / 360 / USD{报价货币}的ask价格
            swap_result = lots[0] * 100000 * swap_value * price[0] / 100 / 360 / ask
            return f'利息:{swap_result:.2f}'
        except pymysql.err.ProgrammingError:
            ask, bid = rate(symbol[0][3:].lower() + 'usd', str(swap_settlment_time))  # 查询{报价货币}USD结算时间时的最新报价
            # 计算公式: 手数 * 合约单位 * 买/卖方向的利率 * 开仓价 / 100 / 360 * {报价货币}USD的Bid价格
            swap_result = lots[0] * 100000 * swap_value * price[0] / 100 / 360 * bid
            return f'利息:{swap_result:.2f}'
    # 持仓货币对是USD结尾的,直接取对应结果
    elif 'USD' == symbol[0][3:]:
        # 计算公式: 手数 * 合约单位 * 买/卖方向的利率 * 开仓价 / 100 / 360
        swap_result = lots[0] * 100000 * swap_value * price[0] / 100 / 360
        return f'利息:{swap_result:.2f}'
    # 持仓货币对是USD开头的,利息的结果除以该货币对的ask价格
    elif 'USD' == symbol[0][:3]:
        ask, bid = rate(symbol[0], str(swap_settlment_time))  # 查询当前货币对结算时间时的最新报价
        # 计算公式: 手数 * 合约单位 * 买/卖方向的利率 * 开仓价 / 100 / 360 / 该货币对的ask价格
        swap_result = lots[0] * 100000 * swap_value * price[0] / 100 / 360 / ask
        return f'利息:{swap_result:.2f}'


if __name__ == '__main__':
    print(swap())
