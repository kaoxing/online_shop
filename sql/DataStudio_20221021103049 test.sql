INSERT INTO inventory_table VALUES('shop123456','goods12345',200,0);
INSERT INTO inventory_table VALUES('shop123456','goods12346',198,20);

DELETE FROM cart_table;

DELETE FROM inventory_table;
DELETE FROM goods_table;
DELETE FROM shopper_table;
DELETE FROM shop_table;


select * from shop_table where shop_num='shop123456';

update goods_table set goods_name = '伊蕾娜3',goods_description = 'hhhhhhhgfg',goods_price= 5,goods_picture= '/static/img/image2.jpg' where goods_num = 'goods36891';

select * from cart_view where shopper_num = 'shopper456';

insert into order_table values('order12346',now(),'shopper456','地址');

INSERT INTO shopper_table VALUES('0X02014169','张昆明','123456',0);
INSERT INTO shopper_table VALUES('0X02014187','段昊良','123456',0);
INSERT INTO shopper_table VALUES('0X02014155','何济宇','123456',0);
INSERT INTO shopper_table VALUES('0X02014156','凌兴','123456',0);
INSERT INTO shopper_table VALUES('0X02014113','沈彤','123456',0);
INSERT INTO shopper_table VALUES('0X02014007','程文杰','123456',0);
INSERT INTO shopper_table VALUES('0X02014092','闵烁','123456',0);
INSERT INTO shopper_table VALUES('0E02014121','马正贤','123456',0);
INSERT INTO shopper_table VALUES('0C42014043','张中雨','123456',0);
INSERT INTO shopper_table VALUES('0C02014078','程嘉铭','123456',0);
INSERT INTO shopper_table VALUES('0B52014032','李兴宇','123456',0);
INSERT INTO shopper_table VALUES('0D02014090','李雨晴','123456',0);
INSERT INTO shopper_table VALUES('0D02014003','仝泽慧','123456',0);
INSERT INTO shopper_table VALUES('0D02014167','刘笑天','123456',0);
INSERT INTO shopper_table VALUES('0D02014065','张欣羽','123456',0);

INSERT INTO shop_table VALUES('1X02014169','张昆明','123456','该商家没有描述',1000);
INSERT INTO shop_table VALUES('1X02014187','段昊良','123456','该商家没有描述',1000);
INSERT INTO shop_table VALUES('1X02014155','何济宇','123456','该商家没有描述',1000);
INSERT INTO shop_table VALUES('1X02014156','凌兴','123456','该商家没有描述',1000);
INSERT INTO shop_table VALUES('1X02014113','沈彤','123456','该商家没有描述',1000);
INSERT INTO shop_table VALUES('1X02014007','程文杰','123456','该商家没有描述',1000);
INSERT INTO shop_table VALUES('1X02014092','闵烁','123456','该商家没有描述',1000);
INSERT INTO shop_table VALUES('1E02014121','马正贤','123456','该商家没有描述',1000);
INSERT INTO shop_table VALUES('1C42014043','张中雨','123456','该商家没有描述',1000);
INSERT INTO shop_table VALUES('1C02014078','程嘉铭','123456','该商家没有描述',1000);
INSERT INTO shop_table VALUES('1B52014032','李兴宇','123456','该商家没有描述',1000);
INSERT INTO shop_table VALUES('1D02014090','李雨晴','123456','该商家没有描述',1000);
INSERT INTO shop_table VALUES('1D02014003','仝泽慧','123456','该商家没有描述',1000);
INSERT INTO shop_table VALUES('1D02014167','刘笑天','123456','该商家没有描述',1000);
INSERT INTO shop_table VALUES('1D02014065','张欣羽','123456','该商家没有描述',1000);
