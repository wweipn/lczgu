# -*- coding: utf-8 -*-
# @Time: 2021/2/1 11:54
# @Author: Waipang

import Config
import common
import os
import requests
import time

# 连接老系统数据库
old_db = common.Database()
old_db.database = Config.get_db(env='old_test_goods')

# 获取上一级路径(也就是该项目的根目录), 比如: D:\PythonProject\Lczgu
GoodsImagePath = r'D:\GoodsImage'


def get_goods_png(goods_id):
    result = old_db.select_one(sql=f"""
    SELECT
        goods_name, category_id, goods_id, brand_id, mobile_intro, original
    FROM
        es_goods
    WHERE
        goods_id = '{goods_id}'
    """)
    name = result[0]

    if name.find('/') != -1 and name.find('*') != -1:
        name = name.replace('/', ' ').replace('*', 'X')
    elif name.find('/') != -1:
        name = name.replace('/', ' ')
    elif name.find('*') != -1:
        name = name.replace('*', 'X')

    # 创建文件夹
    goods_path = os.path.join(GoodsImagePath, name)
    # 定义商品主图文件夹路径
    goods_main_path = os.path.join(goods_path, 'main')
    # 定义商品详情页文件夹路径
    goods_detail_path = os.path.join(goods_path, 'detail')

    try:
        # 创建商品名命名的文件夹
        os.mkdir(GoodsImagePath + rf'\\{name}')
        # 创建商品名命名的文件夹
        os.mkdir(goods_path + r'\\main')
        os.mkdir(goods_path + r'\\detail')
    except FileExistsError:
        print('文件夹已存在, 跳过创建过程')
        return

    # 判断商品主图列表是否为空或者有布尔值,处理后有图片则写入
    if result[4] != '':
        if result[4].find('false') != -1:
            if result[4].find('true') != -1:
                image_url_list = list(eval(result[4].replace("null", "None").replace("false", "None").
                                           replace("true", "None")))
            else:
                image_url_list = list(eval(result[4].replace("null", "None").replace("false", "None")))
        else:
            image_url_list = list(eval(result[4].replace("null", "None")))
        # 查询商品详情页图片,写入detail中
        for goods_detail_image_url in image_url_list:
            detail_url = goods_detail_image_url["content"]

            # 切割图片链接的url,只取最后的链接
            url_list = detail_url.split('/')
            image_name = url_list[-1]

            # 如果文件后缀有_300x300,则去除
            if image_name.find('_300x300') != -1:
                image_name.replace('_300x300', '')

            # 请求图片的url, 并且定义一个二进制文件的参数
            res = requests.get(detail_url)
            image = res.content

            # 定义当前图片的路径和文件名
            detail_image_path = os.path.join(goods_detail_path, image_name)

            # 写入指定路径下的文件
            with open(detail_image_path, 'wb') as image_file:
                image_file.write(image)

    # 获取商品主图,写入mainGallery中
    main_image_result = old_db.select_all(sql=f"""
    SELECT thumbnail FROM es_goods_gallery WHERE goods_id = '{goods_id}'
    """)

    for goods_main_image_url in main_image_result:
        main_image = goods_main_image_url[0]

        # 切割图片链接的url,只取最后的链接
        url_list = main_image.split('/')
        image_name = url_list[-1]

        # 如果文件后缀有_300x300,则去除
        if image_name.find('_300x300') != -1:
            image_name = image_name.replace('_300x300', '')

        # 请求图片的url, 并且定义一个二进制文件的参数
        res = requests.get(main_image)
        image = res.content

        # 定义当前图片的路径和文件名
        main_image_path = os.path.join(goods_main_path, image_name)

        # 写入指定路径下的文件
        with open(main_image_path, 'wb') as image_file:
            image_file.write(image)

    print(f'商品{name}图片添加成功')


if __name__ == '__main__':
    goods_result = old_db.select_all(sql="""
    SELECT
        eg.goods_id
    FROM
        es_goods_sku egs
        LEFT JOIN es_goods eg ON  eg.goods_id = egs.goods_id
    WHERE
        eg.market_enable = 1 -- 上下架状态: 1:上架, 0: 下架
    AND
        egs.enable_quantity > 0  -- 可用库存
    AND
        eg.is_auth = 1 -- 审核状态: 0：待审核，1：审核通过，2：审核拒绝',
    GROUP BY goods_id -- 按商品ID分组
    ORDER BY RAND() -- 随机排序
    LIMIT 1000
    """)

    for goods in goods_result:
        goodsId = goods[0]
        get_goods_png(goodsId)
        time.sleep(1)

