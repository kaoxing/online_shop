import base64
import os
import re
from pathlib import Path
from select import select
from django.db import connection

BASE_DIR = Path(__file__).resolve().parent.parent

cursor = connection.cursor()


def shopper_exist(id, pwd):
    # 用户登录
    sql = "select * from shopper_table where shopper_num=" + id
    cursor.execute(sql)
    rows = cursor.fetchall()
    print(id,pwd,rows)
    if len(rows) != 0 and rows[0][2] == pwd:
        return rows[0][1]
    return None


def shop_exist(id, pwd):
    # 商家登录
    sql = "select * from shop_table where shop_num=" + id
    cursor.execute(sql)
    rows = cursor.fetchall()
    if len(rows) != 0 and rows[0][2] == pwd:
        return rows[0][1]
    return None


# def


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
    print("rows:",rows)
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
    return list
        # dic['shop_name']=row[1]