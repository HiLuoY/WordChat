from database.db_utils import insert, query, update, delete
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Message:
    @staticmethod
    def send_message(room_id, user_id, message, message_type='normal'):
        """发送消息"""
        # 验证 message_type 是否合法
        if message_type not in ['normal', 'urgent', 'system']:
            raise ValueError(f"Invalid message_type: {message_type}. Allowed values: 'normal', 'urgent', 'system'")
        
        sql = """
        INSERT INTO Messages (room_id, user_id, message, message_type, timestamp)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (room_id, user_id, message, message_type, datetime.utcnow())
        try:
            lastrowid = insert(sql, params)
            logger.info("Message sent successfully: room_id=%s, user_id=%s", room_id, user_id)
            return lastrowid  # 返回新插入的消息ID
        except Exception as e:
            logger.error("Failed to send message: %s", str(e), exc_info=True)
            raise  # 将异常抛给调用方

    @staticmethod
    def get_messages_by_room(room_id):
        """根据房间ID获取消息列表"""
        sql = """
        SELECT * FROM Messages
        WHERE room_id = %s
        ORDER BY timestamp ASC
        """
        params = (room_id,)
        try:
            result = query(sql, params)
            logger.info("Fetched messages for room_id=%s", room_id)
            return result
        except Exception as e:
            logger.error("Failed to fetch messages by room_id=%s: %s", room_id, str(e), exc_info=True)
            raise  # 将异常抛给调用方

    @staticmethod
    def get_messages_by_user(user_id):
        """根据用户ID获取消息列表"""
        sql = """
        SELECT * FROM Messages
        WHERE user_id = %s
        ORDER BY timestamp ASC
        """
        params = (user_id,)
        try:
            result = query(sql, params)
            logger.info("Fetched messages for user_id=%s", user_id)
            return result
        except Exception as e:
            logger.error("Failed to fetch messages by user_id=%s: %s", user_id, str(e), exc_info=True)
            raise  # 将异常抛给调用方

    @staticmethod
    def get_message_by_id(message_id):
        """根据消息ID获取单条消息"""
        sql = """
        SELECT * FROM Messages
        WHERE id = %s
        """
        params = (message_id,)
        try:
            result = query(sql, params)
            logger.info("Fetched message for message_id=%s", message_id)
            return result[0] if result else None
        except Exception as e:
            logger.error("Failed to fetch message by message_id=%s: %s", message_id, str(e), exc_info=True)
            raise  # 将异常抛给调用方

    @staticmethod
    def update_message_type(message_id, new_message_type):
        """更新消息类型"""
        # 验证 new_message_type 是否合法
        if new_message_type not in ['normal', 'urgent', 'system']:
            raise ValueError(f"Invalid new_message_type: {new_message_type}. Allowed values: 'normal', 'urgent', 'system'")
        
        sql = """
        UPDATE Messages
        SET message_type = %s
        WHERE id = %s
        """
        params = (new_message_type, message_id)
        try:
            success = update(sql, params)
            logger.info("Updated message_type for message_id=%s to %s", message_id, new_message_type)
            return success  # 返回是否更新成功
        except Exception as e:
            logger.error("Failed to update message_type for message_id=%s: %s", message_id, str(e), exc_info=True)
            raise  # 将异常抛给调用方

    @staticmethod
    def delete_message(message_id):
        """删除消息"""
        sql = """
        DELETE FROM Messages
        WHERE id = %s
        """
        params = (message_id,)
        try:
            success = delete(sql, params)
            logger.info("Deleted message for message_id=%s", message_id)
            return success  # 返回是否删除成功
        except Exception as e:
            logger.error("Failed to delete message for message_id=%s: %s", message_id, str(e), exc_info=True)
            raise  # 将异常抛给调用方