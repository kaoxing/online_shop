from django.test import TestCase
import random
# Create your tests here.
digits='0123456789'
ascii_letters='s'
str_list =[random.choice(digits + ascii_letters) for i in range(10)]
random_str ='qqq'.join(str_list)

goods_num = 'goods'+''.join([random.choice('0123456789') for i in range(5)])

print(goods_num)