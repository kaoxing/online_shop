import base64
import os
from pydoc import describe
import random

import re
from pathlib import Path
from select import select
from django.db import connection

BASE_DIR = Path(__file__).resolve().parent.parent

cursor = connection.cursor()


def shopper_exist(id, pwd):
    # 用户登录
    sql = "select * from shopper_table where shopper_num='{}'".format(id)
    cursor.execute(sql)
    rows = cursor.fetchall()
    print(id,pwd,rows)
    if len(rows) != 0 and rows[0][2] == pwd:
        return rows[0][1]
    return None


def shop_exist(id, pwd):
    # 商家登录
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
    filename = os.path.join(BASE_DIR, 'app01/static/img/')
    filename = filename + 'image.jpg'  # I assume you have a way of picking unique filenames
    print(filename)
    with open(filename, 'wb') as f:
        f.write(photo)
    return filename


def index_search_goods(info):
    sql = "select * from goods_view where goods_name like '%{0}%'".format(info)
    cursor.execute(sql)
    rows = cursor.fetchall()
    # print("rows:",rows)
    list = []
    for row in rows:
        dic = {
        "shop_name": row[5],
        "shop_num": "",
        "goods_num": row[0],
        "goods_name": row[1],
        "inventory_number": row[6],
        "goods_price": row[3],
        'goods_description': row[2],
        'shopper_description': '',#商家描述
        'goods_photo': row[4]
        }
        print("dic",dic)
        list.append(dic)
        print(1)
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
        "goods_number": row[6],
        "goods_price": row[4],
        'goods_description': row[3],
        # 'order_address': '123',
        # 'statu': '',
        'goods_photo': row[5]
        }
        # print("dic",dic)
        list.append(dic)
    return list


def mgood_post(data):
    # print("!!!!!!!!!!!!!!!!!!!!!",data.get("id"))
    # print("!!!!!!!!!!!!!!!!!!!!!",data.keys())
    name = data.get("goods_name")
    description = data.get("goods_description")
    price = data.get("goods_price")
    picture = ""
    amount = data.get("goods_number")
    goods_num = ""
    shop_num = data.get("id")
    ope=''
    # ope='上架'
    if ope == '上架':
        goods_num = 'goods'+''.join([random.choice('0123456789') for i in range(5)]) #随机生成商品号 
        sql = "insert into goods_table values ('{0}','{1}','{2}',{3},'{4}')".format(goods_num,name,description,price,picture)
        cursor.execute(sql)
        sql = "insert into inventory_table values('{0}','{1}',{2},{3})".format(shop_num,goods_num,amount,0)
        cursor.execute(sql)
    elif ope == '修改':
        sql = "updata goods_table set goods_name = '{0}',goods_description = '{1}',goods_price= '{2}',goods_picture= '{3}' where goods_num = '{4}'".format(name,description,price,picture,goods_num)
        cursor.execute(sql)
        sql = "updata inventory_table set inventory_amount = {0} where goods_num = '{1}' and shop_num = '{2}'".format(amount,goods_num,shop_num)
        cursor.execute(sql)