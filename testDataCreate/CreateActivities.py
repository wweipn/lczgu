# -*- coding: utf-8 -*-
# @Time: 2021/2/2 10:02
# @Author: Waipang

import common
from datetime import datetime, timedelta


def get_activity_goods(num, activity_type=1, activity_num=5, limit_num=5):
    """
    生成创建活动时所需的商品数据
    :param limit_num: 限购数量(限时抢购用)
    :param activity_num: 活动库存
    :param activity_type: 活动类型: 1: 普通活动(第二件半价,满减) 2: 限时抢购活动 3: 拼团活动
    :param num: 需要添加的商品数量
    :return:
    """

    sql = f"""
    SELECT
        id,
        goods_id,
        price
    FROM
        goods_sku where goods_id in (SELECT
        a.id
        FROM
    ( SELECT id FROM goods_spu WHERE STATUS = 3 AND type = 0 ORDER BY RAND( ) LIMIT {num} ) AS a)
    """

    sql = f"""
    SELECT
        goods_sku.id,
        goods_sku.goods_id,
        goods_sku.price
    FROM
     goods_sku
        left join goods_spu ON goods_spu.id = goods_sku.goods_id
    where
        goods_spu.status = 3
    and
        goods_spu.audit_status = 1
    and
     goods_spu.is_deleted = 0
    and
        goods_spu.type = 0
    and
        goods_sku.id in (1374997683666677762,1374997683607957506,1374997683549237249,1374997683494711297,
        1374997683435991041,1374997683377270786,1374997683318550530,1374997683264024578,1374997683205304321,
        1374997683125612546,1372823575658962946,1372823573838635010,1372823571930226690,1372823570172813314,
        1372823550073708545,1372822340151222273,1372822340096696321,1372822340025393153,1372822338070847489,
        1372822338016321537,1372822337945018370,1372822327924826113,1372822327870300161,1372822327794802690,
        1372822325928337410,1372822325873811458,1372822325802508290,1372822323743105025,1372822323688579073,
        1372822323629858817,1372822323558555649,1372821592130658305,1372821592080326658,1372821592025800706,
        1372821591962886146,1372821590025117697,1372821589974786050,1372821589924454402,1372821589853151234,
        1372821589790236674,1372821569124900865,1372821569066180609,1372821568999071746,1372821561403187201,
        1372821561352855553,1372821561302523905,1372821561235415042,1372821559524139009,1372821559473807362,
        1372821559423475713,1372821559356366849,1372821542402990082,1372821542348464129,1372821542293938177,
        1372821542205857793,1372821540301643778,1372821540247117826,1372821540192591873,1372821540121288706,
        1372821538221268993,1372821538166743041,1372821538095439874,1372821536073785345,1372821536023453697,
        1372821535973122050,1372821535906013185,1372821525067931649,1372821525013405697,1372821524942102529,
        1372821523138551809,1372821523084025858,1372821523012722690,1372821521230143490,1372821521179811841,
        1372821521129480193,1372821521079148546,1372821521012039681,1372821519191711745,1372821519141380097,
        1372821519095242753,1372821519028133889,1372821513323880449,1372821513269354497,1372821513214828546,
        1372821513156108290,1372821513084805121,1372820139093729281,1372820139022426113) 
"""

    result = common.db.select_all(sql=sql)

    goods_list = []

    # 判断查询结果是否为空

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
    return goods_list


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
    # end_time = (now + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
    end_time = '2021-04-23 23:59:59'

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


def flash_sale(time_line, days=0, goods_num=10):
    """
    创建限时抢购活动
    :param days: 活动开始日期, 0代表今天,1代表明天,以此类推
    :param goods_num: 需要添加的商品数量
    :param time_line: 时间段, 格式: '20:30:00-21:30:00'
    :return:
    """

    admin_token = common.admin_token()
    now = datetime.now()
    start_time = (now + timedelta(days=days)).strftime('%Y-%m-%d')
    goods_list = get_activity_goods(activity_type=2, num=goods_num)
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


def assemble(day, add_num, goods_num, chief_type, team_type):
    """
    创建拼团活动
    :param add_num: 几人团
    :param team_type: 虚拟成团 0:否 1:是
    :param chief_type: 团长免单 0:否 1:是
    :param day: 开始日期, 今天传0, 明天传1, 以此类推
    :param goods_num: 添加的商品数量
    :return:
    """

    admin_token = common.admin_token()
    now = datetime.now()
    goods_list = get_activity_goods(activity_type=3, num=goods_num)
    start_date = str((now + timedelta(days=day)).date())
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


if __name__ == '__main__':

    # 第二件半价活动创建
    half_price_activity(goods_num=100)

    # 满减活动创建
    # full_discount(goods_num=10)

    # 拼团活动创建
    # assemble(day=0, add_num=2, goods_num=15, chief_type=0, team_type=0)  # 拼团活动创建

    # 限时抢购活动创建
    # flash_sale(days=0, time_line='00:00:00-09:59:59', goods_num=10)
    # flash_sale(days=1, time_line='10:00:00-13:59:59', goods_num=15)
    # flash_sale(days=1, time_line='14:00:00-19:59:59', goods_num=15)
    # flash_sale(days=1, time_line='20:00:00-23:59:59', goods_num=15)

