import base64
import json
import sys
import os
import requests
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse

current_directory = os.path.dirname(os.path.abspath(__file__))
# print(current_directory)
sys.path.append(current_directory)

import coder
import my_tools as tls
import re

# D:\anaconda\envs\database\python.exe manage.py runserver
local = "http://127.0.0.1:8000/"


# Create your views here.
def login(request):
    # 用户登录
    if request.method == 'GET':
        return render(request, "login.html")
    # 获取接收到的账号和密码

    data = request.POST
    id = data.get("user")
    pwd = data.get("pwd")
    name = tls.shopper_exist(id, pwd)
    if name is not None:
        pwd = coder.encode(pwd, id)
        print(pwd)
        return redirect(local + "index/" + "?id=" + id + "&name=" + name + "&pwd=" + pwd)
    return render(request, "login.html")
    # todo 这里加一个用户名/密码错误弹窗


def index(request):
    '''用户主页'''
    if request.method == 'GET':
        data = request.GET
        print(data)
        id = data.get('id')
        if id is None:
            return redirect(local + "login/")
        name = data.get('name')
        pwd = data.get('pwd')
        return render(request, "index.html", {'name': name, 'id': id, 'pwd': pwd})
    data = json.loads(request.body)
    info = data.get("info")
    way = data.get("way")
    id = data.get("id")
    goods_num = data.get("goods_num")
    order_list = []
    if way == '加购物车':
        tls.add_cart(id, goods_num)
    else:
        order_list = tls.index_search(info, way)
    return JsonResponse({"data": order_list})




def wallet(request):
    if request.method == 'GET':
        data = request.GET
        id = data.get('id')
        name = data.get('name')
        pwd = data.get('pwd')
        # todo 此处查询用户余额
        money = "{0}".format(tls.shopper_find_money(id))
        print(money, tls.shopper_find_money(id))

        return render(request, "wallet.html", {'name': name, 'id': id, 'pwd': pwd, 'money': money})
    data = json.loads(request.body)
    id = data.get("id")
    pwd = data.get("pwd")
    pwd = pwd.replace(" ", "+")
    name = data.get("name")
    cMoney = data.get("cMoney")
    print("pwd", pwd)
    m = data.get("m")
    print("here")
    # todo 此处通过cMoney改余额,若m==“add"则充值，否则提现
    if m == "add":
        tls.shopper_add_money(id, coder.decode(pwd, id), cMoney)
    else:
        tls.shopper_sub_money(id, coder.decode(pwd, id), cMoney)
    url = local + "wallet/" + "?id=" + id + "&name=" + name + "&pwd=" + pwd
    return redirect(url)


def order(request):
    if request.method == 'GET':
        data = request.GET
        id = data.get('id')
        name = data.get('name')
        pwd = data.get('pwd')
        # print("herep")
        # todo 这里通过用户id找到用户订单
        order_list = tls.shopper_order_get(id)

        return render(request, "order.html", {'name': name, 'id': id, 'pwd': pwd, 'List': json.dumps(order_list)})
    data = request.body
    data = json.loads(data)
    ope = data.get("ope")
    print(data)
    print(ope)
    print(ope == "评论")
    # todo 通过ope的值确定操作类型,"评论","退货","收货"
    if ope == "评论":
        tls.shopper_comment(data)
    elif ope == "退货":
        tls.shopper_refund(data)
    elif ope == "收货":
        tls.shopper_receive(data)
    # todo 通过上述参数在数据库中修改
    return render(request, "order.html")


def car(request):
    print()
    if request.method == 'GET':
        data = request.GET
        id = data.get('id')
        name = data.get('name')
        pwd = data.get('pwd')
        cart_list = tls.cart_show(id)
        return render(request, "car.html", {'name': name, 'id': id, 'pwd': pwd, 'List': json.dumps(cart_list)})
    data = request.body
    data = json.loads(data)
    tls.cart_post(data)
    print()
    return render(request, "car.html")


def sorder(request):
    if request.method == 'GET':
        data = request.GET
        id = data.get('id')
        name = data.get('name')
        pwd = data.get('pwd')
        # print("herep")
        # todo 这里通过商家id找到商家订单
        order_list = [{
            "order_date": '2016-05-02',
            "order_num": 'x12345',
            "goods_num": 'x2s',
            "goods_name": '钩子',
            "goods_number": '100',
            "goods_price": '20',
            'user_address': '上海市普陀区金沙江路 1518 弄',
            'statu': '待发货',
        }, {
            "order_date": '2016-05-02',
            "order_num": 'x12345',
            "goods_num": 'x2s',
            "goods_name": '钩子',
            "goods_number": '100',
            "goods_price": '20',
            'user_address': '上海市普陀区金沙江路 1518 弄',
            'statu': '待发货',
        }]
        return render(request, "sorder.html", {'name': name, 'id': id, 'pwd': pwd, 'List': json.dumps(order_list)})
    data = request.body
    data = json.loads(data)
    ope = data.get("ope")
    # todo 通过ope的值确定操作类型,"发货","取消"
    goods_num = data.get('goods_num')
    order_num = data.get('order_num')
    order_statu = data.get('statu')
    print(goods_num, order_num, order_statu, ope)
    # todo 通过上述参数在数据库中修改
    return render(request, "sorder.html")


def slogin(request):
    if request.method == 'GET':
        return render(request, "slogin.html")
    # 获取接收到的账号和密码
    data = request.POST
    id = data.get("user")
    pwd = data.get("pwd")
    name = tls.shop_exist(id, pwd)
    if name is not None:
        pwd = coder.encode(pwd, id)
        return redirect(local + "sindex/" + "?id=" + id + "&name=" + name + "&pwd=" + pwd)
    return render(request, "slogin.html")
    # todo 这里加一个用户名/密码错误弹窗


def sindex(request):
    '''商家主页'''
    if request.method == 'GET':
        data = request.GET
        print(data)
        id = data.get('id')
        if id is None:
            return redirect(local + "slogin/")
        name = data.get('name')
        pwd = data.get('pwd')
        return render(request, "sindex.html", {'name': name, 'id': id, 'pwd': pwd})
    data = json.loads(request.body)
    # todo 判断是去个人中心还是搜索
    info = data.get("info")
    way = data.get("way")
    order_list = tls.index_search(info, way)
    return JsonResponse({"data": order_list})


def swallet(request):
    if request.method == 'GET':
        data = request.GET
        id = data.get('id')
        name = data.get('name')
        pwd = data.get('pwd')
        # todo 此处查询商家余额
        money = "{0}".format(tls.shop_find_money(id))
        # print(money, tls.shopper_find_money(id))
        return render(request, "swallet.html", {'name': name, 'id': id, 'pwd': pwd, 'money': money})
    data = json.loads(request.body)
    id = data.get("id")
    pwd = data.get("pwd")
    pwd = pwd.replace(" ", "+")
    name = data.get("name")
    cMoney = data.get("cMoney")
    # print("pwd", pwd)
    m = data.get("m")
    # print("here")
    # todo 此处通过cMoney改余额,若m==“add"则充值，否则提现
    if m == "add":
        tls.shop_add_money(id, coder.decode(pwd, id), cMoney)
    else:
        tls.shop_sub_money(id, coder.decode(pwd, id), cMoney)
    url = local + "swallet/" + "?id=" + id + "&name=" + name + "&pwd=" + pwd
    return redirect(url)


def setting(request):
    if request.method == 'GET':
        data = request.GET
        id = data.get('id')
        name = data.get('name')
        pwd = data.get('pwd')
        # todo 这里要先确定数据库雀食有这个商家
        return render(request, "setting.html", {'name': name, 'id': id, 'pwd': pwd})
    # 接收到修改请求
    data = json.loads(request.body)
    id = data.get('id')
    rName = data.get('resultName')
    sPwd = data.get('sourcePwd')
    rPwd = data.get('resultPwd')
    tls.shopper_change_info(id, rName, sPwd, rPwd)
    # todo 在数据库中查询并修改
    print(data)
    # todo 若修改成功
    rPwd = coder.encode(rPwd, id)
    url = local + "setting/" + "?id=" + id + "&name=" + rName + "&pwd=" + rPwd
    return redirect(url)


def ssetting(request):
    if request.method == 'GET':
        data = request.GET
        id = data.get('id')
        name = data.get('name')
        pwd = data.get('pwd')
        # todo 这里要先确定数据库雀食有这个商家并获取商家描述
        description = tls.shop_get_des(id)
        return render(request, "ssetting.html", {'name': name, 'id': id, 'pwd': pwd, 'description': description})
    # 接收到修改请求
    data = json.loads(request.body)
    id = data.get('id')
    rName = data.get('resultName')
    sPwd = data.get('sourcePwd')
    rPwd = data.get('resultPwd')
    rDes = data.get('description')
    # todo 在数据库中查询并修改
    # print(data)
    tls.shop_change_info(id, rName, sPwd, rPwd, rDes)
    # todo 若修改成功

    rPwd = coder.encode(rPwd, id)
    url = local + "ssetting/" + "?id=" + id + "&name=" + rName + "&pwd=" + rPwd
    return redirect(url)


def mgood(request):
    print(request.method)
    if request.method == 'GET':
        data = request.GET
        id = data.get('id')
        if id is None:
            return redirect(local + "slogin/")
        name = data.get('name')
        pwd = data.get('pwd')
        goods_list = tls.mgood_get(id)
        return render(request, "mgood.html", {'name': name, 'id': id, 'pwd': pwd, 'List': json.dumps(goods_list)})
    elif request.method == 'POST':
        data = request.body
        data = json.loads(data)
        tls.mgood_post(data)

        # print(data.keys())
        # photo = data.get("goods_photo")
        # ope = data.get()
        # tls.save_photo(photo)

        # ope = data.get("ope")
        # # todo 通过ope的值确定操作类型,"地址","数量","购买"，“删除”
        # # 注意，在地址操作时，数量为空，数量操作时，地址为空，购买时，都不为空
        # shopper_num = data.get('id')
        # goods_num = data.get('goods_num')
        # goods_number = data.get('goods_number')
        # order_address = data.get('order_address')
        # print(shopper_num, goods_num, goods_number, order_address, ope)
        # todo 通过上述参数在数据库中修改
        return render(request, "mgood.html")


def test(request):
    if request.method == 'GET':
        return render(request, "mainpage.html")
    data = json.loads(request.body)
    print(data)
    user = data.get("user")
    pwd = data.get("pwd")
    # print("here")
    # if tls.user_exist(user, pwd):
    #     return redirect("https://www.baidu.com/")
    return render(request, "mainpage.html")
