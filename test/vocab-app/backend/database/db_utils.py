import pymysql

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='hily0403',  # 替换为你的 MySQL 密码
        database='elp',
        cursorclass=pymysql.cursors.DictCursor
    )