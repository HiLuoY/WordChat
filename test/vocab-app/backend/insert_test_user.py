import pymysql
from werkzeug.security import generate_password_hash

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'test',  # 替换为你的 MySQL 密码
    'database': 'elp'
}

# 创建数据库连接
connection = pymysql.connect(**DB_CONFIG)

try:

    with connection.cursor() as cursor:
        # 哈希处理密码 - 使用与 Flask 完全相同的参数
        password = 'test123'
        # 使用与 Flask 默认相同的参数: method='pbkdf2:sha256', salt_length=8
        hashed_password = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=8
        )

        # 插入测试用户
        sql = "INSERT INTO Users (email, password_hash, nickname) VALUES (%s, %s, %s)"
        cursor.execute(sql, ('zyj@qq.com', hashed_password, 'TestUser'))
        connection.commit()
        print("测试用户插入成功")
finally:
    connection.close()