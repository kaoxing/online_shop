CREATE VIEW evaluation_view AS
SELECT shopper_table.shopper_name, evaluation_table.*
  FROM shopper_table, evaluation_table, order_table
 WHERE shopper_table.shopper_num = order_table.shopper_num
   AND evaluation_table.order_num = order_table.order_num;
   
CREATE VIEW goods_view AS
SELECT goods_table.*, shop_table.shop_name,shop_table.shop_num,shop_table.shop_description, inventory_table.inventory_amount,inventory_table.inventory_sold
  FROM goods_table, shop_table, inventory_table
 WHERE goods_table.goods_num = inventory_table.goods_num
   AND shop_table.shop_num = inventory_table.shop_num;
   
CREATE VIEW shopper_order_view (shopper_num,order_num,content_number,goods_name,shop_name,shop_num,goods_num,order_time,goods_photo) AS
SELECT shopper_table.shopper_num, order_table.order_num, content_table.content_number, goods_table.goods_name, shop_table.shop_name, shop_table.shop_num, goods_table.goods_num, order_table.order_time, goods_picture
  FROM shopper_table, order_table, content_table, inventory_table, shop_table, goods_table
 WHERE shopper_table.shopper_num = order_table.shopper_num
   AND order_table.order_num = content_table.order_num
   AND content_table.goods_num = inventory_table.goods_num
   AND content_table.goods_num = goods_table.goods_num
   AND inventory_table.shop_num = shop_table.shop_num;

CREATE VIEW shop_order_view (shop_num,order_num,content_number,goods_name,shoppper_name,shoppper_num,goods_num,order_time,goods_photo,user_address,status,goods_price) AS
SELECT shop_table.shop_num, order_table.order_num, content_table.content_number, goods_table.goods_name,
shopper_table.shopper_name, shopper_table.shopper_num, goods_table.goods_num, order_table.order_time, goods_picture,
order_table.order_address,content_status,goods_price
  FROM shopper_table, order_table, content_table, inventory_table, shop_table, goods_table
 WHERE shopper_table.shopper_num = order_table.shopper_num
   AND order_table.order_num = content_table.order_num
   AND content_table.goods_num = inventory_table.goods_num
   AND content_table.goods_num = goods_table.goods_num
   AND inventory_table.shop_num = shop_table.shop_num;

--CREATE VIEW shop_order_view (order_num,order_address,shopper_num,goods_num,content_number,shop_num,goods_name,shopper_name) AS
--SELECT order_table.order_num, order_table.order_address, order_table.shopper_num, content_table.goods_num, content_table.content_number, inventory_table.shop_num, goods_table.goods_name, shopper_table.shopper_name
--  FROM order_table, content_table, inventory_table, goods_table, shopper_table
-- WHERE order_table.order_num = content_table.order_num
--   AND content_table.goods_num = inventory_table.goods_num
--   AND content_table.goods_num = goods_table.goods_num
--   AND order_table.shopper_num = shopper_table.shopper_num;
   
CREATE VIEW shop_goods_view AS
SELECT shop_table.shop_num,goods_table.*,inventory_table.inventory_amount,inventory_table.inventory_sold
FROM goods_table,inventory_table,shop_table
WHERE goods_table.goods_num = inventory_table.goods_num
AND shop_table.shop_num = inventory_table.shop_num;

CREATE VIEW cart_view AS
SELECT goods_view.*, cart_table.shopper_num, cart_table.cart_number
  FROM goods_view, cart_table
 WHERE goods_view.goods_num = cart_table.goods_num;
 
 
DROP VIEW evaluation_view;
DROP VIEW goods_view;
DROP VIEW shopper_order_view;
DROP VIEW shop_order_view;
DROP VIEW shop_goods_view;
