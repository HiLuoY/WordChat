from database.db_utils import insert, query, update, delete
from datetime import datetime
import logging
from typing import Optional, Dict, List

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User:
    @staticmethod
    def create_user(email: str, password_hash: str, nickname: str, avatar: Optional[str] = None) -> int:
        """
        创建新用户
        :param email: 用户邮箱(唯一)
        :param password_hash: 密码哈希值
        :param nickname: 用户昵称
        :param avatar: 用户头像URL(可选)
        :return: 新创建的用户ID
        :raises: ValueError 如果邮箱已存在
        """
        # 检查邮箱是否已存在
        if User.get_user_by_email(email) is not None:
            raise ValueError(f"Email {email} already exists")
        
        sql = """
        INSERT INTO Users (email, password_hash, nickname, avatar, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (email, password_hash, nickname, avatar, datetime.utcnow(), datetime.utcnow())
        
        try:
            user_id = insert(sql, params)
            logger.info(f"User created successfully: id={user_id}, email={email}")
            return user_id
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict]:
        """
        根据ID获取用户信息
        :param user_id: 用户ID
        :return: 用户信息字典或None(如果用户不存在)
        """
        sql = """
        SELECT id, email, nickname, avatar, created_at, updated_at 
        FROM Users 
        WHERE id = %s
        """
        params = (user_id,)
        
        try:
            result = query(sql, params)
            logger.info(f"Fetched user by id={user_id}")
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to fetch user by id={user_id}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict]:
        """
        根据邮箱获取用户信息
        :param email: 用户邮箱
        :return: 用户信息字典或None(如果用户不存在)
        """
        sql = """
        SELECT id, password_hash, email, nickname, avatar, created_at, updated_at 
        FROM Users 
        WHERE email = %s
        """
        params = (email,)
        
        try:
            result = query(sql, params)
            logger.info(f"Fetched user by email={email}")
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to fetch user by email={email}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def update_user(user_id: int, updates: Dict) -> bool:
        """
        更新用户信息
        :param user_id: 要更新的用户ID
        :param updates: 包含更新字段的字典(可包含: nickname, avatar, password_hash)
        :return: 是否更新成功
        :raises: ValueError 如果用户不存在或更新字段无效
        """
        if not updates:
            raise ValueError("No update fields provided")
        
        valid_fields = {'nickname', 'avatar', 'password_hash'}
        invalid_fields = set(updates.keys()) - valid_fields
        if invalid_fields:
            raise ValueError(f"Invalid update fields: {invalid_fields}")
        
        # 检查用户是否存在
        if User.get_user_by_id(user_id) is None:
            raise ValueError(f"User with id={user_id} does not exist")
        
        set_clause = ", ".join([f"{field} = %s" for field in updates.keys()])
        sql = f"""
        UPDATE Users 
        SET {set_clause}, updated_at = %s
        WHERE id = %s
        """
        params = (*updates.values(), datetime.utcnow(), user_id)
        
        try:
            success = update(sql, params)
            logger.info(f"Updated user id={user_id} with fields: {updates.keys()}")
            return success
        except Exception as e:
            logger.error(f"Failed to update user id={user_id}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def delete_user(user_id: int) -> bool:
        """
        删除用户
        :param user_id: 要删除的用户ID
        :return: 是否删除成功
        :raises: ValueError 如果用户不存在
        """
        # 检查用户是否存在
        if User.get_user_by_id(user_id) is None:
            raise ValueError(f"User with id={user_id} does not exist")
        
        sql = """
        DELETE FROM Users 
        WHERE id = %s
        """
        params = (user_id,)
        
        try:
            success = delete(sql, params)
            logger.info(f"Deleted user id={user_id}")
            return success
        except Exception as e:
            logger.error(f"Failed to delete user id={user_id}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def list_users(page: int = 1, per_page: int = 10) -> List[Dict]:
        """
        分页获取用户列表
        :param page: 页码(从1开始)
        :param per_page: 每页记录数
        :return: 用户列表
        """
        offset = (page - 1) * per_page
        sql = """
        SELECT id, email, nickname, avatar, created_at, updated_at 
        FROM Users 
        ORDER BY created_at DESC 
        LIMIT %s OFFSET %s
        """
        params = (per_page, offset)
        
        try:
            result = query(sql, params)
            logger.info(f"Fetched user list: page={page}, per_page={per_page}")
            return result
        except Exception as e:
            logger.error(f"Failed to fetch user list: {str(e)}", exc_info=True)
            raise
