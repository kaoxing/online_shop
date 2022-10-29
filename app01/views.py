import base64
import json
import sys
import os
import requests
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.contrib import messages
current_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_directory)

import coder
import my_tools as tls
import re

# D:\anaconda\envs\database\python.exe manage.py runserver
local = "http://127.0.0.1:8000/"


# Create your views here.

def home(request):
    return render(request, "Home.html")

def login(request):
    '''用户登录'''
    if request.method == 'GET':
        return render(request, "login.html")
    # 获取接收到的账号和密码
    data = request.POST
    id = data.get("user")
    pwd = data.get("pwd")
    name = tls.shopper_exist(id, pwd)
    if name is not None:
        pwd = coder.encode(pwd, id)
        return redirect(local + "index/" + "?id=" + id + "&name=" + name + "&pwd=" + pwd)
    messages.success(request, "账号或密码错误")
    return redirect(local + "login/")
    # TODO 这里加一个用户名/密码错误弹窗


def index(request):
    '''用户主页'''
    if request.method == 'GET':
        data = request.GET
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
    elif way == '查看评论':
        order_list = tls.index_goods_evaluation(data)
    else:
        order_list = tls.index_search(info, way)
    return JsonResponse({"data": order_list})


def wallet(request):
    '''用户钱包'''
    if request.method == 'GET':
        data = request.GET
        id = data.get('id')
        name = data.get('name')
        pwd = data.get('pwd')
        #此处查询用户余额
        money = "{0}".format(tls.shopper_find_money(id))

        return render(request, "wallet.html", {'name': name, 'id': id, 'pwd': pwd, 'money': money})
    data = json.loads(request.body)
    id = data.get("id")
    pwd = data.get("pwd")
    pwd = pwd.replace(" ", "+")
    name = data.get("name")
    cMoney = data.get("cMoney")
    m = data.get("m")
    #此处通过cMoney改余额,若m==“add"则充值，否则提现
    if m == "add":
        tls.shopper_add_money(id, coder.decode(pwd, id), cMoney)
    else:
        tls.shopper_sub_money(id, coder.decode(pwd, id), cMoney)
    url = local + "wallet/" + "?id=" + id + "&name=" + name + "&pwd=" + pwd
    return redirect(url)


def order(request):
    '''用户订单'''
    if request.method == 'GET':
        data = request.GET
        id = data.get('id')
        name = data.get('name')
        pwd = data.get('pwd')
        order_list = tls.shopper_order_get(id)
        return render(request, "order.html", {'name': name, 'id': id, 'pwd': pwd, 'List': json.dumps(order_list)})
    data = request.body
    data = json.loads(data)
    ope = data.get("ope")
    if ope == "评论":
        tls.shopper_comment(data)
    elif ope == "退货":
        tls.shopper_refund(data)
    elif ope == "收货":
        tls.shopper_receive(data)
    return render(request, "order.html")


def car(request):
    '''用户购物车'''
    if request.method == 'GET':
        data = request.GET
        id = data.get('id')
        name = data.get('name')
        pwd = data.get('pwd')
        cart_list = tls.cart_show(id)
        return render(request, "car.html", {'name': name, 'id': id, 'pwd': pwd, 'List': json.dumps(cart_list)})
    data = request.body
    data = json.loads(data)
    result = tls.cart_post(data)
    if result == "用户余额不足":
        return JsonResponse({"data": result, "res": "余额不足"})
    elif result[-4:] == "库存不足":
        return JsonResponse({"data": result, "res": "库存不足"})
    return render(request, "car.html")


def sorder(request):
    '''商家订单'''
    if request.method == 'GET':
        data = request.GET
        id = data.get('id')
        name = data.get('name')
        pwd = data.get('pwd')
        order_list = tls.shop_order_get(id)
        return render(request, "sorder.html", {'name': name, 'id': id, 'pwd': pwd, 'List': json.dumps(order_list)})
    data = request.body
    data = json.loads(data)
    ope = data.get("ope")
    # 通过ope的值确定操作类型,"发货","取消"
    if ope == "发货":
        tls.shop_send_order(data)
    elif ope == "取消":
        tls.shop_cancel_order(data)
    return render(request, "sorder.html")


def slogin(request):
    '''商家登录'''
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
    messages.success(request, "账号或密码错误")
    return redirect(local + "slogin/")
    # todo 这里加一个用户名/密码错误弹窗


def sindex(request):
    '''商家主页'''
    if request.method == 'GET':
        data = request.GET
        id = data.get('id')
        if id is None:
            return redirect(local + "slogin/")
        name = data.get('name')
        pwd = data.get('pwd')
        return render(request, "sindex.html", {'name': name, 'id': id, 'pwd': pwd})
    data = json.loads(request.body)
    info = data.get("info")
    way = data.get("way")
    if way == '查看评论':
        order_list = tls.index_goods_evaluation(data)
    else:
        order_list = tls.index_search(info, way)
    return JsonResponse({"data": order_list})


def swallet(request):
    '''商家钱包'''
    if request.method == 'GET':
        data = request.GET
        id = data.get('id')
        name = data.get('name')
        pwd = data.get('pwd')
        # 此处查询商家余额
        money = "{0}".format(tls.shop_find_money(id))
        return render(request, "swallet.html", {'name': name, 'id': id, 'pwd': pwd, 'money': money})
    data = json.loads(request.body)
    id = data.get("id")
    pwd = data.get("pwd")
    pwd = pwd.replace(" ", "+")
    name = data.get("name")
    cMoney = data.get("cMoney")
    m = data.get("m")
    # 此处通过cMoney改余额,若m==“add"则充值，否则提现
    if m == "add":
        tls.shop_add_money(id, coder.decode(pwd, id), cMoney)
    else:
        tls.shop_sub_money(id, coder.decode(pwd, id), cMoney)
    url = local + "swallet/" + "?id=" + id + "&name=" + name + "&pwd=" + pwd
    return redirect(url)


def setting(request):
    '''用户设置'''
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
    # todo 若修改成功
    rPwd = coder.encode(rPwd, id)
    url = local + "setting/" + "?id=" + id + "&name=" + rName + "&pwd=" + rPwd
    return redirect(url)


def ssetting(request):
    '''商家设置'''
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
    tls.shop_change_info(id, rName, sPwd, rPwd, rDes)
    rPwd = coder.encode(rPwd, id)
    url = local + "ssetting/" + "?id=" + id + "&name=" + rName + "&pwd=" + rPwd
    return redirect(url)


def mgood(request):
    '''商品管理'''
    # TODO 这里的 “查看商品评论”按钮不会触发
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
        way = data.get("way")
        if way == '查看评论':
            order_list = tls.index_goods_evaluation(data)
            return JsonResponse({"data": order_list})
        tls.mgood_post(data)

        return render(request, "mgood.html")


def test(request):
    if request.method == 'GET':
        return render(request, "mainpage.html")
    data = json.loads(request.body)
    user = data.get("user")
    pwd = data.get("pwd")
    # if tls.user_exist(user, pwd):
    #     return redirect("https://www.baidu.com/")
    return render(request, "mainpage.html")
