import pymysql
from pymysql.cursors import DictCursor
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'test',
    'database': 'elp',
    'cursorclass': DictCursor,
    'autocommit': True
}

def test_database_connection():
    """测试数据库连接和基本操作"""
    connection = None
    cursor = None
    
    try:
        # 建立数据库连接
        connection = pymysql.connect(**DB_CONFIG)
        logger.info("✅ 数据库连接成功！")
        
        # 创建游标
        cursor = connection.cursor()
        
        # 测试简单查询
        cursor.execute("SELECT 1 + 1 AS result")
        result = cursor.fetchone()
        logger.info(f"测试查询结果: {result['result']}")  # 应该输出2
        
        # 检查数据库是否存在
        cursor.execute("SHOW DATABASES LIKE 'elp'")
        if not cursor.fetchone():
            logger.warning("⚠️ 数据库 'elp' 不存在！")
        else:
            logger.info("✅ 数据库 'elp' 存在")
            
        # 检查表是否存在
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        logger.info(f"数据库包含的表: {[table['Tables_in_elp'] for table in tables]}")
            
        return True
        
    except pymysql.MySQLError as e:
        logger.error(f"❌ 数据库操作失败: {e}")
        return False
        
    finally:
        # 资源清理（PyMySQL游标没有closed属性）
        try:
            if cursor:
                cursor.close()
                logger.debug("游标已关闭")
        except Exception as e:
            logger.warning(f"关闭游标时出错: {e}")
            
        try:
            if connection and connection.open:
                connection.close()
                logger.debug("数据库连接已关闭")
        except Exception as e:
            logger.warning(f"关闭连接时出错: {e}")

if __name__ == "__main__":
    test_database_connection()