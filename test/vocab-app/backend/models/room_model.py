from database.db_utils import insert, query, update, delete
from datetime import datetime
import logging
from typing import Optional, Dict, List, Union

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Room:
    @staticmethod
    def create_room(room_name: str, owner_id: int, password: Optional[str] = None) -> int:
        """
        创建新房间
        :param room_name: 房间名称(唯一)
        :param owner_id: 房主用户ID
        :param password: 房间密码(可选)
        :return: 新创建的房间ID
        :raises: ValueError 如果房间名已存在或owner_id无效
        """
        # 检查房间名是否已存在
        if Room.get_room_by_name(room_name) is not None:
            raise ValueError(f"Room name {room_name} already exists")
        
        sql = """
        INSERT INTO Rooms (room_name, password, owner_id, created_at)
        VALUES (%s, %s, %s, %s)
        """
        params = (room_name, password, owner_id, datetime.utcnow())
        
        try:
            room_id = insert(sql, params)
            logger.info(f"Room created successfully: id={room_id}, name={room_name}")
            return room_id
        except Exception as e:
            logger.error(f"Failed to create room: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_room_by_id(room_id: int) -> Optional[Dict]:
        """
        根据ID获取房间信息
        :param room_id: 房间ID
        :return: 房间信息字典或None(如果房间不存在)
        """
        sql = """
        SELECT id, password, room_name, password, owner_id, created_at 
        FROM Rooms 
        WHERE id = %s
        """
        params = (room_id,)
        
        try:
            result = query(sql, params)
            if not result:
                logger.warning(f"Room not found: id={room_id}")
                return None
                
            room = result[0]
            logger.info(f"Fetched room by id={room_id}: {room}")
            return room
        except Exception as e:
            logger.error(f"Failed to fetch room by id={room_id}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_room_by_name(room_name: str) -> Optional[Dict]:
        """
        根据房间名称获取房间信息
        :param room_name: 房间名称
        :return: 房间信息字典或None(如果房间不存在)
        """
        sql = """
        SELECT id, room_name, owner_id, created_at 
        FROM Rooms 
        WHERE room_name = %s
        """
        params = (room_name,)
        
        try:
            result = query(sql, params)
            logger.info(f"Fetched room by name={room_name}")
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to fetch room by name={room_name}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def update_room(room_id: int, updates: Dict) -> bool:
        """
        更新房间信息
        :param room_id: 要更新的房间ID
        :param updates: 包含更新字段的字典(可包含: room_name, password)
        :return: 是否更新成功
        :raises: ValueError 如果房间不存在或更新字段无效
        """
        if not updates:
            raise ValueError("No update fields provided")
        
        valid_fields = {'room_name', 'password'}
        invalid_fields = set(updates.keys()) - valid_fields
        if invalid_fields:
            raise ValueError(f"Invalid update fields: {invalid_fields}")
        
        # 检查房间是否存在
        if Room.get_room_by_id(room_id) is None:
            raise ValueError(f"Room with id={room_id} does not exist")
        
        # 如果更新房间名，检查新名称是否已存在
        if 'room_name' in updates:
            existing_room = Room.get_room_by_name(updates['room_name'])
            if existing_room and existing_room['id'] != room_id:
                raise ValueError(f"Room name {updates['room_name']} already exists")
        
        set_clause = ", ".join([f"{field} = %s" for field in updates.keys()])
        sql = f"""
        UPDATE Rooms 
        SET {set_clause}
        WHERE id = %s
        """
        params = (*updates.values(), room_id)
        
        try:
            success = update(sql, params)
            logger.info(f"Updated room id={room_id} with fields: {updates.keys()}")
            return success
        except Exception as e:
            logger.error(f"Failed to update room id={room_id}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def delete_room(room_id: int) -> bool:
        """
        删除房间
        :param room_id: 要删除的房间ID
        :return: 是否删除成功
        :raises: ValueError 如果房间不存在
        """
        # 检查房间是否存在
        if Room.get_room_by_id(room_id) is None:
            raise ValueError(f"Room with id={room_id} does not exist")
        
        sql = """
        DELETE FROM Rooms 
        WHERE id = %s
        """
        params = (room_id,)
        
        try:
            success = delete(sql, params)
            logger.info(f"Deleted room id={room_id}")
            return success
        except Exception as e:
            logger.error(f"Failed to delete room id={room_id}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def list_rooms(page: int = 1, per_page: int = 10) -> List[Dict]:
        """
        分页获取房间列表
        :param page: 页码(从1开始)
        :param per_page: 每页记录数
        :return: 房间列表
        """
        offset = (page - 1) * per_page
        sql = """
        SELECT id, password, room_name, owner_id, created_at 
        FROM Rooms 
        ORDER BY created_at DESC 
        LIMIT %s OFFSET %s
        """
        params = (per_page, offset)
        
        try:
            result = query(sql, params)
            logger.info(f"Fetched room list: page={page}, per_page={per_page}")
            return result
        except Exception as e:
            logger.error(f"Failed to fetch room list: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_rooms_by_owner(owner_id: int) -> List[Dict]:
        """
        根据房主ID获取房间列表
        :param owner_id: 房主用户ID
        :return: 房间列表
        """
        sql = """
        SELECT id, room_name, owner_id, created_at 
        FROM Rooms 
        WHERE owner_id = %s
        ORDER BY created_at DESC
        """
        params = (owner_id,)
        
        try:
            result = query(sql, params)
            logger.info(f"Fetched rooms by owner_id={owner_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to fetch rooms by owner_id={owner_id}: {str(e)}", exc_info=True)
            raise


    @staticmethod
    def is_owner(room_id, user_id):
        """判断用户是否是房间的房主"""
        # 定义SQL查询语句和参数
        sql = """
        SELECT * FROM rooms
        WHERE id = %s AND owner_id = %s
        """
        params = (room_id, user_id)

        try:
            # 执行查询
            result = query(sql, params)
            
            # 检查查询结果并返回布尔值
            if result:
                logger.info(f"User={user_id} is the owner of room={room_id}")
                return True
            else:
                logger.info(f"User={user_id} is NOT the owner of room={room_id}")
                return False

        except Exception as e:
            # 捕获异常并记录错误信息
            logger.error(f"Error occurred while checking ownership for room={room_id}, user={user_id}: {e}")
            return False
    @staticmethod
    def get_all_rooms() -> List[Dict]:
        """获取所有房间基础信息（包含密码字段）"""
        sql = """
        SELECT id, room_name, password
        FROM Rooms
        ORDER BY created_at DESC
        """
        try:
            return query(sql) or []
        except Exception as e:
            logger.error(f"获取所有房间失败: {str(e)}")
            raise