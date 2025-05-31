import pymysql
from pymysql.cursors import DictCursor
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'test',  # 替换为你的 MySQL 密码
    'database': 'elp',
    'cursorclass': DictCursor
}

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        logger.info("Database connection established")
        return connection
    except pymysql.MySQLError as e:
        logger.error("Failed to connect to the database: %s", str(e), exc_info=True)
        raise

def query(sql, params=None):
    """执行查询操作"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            result = cursor.fetchall()
            logger.info("Query executed successfully: %s", sql)
            return result
    except pymysql.MySQLError as e:
        logger.error("Failed to execute query: %s\nError: %s", sql, str(e), exc_info=True)
        raise
    finally:
        connection.close()
        logger.info("Database connection closed")

def insert(sql, params=None):
    """执行插入操作"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            connection.commit()
            lastrowid = cursor.lastrowid
            logger.info("Insert executed successfully: %s", sql)
            return lastrowid  # 返回新插入的ID
    except pymysql.MySQLError as e:
        connection.rollback()
        logger.error("Failed to execute insert: %s\nError: %s", sql, str(e), exc_info=True)
        raise
    finally:
        connection.close()
        logger.info("Database connection closed")

def update(sql, params=None):
    """执行更新操作"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            connection.commit()
            success = cursor.rowcount > 0
            logger.info("Update executed successfully: %s", sql)
            return success  # 返回是否更新成功
    except pymysql.MySQLError as e:
        connection.rollback()
        logger.error("Failed to execute update: %s\nError: %s", sql, str(e), exc_info=True)
        raise
    finally:
        connection.close()
        logger.info("Database connection closed")

def delete(sql, params=None):
    """执行删除操作"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            connection.commit()
            success = cursor.rowcount > 0
            logger.info("Delete executed successfully: %s", sql)
            return success  # 返回是否删除成功
    except pymysql.MySQLError as e:
        connection.rollback()
        logger.error("Failed to execute delete: %s\nError: %s", sql, str(e), exc_info=True)
        raise
    finally:
        connection.close()
        logger.info("Database connection closed")


"""
查询房间
mysql -u root -p
SHOW DATABASES;
USE elp;
SELECT * FROM room;

"""