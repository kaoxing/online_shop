-- 商家表
CREATE TABLE shop_table
(
shop_num CHAR(10) PRIMARY KEY,                   --商家账号
shop_name VARCHAR(20) NOT NULL,                  --商家名
shop_password VARCHAR(12) NOT NULL,              --商家密码
shop_description VARCHAR(100) NOT NULL,          --商家描述
shop_money MONEY NOT NULL,                       --商家余额
CONSTRAINT check_shop_num CHECK(length(shop_num)=10),
CONSTRAINT check_shop_password CHECK(length(shop_password)>=6)
);

-- 商品表
CREATE TABLE goods_table
(
goods_num CHAR(10) PRIMARY KEY,                 --商品号
goods_name VARCHAR(20) NOT NULL,                --商品名
goods_description VARCHAR(100) NOT NULL,        --商品描述
goods_price MONEY NOT NULL,                     --商品价格
goods_picture VARCHAR,                          --商品图片
CONSTRAINT check_goods_num CHECK(length(goods_num)=10)
);

-- 用户表
CREATE TABLE shopper_table(
shopper_num CHAR(10) PRIMARY KEY,               --用户账号
shopper_name VARCHAR(20) NOT NULL,              --用户名
shopper_password VARCHAR(12) NOT NULL,          --用户密码
shopper_money MONEY NOT NULL,                   --用户余额
CONSTRAINT check_shopper_num CHECK(length(shopper_num)=10),
CONSTRAINT check_shopper_password CHECK(length(shopper_password)>=6)
);

-- 订单表
CREATE TABLE order_table(
order_num CHAR(10) PRIMARY KEY,                 --订单号
order_time TIMESTAMP NOT NULL,                  --下单时间
shopper_num VARCHAR(10) NOT NULL,               --用户账号
order_address VARCHAR(100) NOT NULL,            --地址
FOREIGN KEY (shopper_num) REFERENCES shopper_table(shopper_num),
CONSTRAINT check_order_num CHECK(length(order_num)=10)
);

-- 库存表
CREATE TABLE inventory_table
(
shop_num CHAR(10),                              --商家账号
goods_num CHAR(10),                             --商品号
inventory_amount INT NOT NULL,                  --库存量
inventory_sold INT NOT NULL,                    --已售库存
PRIMARY KEY(shop_num,goods_num),
FOREIGN KEY(shop_num) REFERENCES shop_table(shop_num),
FOREIGN KEY(goods_num) REFERENCES goods_table(goods_num)
);

-- 包含表
CREATE TABLE content_table(
order_num CHAR(10),                             --订单号
goods_num CHAR(10),                             --商品号
content_number INT NOT NULL,                    --购买数量
content_status VARCHAR NOT NULL,                --购买状态
PRIMARY KEY(order_num,goods_num),
FOREIGN KEY(order_num) REFERENCES order_table(order_num),
FOREIGN KEY(goods_num) REFERENCES goods_table(goods_num)
);

-- 评价表
CREATE TABLE evaluation_table(
order_num CHAR(10),                             --订单号
goods_num CHAR(10),                             --商品号
evaluation_time TIMESTAMP,                      --评论时间
evalutaion_infomation VARCHAR(100) NOT NULL,    --评论信息
PRIMARY Key (order_num,goods_num,evaluation_time),
FOREIGN KEY (order_num,goods_num) REFERENCES content_table(order_num,goods_num)
);

--购物车表
CREATE TABLE cart_table(
shopper_num CHAR(10),                            --用户账号
goods_num CHAR(10),                              --商品号
cart_number INT,                                 --购买数量
PRIMARY KEY(shopper_num,goods_num),
FOREIGN KEY(shopper_num) REFERENCES shopper_table(shopper_num),
FOREIGN KEY(goods_num) REFERENCES goods_table(goods_num)
);

DROP TABLE cart_table;
DROP TABLE evaluation_table;
DROP TABLE content_table;
DROP TABLE inventory_table;
DROP TABLE order_table;
DROP TABLE shopper_table;
DROP TABLE goods_table;
DROP TABLE shop_table;
