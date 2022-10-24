import base64
import os
from pydoc import describe
import random
from tokenize import Double
import coder
import re
from pathlib import Path
from select import select
from django.db import connection
from datetime import datetime
import time

BASE_DIR = Path(__file__).resolve().parent.parent

cursor = connection.cursor()


def shopper_exist(id, pwd):
    # 用户登录，pwd = coder.decode(pwd,id)，返回为None则不存在
    sql = "select * from shopper_table where shopper_num='{}'".format(id)
    cursor.execute(sql)
    rows = cursor.fetchall()
    print(id, pwd, rows)
    if len(rows) != 0 and rows[0][2] == pwd:
        return rows[0][1]
    return None


def shop_exist(id, pwd):
    # 商家登录,pwd = coder.decode(pwd,id)，返回None则不存在
    sql = "select * from shop_table where shop_num='{}'".format(id)
    print(sql)
    cursor.execute(sql)
    rows = cursor.fetchall()
    if len(rows) != 0 and rows[0][2] == pwd:
        return rows[0][1]
    return None


def save_photo(photo):
    # print(photo)
    c = re.sub(r'%0A', "\\n", photo)
    d = re.sub(r'data:image/png;base64,', "", c)
    d = re.sub(r'data:image/jpg;base64,', "", d)
    d = re.sub(r'data:image/jpeg;base64,', "", d)
    # print(d)
    photo = base64.b64decode(d)
    filepath = os.path.join(BASE_DIR, 'app01/static/img/')
    filename = unique_name(filepath)
    filepath = filepath + filename  # I assume you have a way of picking unique filenames
    print(filepath)
    with open(filepath, 'wb') as f:
        f.write(photo)
    return "/static/img/" + filename


def unique_name(path):
    n = len(os.listdir(path))
    return "image{0}.jpg".format(n)


def add_cart(id, goods_num):
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
    if isinstance(data, list):
        # 若data为数组类型，则为购买
        shopper_num = data[0][0]
        sql = "select shopper_money from shopper_table where shopper_num = '{0}'".format(shopper_num)
        cursor.execute(sql)  # 查用户钱包
        result = cursor.fetchall()
        shopper_money = to_money(result[0][0])
        print(shopper_money)
        total_money = 0
        for i in data[1:]:
            goods_num = i.get("goods_num")
            sql = "select goods_price,cart_number from cart_view where shopper_num = '{0}' and goods_num = '{1}'".format(
                shopper_num, goods_num)
            cursor.execute(sql)  # 查价格和数量
            result = cursor.fetchall()
            goods_price = to_money(result[0][0])
            content_number = result[0][1]
            money = goods_price * content_number  # 计算价格
            total_money += money  # 计算总价
        print(total_money)
        if shopper_money < total_money:
            # 用户余额不足
            return False
        else:
            # 用户余额充足
            order_num = 'order' + ''.join([random.choice('0123456789') for i in range(5)])  # 随机生成订单号
            order_address = data[0][1]
            sql = "insert into order_table values('{0}',now()+'8:00','{1}','{2}')".format(order_num, shopper_num,
                                                                                          order_address)
            cursor.execute(sql)  # 插订单表
            sql = "update shopper_table set shopper_money = shopper_money - money({0}) where shopper_num = '{1}'".format(
                total_money, shopper_num)
            cursor.execute(sql)  # 用户钱包更新
            # sql = "update shop_table set shop_money = shop_money + money({0})".format(total_money)
            # cursor.execute(sql)# 商家钱包更新
            for i in data[1:]:
                goods_num = i.get("goods_num")
                sql = "insert into content_table values('{0}','{1}',{2},'待发货')".format(order_num, goods_num,
                                                                                          content_number)
                cursor.execute(sql)  # 插包含表
                sql = "delete from cart_table where shopper_num = '{0}' and goods_num = '{1}'".format(shopper_num,
                                                                                                      goods_num)
                cursor.execute(sql)  # 删购物车表
            return True
    else:
        # 注意，在地址操作时，数量为空，数量操作时，地址为空，购买时，都不为空
        ope = data.get("ope")
        shopper_num = data.get('id')
        goods_num = data.get('goods_num')
        goods_number = data.get('goods_number')
        print(shopper_num, goods_num, goods_number, ope)
        if ope == '数量':
            sql = "update cart_table set cart_number = {0} where shopper_num = '{1}' and goods_num = '{2}'".format(
                goods_number, shopper_num, goods_num)
        elif ope == '删除':
            sql = "delete from cart_table where shopper_num = '{0}' and goods_num = '{1}'".format(shopper_num,
                                                                                                  goods_num)
        cursor.execute(sql)


def index_search(info, way):
    # todo 需要商品评论,即在list增加一项 "goods_comment":[...],这里需要后面是评论内容,需要按时间排序,具体某一项格式如下
    # todo ... = "2022-10-24 11:11:12 买家1(shopper123): 伊雷娜很好，孩子很喜欢，已经🐍了"
    # 即格式为 “{0} {1}({2}):{3}”.format(evaluation_time,shopper_name,shopper_num,evaluation_information)
    if way == '1':
        sql = "select * from goods_view where goods_name like '%{0}%'".format(info)
    elif way == '2':
        sql = "select * from goods_view where shop_name like '%{0}%'".format(info)
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


def mgood_get(id):
    sql = "select * from shop_goods_view where shop_num = '{0}'".format(id)
    cursor.execute(sql)
    rows = cursor.fetchall()
    # print("rows:",rows)
    list = []
    for row in rows:
        dic = {
            "goods_num": row[1],
            "goods_name": row[2],
            "inventory_number": row[6],
            "goods_price": row[4],
            'goods_description': row[3],
            'goods_photo': row[5]
        }
        # print("dic",dic)
        list.append(dic)
    return list


def mgood_post(data):
    ope = data.get('ope')
    name = data.get("goods_name")
    description = data.get("goods_description")
    price = data.get("goods_price")
    picture = save_photo(data.get('goods_photo'))
    amount = data.get("goods_number")
    shop_num = data.get("id")
    pwd = data.get('pwd')

    if ope == '上架':
        goods_num = 'goods' + ''.join([random.choice('0123456789') for i in range(5)])  # 随机生成商品号
        sql = "insert into goods_table values ('{0}','{1}','{2}',{3},'{4}')".format(goods_num, name, description, price,
                                                                                    picture)
        cursor.execute(sql)
        sql = "insert into inventory_table values('{0}','{1}',{2},{3})".format(shop_num, goods_num, amount, 0)
        cursor.execute(sql)
    elif ope == '修改':
        goods_num = data.get('goods_num')
        sql = "update goods_table set goods_name = '{0}',goods_description = '{1}',goods_price= {2},goods_picture= '{3}' where goods_num = '{4}'".format(
            name, description, price, picture, goods_num)
        # print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!sql:',sql)
        cursor.execute(sql)
        sql = "update inventory_table set inventory_amount = {0} where goods_num = '{1}' and shop_num = '{2}'".format(
            amount, goods_num, shop_num)
        cursor.execute(sql)


def shopper_find_money(id):
    # 查询用户余额
    sql = "select shopper_money from shopper_table where shopper_num='{0}'".format(id)
    cursor.execute(sql)
    rows = cursor.fetchall()
    print(sql, rows)
    if len(rows[0]) == 0:
        return 0
    money = rows[0][0]
    money = money.replace(",", '')
    if money[0] == '-':
        return '-' + money[2:]
    else:
        return money[1:]


def shopper_add_money(id, pwd, cMoney):
    # 用户充值
    sql = "UPDATE shopper_table set shopper_money = shopper_money + money({2}) " \
          "WHERE shopper_num = '{0}' AND shopper_password = '{1}';".format(id, pwd, cMoney)
    print(sql)
    cursor.execute(sql)


def shopper_sub_money(id, pwd, cMoney):
    # 用户提现
    sql = "UPDATE shopper_table set shopper_money = shopper_money - money({2}) " \
          "WHERE shopper_num = '{0}' AND shopper_password = '{1}';".format(id, pwd, cMoney)
    cursor.execute(sql)


def shop_find_money(id):
    # 查询商家余额
    sql = "select shop_money from shop_table where shop_num='{0}'".format(id)
    cursor.execute(sql)
    rows = cursor.fetchall()
    print(sql, rows)
    if len(rows[0]) == 0:
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
    sql = "UPDATE shop_table set shop_money = shop_money + money({2}) " \
          "WHERE shop_num = '{0}' AND shop_password = '{1}';".format(id, pwd, cMoney)
    print(sql)
    cursor.execute(sql)


def shop_sub_money(id, pwd, cMoney):
    # 商家提现
    sql = "UPDATE shop_table set shop_money = shop_money - money({2}) " \
          "WHERE shop_num = '{0}' AND shop_password = '{1}';".format(id, pwd, cMoney)
    cursor.execute(sql)


def shopper_change_info(id, rName, sPwd, rPwd):
    # 用户账号信息修改
    sql = "UPDATE shopper_table set shopper_name = '{0}',shopper_password = '{1}' " \
          "WHERE shopper_num = '{2}' AND shopper_password = '{3}';".format(rName, rPwd, id, sPwd)
    cursor.execute(sql)


def shop_change_info(id, rName, sPwd, rPwd, rDes):
    # 用户账号信息修改
    sql = "UPDATE shop_table set shop_name = '{0}',shop_password = '{1}',shop_description = '{4}' " \
          "WHERE shop_num = '{2}' AND shop_password = '{3}';".format(rName, rPwd, id, sPwd, rDes)
    cursor.execute(sql)


def shop_get_des(id):
    # 获取商家描述
    sql = "select shop_description from shop_table where shop_num = '{0}'".format(id)
    cursor.execute(sql)
    rows = cursor.fetchall()
    return rows[0][0]


def shopper_order_get(id):
    # 用户订单查询
    sql = "select * from shopper_order_view where shopper_num = '{0}'".format(id)
    cursor.execute(sql)
    rows = cursor.fetchall()
    order_list = []
    # print(rows)
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
    sql = "select * from shop_order_view where shop_num = '{0}'".format(id)
    cursor.execute(sql)
    rows = cursor.fetchall()
    order_list = []
    print(rows)
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
    print("comment")
    comment = data.get("commentInfo")
    goods_num = data.get("goods_num")
    order_num = data.get("order_num")
    sql = "insert into evaluation_table values('{0}','{1}',now()+'8:00','{2}')".format(order_num, goods_num, comment)
    # sql = "insert evaluation_table set evaluation_information = '{0}'," \
    #       "goods_num = '{1}', order_num = '{2}', evaluation_time = now() ".format(comment, goods_num, order_num)
    cursor.execute(sql)


def timestamp_to_time(timestamp):
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def shopper_receive(data):
    # 用户收货
    goods_num = data.get("goods_num")
    order_num = data.get("order_num")
    sql = "update content_table set content_status = '已收货' where order_num = '{0}' and goods_num = '{1}'".format(
        order_num, goods_num)
    cursor.execute(sql)
    sql = "select shop_num,content_number,goods_price from shop_order_view where order_num = '{0}' and goods_num = '{1}'"\
        .format(order_num, goods_num)
    cursor.execute(sql)
    rows = cursor.fetchall()
    if len(rows[0]) == 0:
        return
    money = to_money(rows[0][2]) * int(rows[0][1])
    print(money)
    sql = "update shop_table set shop_money = shop_money + money({0}) where shop_num = '{1}'".format(money, rows[0][0])
    cursor.execute(sql)


def shop_send_order(data):
    # 商家发货
    goods_num = data.get('goods_num')
    order_num = data.get('order_num')
    sql = "update content_table set content_status = '已发货' where goods_num = '{0}' and order_num = '{1}'".format(goods_num, order_num)
    cursor.execute(sql)

def shop_cancel_order(data):
    # todo 商家取消订单，买家的钱原数奉还
    goods_num = data.get('goods_num')
    order_num = data.get('order_num')
