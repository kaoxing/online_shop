import base64
import os
from pydoc import describe
import random
from tokenize import Double
from unittest import result
import coder
import re
from pathlib import Path
from select import select
from django.db import connection
from datetime import datetime
import time

BASE_DIR = Path(__file__).resolve().parent.parent


def shopper_exist(id, pwd):
    # 用户登录，pwd = coder.decode(pwd,id)，返回为None则不存在
    cursor = connection.cursor()
    sql = "select * from shopper_table where shopper_num='{}'".format(id)
    cursor.execute(sql)
    rows = cursor.fetchall()
    if len(rows) != 0 and rows[0][2] == pwd:
        return rows[0][1]
    return None


def shop_exist(id, pwd):
    # 商家登录,pwd = coder.decode(pwd,id)，返回None则不存在
    cursor = connection.cursor()
    sql = "select * from shop_table where shop_num='{}'".format(id)
    cursor.execute(sql)
    rows = cursor.fetchall()
    if len(rows) != 0 and rows[0][2] == pwd:
        return rows[0][1]
    return None


def save_photo(photo, goods_num):
    cursor = connection.cursor()
    if photo == '1' or photo is None:
        # 如果图片为空
        return "/static/img/default.jpg"
    else:
        # 如果图片不为空，处理照片
        c = re.sub(r'%0A', "\\n", photo)
        d = re.sub(r'data:image/png;base64,', "", c)
        d = re.sub(r'data:image/jpg;base64,', "", d)
        d = re.sub(r'data:image/jpeg;base64,', "", d)
        photo = base64.b64decode(d)
        # 处理图片地址
        filepath = os.path.join(BASE_DIR, 'app01/static/img/')
        filename = unique_name(filepath)
        filepath = filepath + filename  # I assume you have a way of picking unique filenames
        ret = "/static/img/" + filename
        if goods_num is not None:
            # 如果是‘修改’操作
            sql = "select goods_picture from goods_table where goods_num = '{0}'".format(goods_num)
            cursor.execute(sql)
            rows = cursor.fetchall()
            pic_path = rows[0][0]
            if pic_path != "/static/img/default.jpg":
                # 如果不是默认图片
                ret = pic_path
                filepath = os.path.join(BASE_DIR, 'app01' + pic_path)
        # 保存图片文件
        with open(filepath, 'wb') as f:
            f.write(photo)
        return ret


def unique_name(path):
    n = len(os.listdir(path))
    return "image{0}.jpg".format(n)


def add_cart(id, goods_num):
    cursor = connection.cursor()
    sql = "select * from cart_table where shopper_num = '{0}' and goods_num = '{1}'".format(id, goods_num)
    cursor.execute(sql)
    rows = cursor.fetchall()
    if len(rows) == 0:
        sql = "insert into cart_table values('{0}','{1}',{2})".format(id, goods_num, 1)
    else:
        sql = "update cart_table set cart_number = cart_number+1 where shopper_num = '{0}' and goods_num = '{1}'".format(
            id, goods_num)
    cursor.execute(sql)


def cart_show(id):
    cursor = connection.cursor()
    sql = "select * from cart_view where shopper_num = '{0}'".format(id)
    cursor.execute(sql)
    rows = cursor.fetchall()
    list = []
    for row in rows:
        dic = {
            "goods_num": row[0],
            "goods_name": row[1],
            'goods_description': row[2],
            "goods_price": row[3],
            'goods_photo': row[4],
            "shop_name": row[5],
            "shop_num": row[6],
            'shopper_description': row[7],  # 商家描述
            "inventory_number": row[8],
            "inventory_sold": row[9],
            "goods_number": row[11]
        }
        list.append(dic)
    return list


def cart_post(data):
    cursor = connection.cursor()
    if isinstance(data, list):
        # 若data为数组类型，则为购买
        shopper_num = data[0][0]
        # 查用户钱包
        sql = "select shopper_money from shopper_table where shopper_num = '{0}'".format(shopper_num)
        cursor.execute(sql)
        result = cursor.fetchall()
        shopper_money = to_money(result[0][0])
        # 购买验证
        total_money = 0
        for i in data[1:]:
            # 获取商品号
            goods_num = i.get("goods_num")
            # 查商品的价格和购买数量
            sql = "select goods_price,cart_number from cart_view where goods_num = '{0}'".format(goods_num)
            cursor.execute(sql)
            result = cursor.fetchall()
            goods_price = to_money(result[0][0])
            content_number = result[0][1]
            # 查商品的库存量
            sql = "select inventory_amount from inventory_table where goods_num = '{0}'".format(goods_num)
            cursor.execute(sql)
            result = cursor.fetchall()
            inventory_amount = result[0][0]
            # 判断库存是否充足
            if inventory_amount < content_number:
                # 如果库存不充足
                return "{0}库存不足".format(goods_num)
            else:
                # 如果库存充足
                money = goods_price * content_number  # 计算价格
                total_money += money  # 计算总价
        # 判断用户余额是否充足
        if shopper_money < total_money:
            # 如果用户余额不足
            return "用户余额不足"
        else:
            # 如果用户余额充足，此时生成订单
            # 向订单表插入订单信息
            order_num = 'order' + ''.join([random.choice('0123456789') for i in range(5)])  # 随机生成订单号
            order_address = data[0][1]
            sql = "insert into order_table values('{0}',now()+'8:00','{1}','{2}')".format(order_num, shopper_num,
                                                                                          order_address)
            cursor.execute(sql)
            # 用户钱包更新
            sql = "update shopper_table set shopper_money = shopper_money - money({0}) where shopper_num = '{1}'".format(
                total_money, shopper_num)
            cursor.execute(sql)
            for i in data[1:]:
                goods_num = i.get("goods_num")
                # 查商品的购买数量
                sql = "select cart_number from cart_view where goods_num = '{0}'".format(goods_num)
                cursor.execute(sql)
                result = cursor.fetchall()
                cart_number = result[0][0]
                # 向包含表里插入订单包含信息
                sql = "insert into content_table values('{0}','{1}',{2},'待发货')".format(order_num, goods_num,
                                                                                          cart_number)
                cursor.execute(sql)
                # 删购物车表中对应元组
                sql = "delete from cart_table where shopper_num = '{0}' and goods_num = '{1}'".format(shopper_num,
                                                                                                      goods_num)
                cursor.execute(sql)
                # 更新商家的库存表
                sql = "update inventory_table set inventory_amount = inventory_amount - {0},inventory_sold = inventory_sold + {0} where goods_num = '{1}'".format(
                    cart_number, goods_num)
                cursor.execute(sql)
            return "下单成功"
    else:
        # 注意，在地址操作时，数量为空，数量操作时，地址为空，购买时，都不为空
        ope = data.get("ope")
        shopper_num = data.get('id')
        goods_num = data.get('goods_num')
        goods_number = data.get('goods_number')
        if ope == '数量':
            sql = "update cart_table set cart_number = {0} where shopper_num = '{1}' and goods_num = '{2}'".format(
                goods_number, shopper_num, goods_num)
        elif ope == '删除':
            sql = "delete from cart_table where shopper_num = '{0}' and goods_num = '{1}'".format(shopper_num,
                                                                                                  goods_num)
        cursor.execute(sql)


def index_search(info, way):
    cursor = connection.cursor()
    if way == '1':
        sql = "select * from goods_view where goods_name like '%{0}%' and inventory_amount <> -1".format(info)
    elif way == '2':
        sql = "select * from goods_view where shop_name like '%{0}%' and inventory_amount <> -1".format(info)
    cursor.execute(sql)
    rows = cursor.fetchall()
    list = []
    for row in rows:
        dic = {
            "goods_num": row[0],
            "goods_name": row[1],
            'goods_description': row[2],
            "goods_price": row[3],
            'goods_photo': row[4],
            "shop_name": row[5],
            "shop_num": row[6],
            'shopper_description': row[7],  # 商家描述
            "inventory_number": row[8],
            "inventory_sold": row[9],
        }
        list.append(dic)
    return list


def index_goods_evaluation(data):
    cursor = connection.cursor()
    goods_num = data.get("goods_num")
    sql = "select * from evaluation_view where goods_num = '{0}'".format(goods_num)
    cursor.execute(sql)
    table = []
    rows = cursor.fetchall()
    for row in rows:
        dic = {
            'shopper_name': row[0],
            'shopper_num': row[1],
            'order_num': row[2],
            'evaluation_time': timestamp_to_time(row[4]),
            'evaluation_information': row[5],
        }
        table.append(dic)
    return table


def mgood_get(id):
    cursor = connection.cursor()
    sql = "select * from shop_goods_view where shop_num = '{0}' and inventory_amount <> -1".format(id)
    cursor.execute(sql)
    rows = cursor.fetchall()
    list = []
    for row in rows:
        dic = {
            "goods_num": row[1],
            "goods_name": row[2],
            'goods_description': row[3],
            "goods_price": row[4],
            'goods_photo': row[5],
            "inventory_number": row[6],
            'inventory_sold': row[7]
        }
        list.append(dic)
    return list


def mgood_post(data):
    cursor = connection.cursor()
    ope = data.get('ope')
    if ope == '下架':
        goods_num = data.get('goods_num')
        sql = "update inventory_table set inventory_amount = -1 where goods_num = '{0}'".format(goods_num)
        cursor.execute(sql)
        # sql = "delete from inventory_table  where goods_num = '{0}'".format(goods_num)
        # cursor.execute(sql)
        # sql = "delete from goods_table  where goods_num = '{0}'".format(goods_num)
        # cursor.execute(sql)
    else:
        name = data.get("goods_name")
        description = data.get("goods_description")
        # description = description.replace("\n", '')
        price = data.get("goods_price")
        amount = data.get("goods_number")
        shop_num = data.get("id")
        if ope == '上架':
            goods_num = 'goods' + ''.join([random.choice('0123456789') for i in range(5)])  # 随机生成商品号
            picture = save_photo(data.get('goods_photo'), None)
            sql = "insert into goods_table values ('{0}','{1}','{2}',{3},'{4}')".format(goods_num, name, description,
                                                                                        price,
                                                                                        picture)
            cursor.execute(sql)
            sql = "insert into inventory_table values('{0}','{1}',{2},{3})".format(goods_num, shop_num, amount, 0)
            cursor.execute(sql)
        elif ope == '修改':
            goods_num = data.get('goods_num')
            picture = save_photo(data.get('goods_photo'), goods_num)
            sql = ""
            if picture == "/static/img/default.jpg":
                sql = "update goods_table set goods_name = '{0}',goods_description = '{1}',goods_price= {2} where goods_num = '{3}'".format(
                    name, description, price, goods_num)
            else:
                sql = "update goods_table set goods_name = '{0}',goods_description = '{1}',goods_price= {2},goods_picture= '{3}' where goods_num = '{4}'".format(
                    name, description, price, picture, goods_num)
            cursor.execute(sql)
            sql = "update inventory_table set inventory_amount = {0} where goods_num = '{1}'".format(
                amount, goods_num)
            cursor.execute(sql)


def shopper_find_money(id):
    # 查询用户余额
    cursor = connection.cursor()
    sql = "select shopper_money from shopper_table where shopper_num='{0}'".format(id)
    cursor.execute(sql)
    rows = cursor.fetchall()
    if len(rows) == 0:
        return 0
    money = rows[0][0]
    money = money.replace(",", '')
    if money[0] == '-':
        return '-' + money[2:]
    else:
        return money[1:]


def shopper_add_money(id, pwd, cMoney):
    # 用户充值
    cursor = connection.cursor()
    sql = "UPDATE shopper_table set shopper_money = shopper_money + money({2}) " \
          "WHERE shopper_num = '{0}' AND shopper_password = '{1}';".format(id, pwd, cMoney)
    cursor.execute(sql)


def shopper_sub_money(id, pwd, cMoney):
    # 用户提现
    cursor = connection.cursor()
    sql = "UPDATE shopper_table set shopper_money = shopper_money - money({2}) " \
          "WHERE shopper_num = '{0}' AND shopper_password = '{1}';".format(id, pwd, cMoney)
    cursor.execute(sql)


def shop_find_money(id):
    # 查询商家余额
    cursor = connection.cursor()
    sql = "select shop_money from shop_table where shop_num='{0}'".format(id)
    cursor.execute(sql)
    rows = cursor.fetchall()
    if len(rows) == 0:
        return 0
    money = rows[0][0]
    money = money.replace(",", '')
    if money[0] == '-':
        return '-' + money[2:]
    else:
        return money[1:]


def to_money(money: str):
    money = money.replace(",", '')
    if money[0] == '-':
        money = '-' + money[2:]
    else:
        money = money[1:]
    return float(money)


def shop_add_money(id, pwd, cMoney):
    # 商家充值
    cursor = connection.cursor()
    sql = "UPDATE shop_table set shop_money = shop_money + money({2}) " \
          "WHERE shop_num = '{0}' AND shop_password = '{1}';".format(id, pwd, cMoney)
    cursor.execute(sql)


def shop_sub_money(id, pwd, cMoney):
    # 商家提现
    cursor = connection.cursor()
    sql = "UPDATE shop_table set shop_money = shop_money - money({2}) " \
          "WHERE shop_num = '{0}' AND shop_password = '{1}';".format(id, pwd, cMoney)
    cursor.execute(sql)


def shopper_change_info(id, rName, sPwd, rPwd):
    # 用户账号信息修改
    cursor = connection.cursor()
    sql = "UPDATE shopper_table set shopper_name = '{0}'" \
          "WHERE shopper_num = '{1}';".format(rName, id)
    cursor.execute(sql)
    if len(rPwd) == 0:
        return True
    sql = "select * from shopper_table where shopper_num = '{0}' and shopper_password = '{1}'".format(id, sPwd)
    cursor.execute(sql)
    rows = cursor.fetchall()
    if len(rows) == 0 or len(rPwd) > 12 or len(rPwd) < 6:
        return False
    sql = "UPDATE shopper_table set shopper_password = '{0}' " \
          "WHERE shopper_num = '{1}' AND shopper_password = '{2}';".format(rPwd, id, sPwd)
    cursor.execute(sql)
    return True


def shop_change_info(id, rName, sPwd, rPwd, rDes):
    # 用户账号信息修改
    cursor = connection.cursor()
    sql = "UPDATE shop_table set shop_name = '{0}',shop_description = '{2}'" \
          "WHERE shop_num = '{1}';".format(rName, id, rDes)
    cursor.execute(sql)
    if len(rPwd) == 0:
        return True
    sql = "select * from shop_table where shop_num = '{0}' and shop_password = '{1}'".format(id, sPwd)
    cursor.execute(sql)
    rows = cursor.fetchall()
    if len(rows) == 0 or len(rPwd) > 12 or len(rPwd) < 6:
        return False
    sql = "UPDATE shop_table set shop_password = '{0}' " \
          "WHERE shop_num = '{1}' AND shop_password = '{2}';".format(rPwd, id, sPwd)
    cursor.execute(sql)
    return True

    cursor.execute(sql)


def shop_get_des(id):
    # 获取商家描述
    cursor = connection.cursor()
    sql = "select shop_description from shop_table where shop_num = '{0}'".format(id)
    cursor.execute(sql)
    rows = cursor.fetchall()
    return rows[0][0]


def shopper_order_get(id):
    # 用户订单查询
    cursor = connection.cursor()
    sql = "select * from shopper_order_view where shopper_num = '{0}'".format(id)
    cursor.execute(sql)
    rows = cursor.fetchall()
    order_list = []
    for row in rows:
        dic = {
            "shopper_num": row[0],
            "order_num": row[1],
            "goods_number": row[2],
            "goods_name": row[3],
            "shop_name": row[4],
            'shop_num': row[5],
            'goods_num': row[6],
            'order_date': timestamp_to_time(row[7]),
            'goods_photo': row[8],
            'user_address': row[9],
            'statu': row[10],
            'goods_price': row[11]
        }
        order_list.append(dic)
    return order_list


def shop_order_get(id):
    # 商家订单查询
    cursor = connection.cursor()
    sql = "select * from shop_order_view where shop_num = '{0}'".format(id)
    cursor.execute(sql)
    rows = cursor.fetchall()
    order_list = []
    for row in rows:
        dic = {
            "shop_num": row[0],
            "order_num": row[1],
            "goods_number": row[2],
            "goods_name": row[3],
            "shopper_name": row[4],
            'shopper_num': row[5],
            'goods_num': row[6],
            'order_date': timestamp_to_time(row[7]),
            'goods_photo': row[8],
            'user_address': row[9],
            'statu': row[10],
            'goods_price': row[11]
        }
        order_list.append(dic)
    return order_list


def shopper_comment(data):
    # 用户评论
    cursor = connection.cursor()
    comment = data.get("commentInfo")
    goods_num = data.get("goods_num")
    order_num = data.get("order_num")
    sql = "insert into evaluation_table values('{0}','{1}',now()+'8:00','{2}')".format(order_num, goods_num, comment)
    # sql = "insert evaluation_table set evaluation_information = '{0}'," \
    #       "goods_num = '{1}', order_num = '{2}', evaluation_time = now() ".format(comment, goods_num, order_num)
    cursor.execute(sql)


def timestamp_to_time(timestamp):
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def shopper_refund(data):
    cursor = connection.cursor()
    order_num = data.get("order_num")
    goods_num = data.get("goods_num")
    # 用户订单查询
    sql = "select shopper_num,content_number,goods_price from shopper_order_view where order_num = '{0}' and goods_num = '{1}'".format(
        order_num, goods_num)
    cursor.execute(sql)
    rows = cursor.fetchall()
    shopper_num = rows[0][0]
    content_number = rows[0][1]
    goods_price = to_money(rows[0][2])
    total_money = content_number * goods_price
    # 用户钱包更新
    sql = "update shopper_table set shopper_money = shopper_money + money({0}) where shopper_num = '{1}'".format(
        total_money, shopper_num)
    cursor.execute(sql)
    # 更新包含表的订单包含信息
    sql = "update content_table set content_status = '已退货' where order_num = '{0}' and goods_num = '{1}'".format(
        order_num, goods_num)
    cursor.execute(sql)
    # 更新商家的库存表
    sql = "update inventory_table set inventory_amount = inventory_amount + {0},inventory_sold = inventory_sold - {0} where goods_num = '{1}'".format(
        content_number, goods_num)
    cursor.execute(sql)


def shopper_receive(data):
    # 用户收货
    cursor = connection.cursor()
    goods_num = data.get("goods_num")
    order_num = data.get("order_num")
    sql = "update content_table set content_status = '已收货' where order_num = '{0}' and goods_num = '{1}'".format(
        order_num, goods_num)
    cursor.execute(sql)
    sql = "select shop_num,content_number,goods_price from shop_order_view where order_num = '{0}' and goods_num = '{1}'" \
        .format(order_num, goods_num)
    cursor.execute(sql)
    rows = cursor.fetchall()
    if len(rows[0]) == 0:
        return
    money = to_money(rows[0][2]) * int(rows[0][1])
    sql = "update shop_table set shop_money = shop_money + money({0}) where shop_num = '{1}'".format(money, rows[0][0])
    cursor.execute(sql)


def shop_send_order(data):
    '''商家发货'''
    cursor = connection.cursor()
    goods_num = data.get('goods_num')
    order_num = data.get('order_num')
    sql = "update content_table set content_status = '已发货' where goods_num = '{0}' and order_num = '{1}'".format(
        goods_num, order_num)
    cursor.execute(sql)


def shop_cancel_order(data):
    '''商家取消订单'''
    cursor = connection.cursor()
    goods_num = data.get('goods_num')
    order_num = data.get('order_num')
    sql = "select shopper_num,content_number,goods_price from shopper_order_view " \
          "where order_num = '{0}' and goods_num = '{1}'" \
        .format(order_num, goods_num)
    cursor.execute(sql)
    rows = cursor.fetchall()
    if len(rows[0]) == 0:
        return
    money = to_money(rows[0][2]) * int(rows[0][1])
    sql = "update shopper_table set " \
          "shopper_money = shopper_money + money({0}) where shopper_num = '{1}'".format(money, rows[0][0])
    cursor.execute(sql)
    sql = "delete from content_table where goods_num = '{0}' and order_num = '{1}'".format(goods_num, order_num)
    cursor.execute(sql)
    sql = "update inventory_table set inventory_amount = inventory_amount + {0},inventory_sold = inventory_sold - {0} " \
          "where goods_num = '{1}'".format(rows[0][1], goods_num)
    cursor.execute(sql)


def setting_get_shopper_pwd(id):
    cursor = connection.cursor()
    sql = "select shopper_password from shopper_table where shopper_num = '{0}'".format(id)
    cursor.execute(sql)
    rows = cursor.fetchall()
    return rows[0][0]

def ssetting_get_shop_pwd(id):
    cursor = connection.cursor()
    sql = "select shop_password from shop_table where shop_num = '{0}'".format(id)
    cursor.execute(sql)
    rows = cursor.fetchall()
    return rows[0][0]

