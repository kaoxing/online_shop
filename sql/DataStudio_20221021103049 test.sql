INSERT INTO shopper_table VALUES('shopper123','脑瘫','123456',0);
INSERT INTO shopper_table VALUES('shopper456','智障','123456',250);

INSERT INTO shop_table VALUES('shop123456','是嘉心糖捏','123456','好想做嘉然小姐的狗啊',0);

INSERT into goods_table VALUES('goods12345','向哲的牛牛','描述',10,'图片');
INSERT into goods_table VALUES('goods12346','向哲的皮炎子','描述2',12,'图片2');

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
