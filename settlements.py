import mysql_setting as ms
from exchange_rate import rate
import pymysql


def stm_result():
    order_no = input('订单号:')

    # 获取订单列表的平仓单
    close_detail = ms.Database().select(
        sql=f"SELECT symbol,side,open_Price,open_qty,swap,close_price,close_execution_time FROM trade_order WHERE "
            f"order_no = '{order_no}' AND closed_no = ''")

    if close_detail is None:
        print('订单不存在')
    else:
        symbol = close_detail[0]  # 货币对名称
        side = close_detail[1]  # 交易方向,买:1,卖:2
        open_Price = float(close_detail[2])  # 开仓价
        open_qty = float(close_detail[3])  # 开仓手数
        swap = float(close_detail[4])  # 过夜利息费
        close_price = float(close_detail[5])  # 平仓价
        close_execution_time = close_detail[6]  # 平仓时间

        if side == 1:
            p_l = round((close_price - open_Price) * 100000 * open_qty, 2)
        else:
            p_l = round((open_Price - close_price) * 100000 * open_qty, 2)
        return symbol, p_l, close_execution_time


def stm_rate_result():
    try:
        # slt_result函数取出货币对,盈亏以及平仓时间
        symbol, p_l, close_execution_time = stm_result()
        if 'USD' not in symbol:
            try:
                ask, bid = rate('usd' + symbol[3:].lower(), str(close_execution_time))  # 查询USD{报价货币}结算时间时的最新报价
                result = round(p_l / ask, 2)
            except pymysql.err.ProgrammingError:
                ask, bid = rate(symbol[3:].lower() + 'usd', str(close_execution_time))  # 查询{报价货币}USD结算时间时的最新报价
                result = round(p_l * bid, 2)
        # 持仓货币对是USD结尾的,直接取对应结果
        elif 'USD' == symbol[3:]:
            result = p_l
        # 持仓货币对是USD开头的,盈亏除以该货币对的ask价格
        elif 'USD' == symbol[:3]:
            ask, bid = rate(symbol, str(close_execution_time))  # 查询当前货币对结算时间时的最新报价
            result = round(p_l / ask, 2)
        return result
    except TypeError:
        pass


if __name__ == '__main__':
    while 1:
        print(f"该订单的最终盈亏为:{stm_rate_result()}\n")
