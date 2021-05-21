# -*- coding: utf-8 -*-
# @Time: 2021/2/2 10:02
# @Author: Waipang

import common
from datetime import datetime, timedelta


def get_activity_goods(num=10, activity_type=1, activity_num=100, limit_num=5, sku_ids=None):
    """
    生成创建活动时所需的商品数据
    :param sku_ids: sku集合, 格式: '1,2,3,4'
    :param num: 需要添加的商品数量(sku_ids有传值时不生效)
    :param limit_num: 限购数量(适用于限时抢购, 单品立减, )
    :param activity_num: 活动库存(适用于限时抢购,拼团活动)
    :param activity_type: 活动类型: 1:第二件半价,满减 2:限时抢购 3:拼团 4:活动余额特殊抵扣  5:单品立减  6:N元选M件
    :return:
    """

    sql = f"""
    SELECT
        id,
        goods_id,
        price,
        spu_name
    FROM
        goods_sku where {f'goods_id in (SELECT  a.id FROM( SELECT id FROM goods_spu WHERE STATUS = 3 AND type = 0 ORDER BY RAND( ) LIMIT {num} ) AS a)'
    if sku_ids is None else f'id in ({sku_ids})'}
    """
    result = common.db.select_all(sql=sql)

    goods_list = []
    for goods in result:
        sku_id = goods[0]
        spu_id = goods[1]
        price = goods[2]
        goods_name = goods[3]

        # 第二件半价/满减商品VO
        if activity_type == 1:
            goods_list.append({"goodsId": spu_id, "skuId": sku_id})

        # 限时抢购商品VO
        elif activity_type == 2:
            goods_list.append({
                "goodsId": spu_id,
                "skuId": sku_id,
                "activityNum": activity_num,
                "limitNum": limit_num,
                "goodsName": goods_name,
                "sort": 99,
                "price": round(float(price * 80 / 100), 2)})

        # 拼团商品VO
        elif activity_type == 3:
            goods_list.append({
                "activityNum": activity_num,
                "goodsId": spu_id,
                "goodsName": goods_name,
                "price": round(float(price * 75 / 100), 2),
                "skuId": sku_id,
                "sort": 99
            })

        # 活动余额特殊抵扣商品VO
        elif activity_type == 4:
            goods_list.append({
                'skuId': sku_id,
                'spuId': spu_id
            })

        # 单品立减商品VO
        elif activity_type == 5:
            goods_list.append({
                'goodsId': spu_id,
                'skuId': sku_id,
                'activityPrice': round(float(price * 85 / 100), 2),
                'limitNum': limit_num
            })
        # N元选M件商品VO
        elif activity_type == 6:
            goods_list.append({
                'goodsId': spu_id,
                'skuId': sku_id,
                'limitBuyNum': limit_num
            })

    return goods_list


def half_price_activity(is_over_lap=0, **kwargs):
    """
    创建第二件半价活动
    :param is_over_lap: 是否支持活动余额抵扣 0:支持, 1:不支持
    :param kwargs:
    :return:
    """

    # 获取商品数据
    goods_list = get_activity_goods(activity_type=1, **kwargs)

    # 定义开始时间和结束时间
    now = datetime.now()
    start_time = (now + timedelta(minutes=0.5)).strftime('%Y-%m-%d %H:%M:%S')
    end_time = (now + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')

    # 定义请求参数
    body = {
        "name": f"半价活动({start_time})",
        "startTime": start_time,
        "endTime": end_time,
        "goodsList": goods_list,
        'isOverlap': is_over_lap
    }

    # 请求创建活动接口
    request = common.req.request_post(url='/store/manage/promotion/half-price/saveHalfPrice',
                                      token=common.admin_token(),
                                      body=body)

    common.api_print(name='创建半价活动', url=request['url'], data=body, result=request)


def full_discount(limit_num=100, is_over_lap=0, **kwargs):
    """
    创建满减活动
    :param limit_num: 阶梯满减限制参与次数
    :param is_over_lap: 是否支持活动余额抵扣 0:支持, 1:不支持
    :return:
    """

    full_reduction_detail = []
    # 填写满减活动信息
    while 1:
        add_price = input('输入门槛(0:退出): ')
        if add_price == '0':
            break
        reduce_price = input('输入减免金额: ')
        limit_num = int(input('输入参与次数(0:不限制): ')) if limit_num is None else limit_num
        full_reduction_detail.append({
            "addPrice": add_price,
            "reducePrice": reduce_price,
            "limitNum": limit_num,
            'isOverlap': is_over_lap
        })

    # 获取商品数据
    goods_list = get_activity_goods(activity_type=1, **kwargs)

    # 定义开始时间和结束时间
    now = datetime.now()
    start_time = (now + timedelta(minutes=0.5)).strftime('%Y-%m-%d %H:%M:%S')
    end_time = (now + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')

    # 定义请求参数
    body = {
        "name": f"满减活动({start_time})",
        "startTime": start_time,
        "endTime": end_time,
        "modeType": 0,
        "goodsList": goods_list,
        "addReduce": full_reduction_detail
    }

    # 请求创建活动接口
    request = common.req.request_post(url='/store/manage/promotion/full-discount/saveFullDiscount',
                                      token=common.admin_token(),
                                      body=body)

    common.api_print(name='创建满减活动', url=request['url'], data=body, result=request)


def flash_sale(time_line, days=0, **kwargs):
    """
    创建限时抢购活动
    :param days: 活动开始日期, 0代表今天,1代表明天,以此类推
    :param time_line: 时间段, 格式: '20:30:00-21:30:00'
    :return:
    """

    admin_token = common.admin_token()
    now = datetime.now()
    start_time = (now + timedelta(days=days)).strftime('%Y-%m-%d')
    goods_list = get_activity_goods(activity_type=2, **kwargs)
    activity_name = f"限时抢购({start_time} {time_line})"

    body = {
        "startTime": start_time,
        "seckillName": activity_name,
        "timeLine": time_line,
        "goodsList": goods_list
    }

    request = common.req.request_post(url='/store/manage/promotion/time-limit/saveTimeLimit',
                                      body=body,
                                      token=admin_token)
    if request['code'] != 200:
        print(f'活动 - {activity_name}添加失败, code: {request["code"]}, 错误信息: {request["desc"]}')
        if request['code'] in (8068, 8069):
            return
        else:
            flash_sale(time_line=time_line, days=days, **kwargs)
    else:
        common.api_print(name='创建限时抢购活动', url=request['url'], data=body, result=request)


def assemble(day, add_num, chief_type, team_type, limit_num=100, **kwargs):
    """
    创建拼团活动
    :param add_num: 几人团
    :param limit_num: 活动限购数量
    :param team_type: 虚拟成团 0:否 1:是
    :param chief_type: 团长免单 0:否 1:是
    :param day: 开始日期, 今天传0, 明天传1, 以此类推
    :return:
    """
    admin_token = common.admin_token()
    goods_list = get_activity_goods(activity_type=3, **kwargs)
    now = datetime.now()
    start_date = str((now + timedelta(days=day)).date())
    name = f"{add_num}人团{' 团长免单' if chief_type == 1 else ''} {' 虚拟成团' if team_type == 1 else ''}({start_date})"

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

    url = '/store/manage/promotion/pintuan/savePintuan'
    request = common.req.request_post(url=url,
                                      body=body,
                                      token=admin_token)
    if request['code'] != 200:
        print(f'活动 - {name}添加失败, code: {request["code"]} 错误信息: {request["desc"]}')
        if request['code'] in (8068, 8069):
            return
        else:
            assemble(day, add_num, chief_type, team_type, **kwargs)
    else:
        common.api_print(name='创建拼团活动', url=request['url'], data=body, result=request)


def create_special_deduct(member_ratio=15, vip_ratio=30, **kwargs):
    """
    创建活动余额特殊抵扣活动
    :param member_ratio: 普通会员活动余额抵扣比例
    :param vip_ratio: VIP活动余额抵扣比例
    :return:
    """

    now = datetime.now()  # 当前时间
    start_time = (now + timedelta(minutes=0.2)).strftime('%Y-%m-%d  %H:%M:%S')  # 开始时间
    end_time = (now + timedelta(days=30)).strftime('%Y-%m-%d  %H:%M:%S')  # 结束时间
    name = f'活动特殊抵扣(普通会员: {member_ratio}, VIP: {vip_ratio})'  # 活动名称
    member_ratio = member_ratio  # 普通会员抵扣比例
    vip_ratio = vip_ratio  # VIP抵扣比例

    body = {
        'activityMoneySpecialDeductGoodsVOList': get_activity_goods(activity_type=4, **kwargs),
        'activityMoneySpecialDeductVO': {
            'name': name,
            'startTime': start_time,
            'endTime': end_time,
            'memberRatio': member_ratio,
            'vipRatio': vip_ratio
        }
    }

    request = common.req.request_post(token=common.admin_token(), url='/store/manage/specialDeduct/add', body=body)
    common.api_print(name='创建活动余额特殊抵扣', url=request['url'], data=body, result=request)


def create_single_reduce(is_over_lap=0, **kwargs):
    """
    创建单品立减活动
    :param is_over_lap: 是否支持活动余额抵扣 0:支持, 1:不支持
    :param kwargs:
    :return:
    """
    now = datetime.now()  # 当前时间
    start_time = (now + timedelta(minutes=0.2)).strftime('%Y-%m-%d  %H:%M:%S')  # 开始时间
    end_time = (now + timedelta(days=30)).strftime('%Y-%m-%d  %H:%M:%S')  # 结束时间

    body = {
        'name': 0,
        'isOverlap': is_over_lap,
        'skuList': get_activity_goods(activity_type=5, **kwargs),
        'startTime': start_time,
        'endTime': end_time
    }
    request = common.req.request_post(token=common.admin_token(), url='/store/manage/promotion/single-reduce/saveSingleGoodsMinus', body=body)
    common.api_print(name='创建单品立减活动', url=request['url'], data=body, result=request)


def create_full_amount_choose_num(threshold_amount, threshold_num, limit_buy_num=100, is_over_lap=0, **kwargs):
    """
    创建N元选M件活动
    :param threshold_amount: 满N元
    :param threshold_num: 选M件
    :param limit_buy_num: 限购数量
    :param is_over_lap: 是否支持活动余额抵扣 0:支持, 1:不支持
    :return:
    """

    now = datetime.now()  # 当前时间
    start_time = (now + timedelta(minutes=0.2)).strftime('%Y-%m-%d  %H:%M:%S')  # 开始时间
    end_time = (now + timedelta(days=30)).strftime('%Y-%m-%d  %H:%M:%S')  # 结束时间

    body = {
        'isCanUseActivityMoney': is_over_lap,
        'name': f'{threshold_amount}元选{threshold_num}件活动({start_time})',
        'startTime': start_time,
        'endTime': end_time,
        'thresholdAmount': threshold_amount,
        'thresholdNum': threshold_num,
        'fullAmountChooseNumGoodsVOList': get_activity_goods(activity_type=6, limit_num=limit_buy_num, **kwargs)
    }

    request = common.req.request_post(token=common.admin_token(), url='/store/manage/activity/add', body=body)
    common.api_print(name=f'创建{threshold_amount}元选{threshold_num}件活动', url=request['url'], data=body, result=request)


if __name__ == '__main__':

    "创建第二件半价活动"
    half_price_activity(goods_num=100)

    "创建满减活动"
    full_discount(goods_num=10, limit_num=1)

    "创建单品立减活动"
    create_single_reduce()

    "创建N元选M件活动"
    create_full_amount_choose_num(threshold_amount=100, threshold_num=3)

    "拼团活动创建"
    assemble(day=6, add_num=3, chief_type=1, team_type=0)  # 拼团活动创建
    # assemble(day=6, add_num=2, goods_num=15, chief_type=0, team_type=1)  # 拼团活动创建

    "限时抢购活动创建"
    flash_sale(days=0, time_line='00:00:00-09:59:59', goods_num=10)
    # flash_sale(days=0, time_line='10:00:00-13:59:59', goods_num=10)
    # flash_sale(days=0, time_line='14:00:00-19:59:59', goods_num=10)
    # flash_sale(days=0, time_line='20:00:00-23:59:59', goods_num=10)

    "活动余额特殊抵扣配置添加"
    create_special_deduct(member_ratio=22, vip_ratio=33, sku_ids='1370631960673665025')
