# -*- coding: utf-8 -*-
# @Time: 2021/1/30 10:27
# @Author: Waipang

import common


def get_order_all_status(order_id):
    """
    主订单状态判断方法
    :param order_id: 主订单ID
    :return: 3:已退款, 4:待发货, 5:待收货, 6:已收货, 7:已完成
    """

    # 根据主订单ID查询子订单表的所有状态
    get_order_shop_status_result = common.db.select_all(sql=f"""
    SELECT
        status
    FROM
        order_shop
    WHERE
        order_id = "{order_id}"
    """)

    # 如果查询到的结果为空,不执行后面的代码,返回空
    if not get_order_shop_status_result:
        print('父订单不存在')
        return None

    else:
        # 定义父订单状态字典
        order_dic = {3: "已退款", 4: "待发货", 5: "待收货", 6: "已收货", 7: "已完成"}
        # 定义状态集合,后续用于存入子订单状态
        order_set = set()

        # 遍历查询到的结果,将子订单状态添加到集合中
        for order_shop_status in get_order_shop_status_result:
            status = order_shop_status[0]
            order_set.add(status)

        # 过滤掉未发货退款和已发货退款的状态
        order_set.discard(3)
        order_set.discard(8)

        # 如果集合为空,代表没有付款成功的子订单,直接视为主订单状态为已退款
        if len(order_set) == 0:
            return order_dic[3]

        # 子订单的所有状态都一样的情况下,直接作为主订单的状态
        elif len(order_set) == 1:
            return order_dic[list(order_set)[0]]

        else:
            # 子订单存在待发货或者待收货状态时走下面的判断
            if {4}.issubset(order_set) or {5}.issubset(order_set):

                # 同时存在待发货和待收货的状态, 主订单状态视为待收货
                if {4, 5}.issubset(order_set):
                    return 5
                    # return order_dic[5]

                # 只有待发货状态的子订单, 主订单状态视为待发货
                else:
                    return 4
                    # return order_dic[4]

            # 不存在待发货和待收货子订单的情况下走以下判断
            else:

                # 如果同时存在已完成和已收货的子订单或者只存在待收货的子订单, 主订单状态视为已收货
                if {6, 7}.issubset(order_set) or {6}.issubset(order_set):
                    return 6
                    # return order_dic[6]

                # 如果没有已收货的子订单, 视为全部已完成
                else:
                    return 7
                    # return order_dic[7]


if __name__ == '__main__':
    get_order_all_status(order_id=4321412)

