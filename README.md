# online_shop

## hello,database

## 系统启动说明
1. 安装系统所需的python第三方库；
2. 在``` ./online_shop/settings.py```文件下找到DATABASES字典，设置数据库连接的参数；

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',  # 数据库名
        'USER': '',  # 用户名
        'PASSWORD': '',  # 密码
        'HOST': '',  # ip
        'PORT': 26000  # openGauss数据口的端口
    }
}
```
3. 在项目目录下运行下面的命令：
```python manage.py runserver```