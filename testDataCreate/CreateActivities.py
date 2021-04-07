# -*- coding: utf-8 -*-
# @Time: 2021/2/2 10:02
# @Author: Waipang

import common
from datetime import datetime, timedelta
import time
import random
import csv


def get_activity_goods(num, sql_limit=0, activity_type=1, activity_num=5, limit_num=5, goods_type=1):
    """
    生成创建活动时所需的商品数据
    :param goods_type: 商品数据类型: 0: 验证商品详情数据 1: 常规
    :param sql_limit: sql查询偏移量(商品详情页类型的数据用)
    :param limit_num: 限购数量(限时抢购用)
    :param activity_num: 活动库存
    :param activity_type: 活动类型: 1: 普通活动(第二件半价,满减) 2: 限时抢购活动 3: 拼团活动
    :param num: 需要添加的商品数量
    :return:
    """

    sql = None

    if goods_type == 0:
        sql = f"""
        (SELECT
        sku.id AS 'sku_id',
        spu.id AS 'spu_id',
        sku.price AS 'price'
        FROM
        goods_sku sku
        LEFT JOIN goods_spu spu ON spu.id = sku.goods_id 
        WHERE
        spu.audit_status = 1 
        AND spu.STATUS = 3 
        AND spu.type = 0 
        AND sku.is_deleted = 0 
        AND spu.id != 1353286603958677506
        AND sku.price > 0
        ORDER BY RAND() 
        LIMIT {num})
        UNION 
        (SELECT
        sku.id AS 'sku_id',
        spu.id AS 'spu_id',
        sku.price AS 'price'
        FROM
        goods_sku sku
        LEFT JOIN goods_spu spu ON spu.id = sku.goods_id 
        WHERE
        spu.audit_status = 1 
        AND spu.STATUS = 3 
        AND spu.type = 0 
        AND sku.is_deleted = 0
        # AND sku.id = 1370617190700564482
        AND sku.price > 0
        LIMIT {sql_limit}, 1)
        """

    elif goods_type == 1:
        sql = f"""
        SELECT
        sku.id AS 'sku_id',
        spu.id AS 'spu_id',
        sku.price AS 'price'
        FROM
        goods_sku sku
        LEFT JOIN goods_spu spu ON spu.id = sku.goods_id 
        WHERE
        spu.audit_status = 1 
        AND spu.STATUS = 3 
        AND spu.type = 0 
        AND sku.is_deleted = 0
        AND sku.price > 0
        # AND sku.id  in (1370617444850221057,1370631959348264962) 
        ORDER BY RAND() 
        LIMIT {num}
        """

    result = common.db.select_all(sql=sql)

    goods_list = []

    # 判断查询结果是否为空
    if result:
        for goods in result:
            sku_id = goods[0]
            spu_id = goods[1]
            price = goods[2]
            if activity_type == 1:
                goods_list.append({"goodsId": spu_id, "skuId": sku_id})
            elif activity_type == 2:
                goods_list.append({
                    "goodsId": spu_id,
                    "skuId": sku_id,
                    "activityNum": activity_num,
                    "limitNum": limit_num,
                    "sort": 99,
                    "price": round(float(price * 80 / 100), 2)})
            elif activity_type == 3:
                goods_list.append({
                    "activityNum": activity_num,
                    "goodsId": spu_id,
                    "price": round(float(price * 70 / 100), 2),
                    "skuId": sku_id,
                    "sort": 99
                })
        # print(goods_list)
        return goods_list
    else:
        print('商品列表为空')
        return


def half_price_activity(goods_num):
    """
    创建第二件半价活动
    :param goods_num: 需要添加的商品数量
    :return:
    """

    admin_token = common.admin_token()
    # 获取商品数据
    goods_list = get_activity_goods(num=goods_num)

    # 定义开始时间和结束时间
    now = datetime.now()
    start_time = (now + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
    end_time = (now + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
    # end_time = (now + timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S')

    # 定义请求参数
    body = {
        "name": f"半价活动({start_time})",
        "startTime": start_time,
        "endTime": end_time,
        "goodsList": goods_list
    }

    # 请求创建活动接口
    request = common.req.request_post(url='/store/manage/promotion/half-price/saveHalfPrice',
                                      token=admin_token,
                                      body=body)
    print(f"""
    {str(body).replace("'", '"')}
    {request['text']}

    """)


def full_discount(goods_num, limit_num=100):
    """
    创建满减活动
    :param limit_num: 限制参与次数
    :param goods_num: 商品数量
    :return:
    """

    admin_token = common.admin_token()
    full_reduction_detail = []
    # 填写满减活动信息
    while 1:
        add_price = input('输入门槛(0:退出): ')
        if add_price == '0':
            break
        reduce_price = input('输入减免金额: ')
        full_reduction_detail.append({
            "addPrice": add_price,
            "reducePrice": reduce_price
        })

    # 获取商品数据
    goods_list = get_activity_goods(num=goods_num)

    # 定义开始时间和结束时间
    now = datetime.now()
    start_time = (now + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
    end_time = (now + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
    # end_time = '2021-03-29 23:59:59'

    # 定义请求参数
    body = {
        "name": f"满减活动({start_time})",
        # "name": f"纸巾专场满减活动",
        "startTime": start_time,
        "endTime": end_time,
        "modeType": 0,
        "limitNum": limit_num,
        "goodsList": goods_list,
        "addReduce": full_reduction_detail
    }

    # 请求创建活动接口
    request = common.req.request_post(url='/store/manage/promotion/full-discount/saveFullDiscount',
                                      token=admin_token,
                                      body=body)

    print(f"""
    {str(body).replace("'", '"')}
    {request['text']}

    """)


def flash_sale(time_line, sql_limit=0, goods_type=1, days=0, goods_num=10):
    """
    创建限时抢购活动
    :param sql_limit: sql查询偏移量(创建商品详情页数据时才有用)
    :param goods_type: 商品数据类型: 0: 验证商品详情数据 1: 常规
    :param days: 活动开始日期, 0代表今天,1代表明天,以此类推
    :param goods_num: 需要添加的商品数量
    :param time_line: 时间段, 格式: '20:30:00-21:30:00'
    :return:
    """

    admin_token = common.admin_token()
    now = datetime.now()
    start_time = (now + timedelta(days=days)).strftime('%Y-%m-%d')
    goods_list = get_activity_goods(activity_type=2, num=goods_num, sql_limit=sql_limit, goods_type=goods_type)
    seckill_name = f"限时抢购({start_time} {time_line})"

    body = {
        "startTime": start_time,
        "seckillName": seckill_name,
        "timeLine": time_line,
        "goodsList": goods_list
    }

    request = common.req.request_post(url='/store/manage/promotion/time-limit/saveTimeLimit',
                                      body=body,
                                      token=admin_token)
    print(f"""
    {str(body).replace("'", '"')} 
    {request['text']}

    """)


def flash_sale_from_file(time_line, days, file_name):
    """
    创建限时抢购活动
    :param file_name: 导入的文件名
    :param days: 活动开始日期, 0代表今天,1代表明天,以此类推
    :param time_line: 时间段, 格式: '20:30:00-21:30:00'
    :return:
    """

    admin_token = common.account.get_admin_token()
    now = datetime.now()
    start_time = (now + timedelta(days=days)).strftime('%Y-%m-%d')
    goods_list = get_goods_data_from_file(file_name=file_name, activity_type=1)
    seckill_name = f"限时抢购({start_time} {time_line})"

    body = {
        "startTime": start_time,
        "seckillName": seckill_name,
        "timeLine": time_line,
        "goodsList": goods_list
    }
    # print(str(body).replace("'", '"'))
    request = common.req.request_post(url='/store/manage/promotion/time-limit/saveTimeLimit',
                                      body=body,
                                      token=admin_token)
    print(f"""
    {str(body).replace("'", '"')}
    {request['text']}

    """)


def assemble(sql_limit=0, goods_type=1, day=0, add_num=None, goods_num=10, chief_type=0, team_type=0):
    """
    创建拼团活动
    :param add_num: 几人团
    :param team_type: 虚拟成团 0:否 1:是
    :param chief_type: 团长免单 0:否 1:是
    :param sql_limit: sql查询偏移量(创建商品详情页数据时才有用)
    :param goods_type: 商品数据类型: 0: 验证商品详情数据 1: 常规
    :param day: 开始日期, 今天传0, 明天传1, 以此类推
    :param goods_num: 添加的商品数量
    :return:
    """

    admin_token = common.admin_token()
    now = datetime.now()
    goods_list = get_activity_goods(activity_type=3, num=goods_num, sql_limit=sql_limit, goods_type=goods_type)
    start_date = str((now + timedelta(days=day)).date())
    if add_num is None:
        add_num = random.randint(2, 5)
    name = f"{add_num}人团{' 团长免单' if chief_type == 1 else ''} {' 虚拟成团' if team_type == 1 else ''}({start_date})"

    body = {
        "addNum": add_num,  # 参团人数
        "limitNum": 30,  # 限购数量
        "chiefType": chief_type,  # 团长免单: 0: 关闭, 1: 开启
        "teamType": team_type,  # 虚拟成团: 0: 关闭, 1: 开启
        "startDate": start_date,  # 开始时间
        "name": name,  # 活动名称
        "title": name,  # 活动标题
        "goodsList": goods_list  # 商品列表
    }

    url = '/store/manage/promotion/pintuan/savePintuan'
    request = common.req.request_post(url=url,
                                      body=body,
                                      token=admin_token)

    common.api_print(name='创建拼团活动', url=url, data=body, result=request)


def assemble_from_file(file_name, day, add_num, limit_num, chief_type, team_type):
    """
    创建拼团活动
    :param team_type: 虚拟成团 0:否 1:是
    :param day: 开始日期, 今天传0, 明天传1, 以此类推
    :param add_num: 几人团
    :param chief_type: 是否团长免单
    :param limit_num: 限购数量
    :param file_name: 文件名
    :return:
    """

    # admin_token = common.admin_token()
    now = datetime.now()
    goods_list = get_goods_data_from_file(file_name=file_name, activity_type=2)
    start_date = str((now + timedelta(days=day)).date())
    if add_num is None:
        add_num = random.randint(2, 5)
    name = f"{start_date}拼团, {add_num}人团"
    if chief_type == 1:
        name = name + ', 团长免单'

    body = {
        "addNum": add_num,  # 参团人数
        "limitNum": limit_num,  # 限购数量
        "chiefType": chief_type,  # 团长免单: 0: 关闭, 1: 开启
        "teamType": team_type,  # 虚拟成团: 0: 关闭, 1: 开启
        "startDate": start_date,  # 开始时间
        "name": name,  # 活动名称
        "title": name,  # 活动标题
        "goodsList": goods_list  # 商品列表
    }
    print(str(body).replace("'", '"'))
    # url = '/store/manage/promotion/pintuan/savePintuan'
    # request = common.req.request_post(url=url,
    #                                   body=body,
    #                                   token=admin_token)
    #
    # common.api_print(name='创建拼团活动', url=url, data=body, result=request)


def goods_detail_activity():
    for i in range(6):
        if i == 0:
            # 今天
            assemble(day=0, goods_num=20, sql_limit=i, goods_type=0)

        elif i == 1:
            # 明天
            assemble(day=1, goods_num=20, sql_limit=i, goods_type=0)

        elif i == 2:
            # 后天
            assemble(day=2, goods_num=20, sql_limit=i, goods_type=0)

        elif i == 3:
            # 当前时间段
            flash_sale(days=0, time_line='13:00:00-17:59:59', goods_num=20, goods_type=0, sql_limit=i)

        elif i == 4:
            # 下个时间段
            flash_sale(days=0, time_line='18:00:00-23:59:59', goods_num=20, goods_type=0, sql_limit=i)

        elif i == 5:
            # 下下个时间段
            flash_sale(days=1, time_line='09:00:00-11:59:59', goods_num=20, goods_type=0, sql_limit=i)
        time.sleep(1)


def get_goods_data_from_file(file_name, activity_type):
    file_path = common.get_file_path(file_name, parent_path='test_file')
    with open(file_path, 'r', encoding='GBK') as Activity_goods:
        goods_data = csv.reader(Activity_goods)
        next(goods_data)
        data_list = []
        # 限时抢购活动的商品列表
        if activity_type == 1:
            for data in goods_data:
                spu_id, sku_id, goods_type, goods_status = search_new_spu_sku_id(data[1])
                price = data[2]
                activity_num = data[3]
                limit_num = data[4]
                if goods_type == 0 and goods_status == 3:
                    data_list.append({
                        "goodsId": spu_id,
                        "skuId": sku_id,
                        "price": price,
                        "activityNum": activity_num,
                        "limitNum": limit_num,
                        "sort": 99
                    })
            return data_list

        # 拼团活动的商品列表
        elif activity_type == 2:
            for data in goods_data:
                spu_id, sku_id, goods_type, goods_status = search_new_spu_sku_id(data[1])
                price = data[2]
                activity_num = data[3]
                sort = data[4]
                if goods_type == 0 and goods_status == 3:
                    data_list.append({
                        "activityNum": activity_num,
                        "goodsId": spu_id,
                        "price": price,
                        "skuId": sku_id,
                        "sort": sort})
            return data_list


def search_new_spu_sku_id(old_sku_id):
    result = common.db.select_one(sql=f"""
    SELECT
        goods_sku.goods_id,
        goods_sku.id,
        goods_spu.type,
        goods_spu.status
    FROM
        goods_sku
    LEFT JOIN goods_spu ON goods_spu.id = goods_sku.goods_id
    WHERE	
        goods_sku.id = {old_sku_id}
    """)
    spu_id = result[0]
    sku_id = result[1]
    goods_type = result[2]
    goods_status = result[3]
    return spu_id, sku_id, goods_type, goods_status


if __name__ == '__main__':
    pass

    # 第二件半价活动创建
    # half_price_activity(goods_num=10)

    # 满减活动创建
    # full_discount(goods_num=10)

    # 拼团活动创建
    assemble(day=0, add_num=2, goods_num=10, chief_type=0, team_type=0)  # 拼团活动创建

    # 限时抢购活动创建
    # flash_sale(days=2, time_line='00:00:00-09:59:59', goods_num=15)
    # flash_sale(days=2, time_line='10:00:00-13:59:59', goods_num=15)
    # flash_sale(days=2, time_line='14:00:00-19:59:59', goods_num=15)
    # flash_sale(days=2, time_line='20:00:00-23:59:59', goods_num=15)

    # 从文件获取添加限时抢购
    # flash_sale_from_file(file_name='0330 00.csv', time_line='00:00:00-09:59:59', days=1)
    # flash_sale_from_file(file_name='0331 10.csv', time_line='10:00:00-13:59:59', days=0)
    # flash_sale_from_file(file_name='0404 14.csv', time_line='14:00:00-19:59:59', days=7)
    # flash_sale_from_file(file_name='0329 20.csv', time_line='20:00:00-23:59:59', days=0)

    # 从文件获取添加拼团
    # assemble_from_file(file_name='0402 3人团 团长免单.csv', day=0, add_num=3, limit_num=100, chief_type=1, team_type=0)

    # 验证文件获取的商品数据结构
    # print(get_goods_data_from_file(file_name='0331 10.csv', activity_type=1))
