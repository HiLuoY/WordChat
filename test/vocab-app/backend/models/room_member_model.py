from database.db_utils import insert, query, update, delete
from datetime import datetime
import logging
from typing import Optional, Dict, List

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RoomMember:
    @staticmethod
    def add_member(room_id: int, user_id: int) -> int:
        """
        添加用户到房间
        :param room_id: 房间ID
        :param user_id: 用户ID
        :return: 新创建的成员关系ID
        :raises: ValueError 如果成员关系已存在
        """
        # 检查是否已经是成员
        if RoomMember.is_member(room_id, user_id):
            raise ValueError(f"User {user_id} is already a member of room {room_id}")
        
        sql = """
        INSERT INTO RoomMembers (room_id, user_id, joined_at)
        VALUES (%s, %s, %s)
        """
        params = (room_id, user_id, datetime.utcnow())
        
        try:
            member_id = insert(sql, params)
            logger.info(f"Member added successfully: id={member_id}, room_id={room_id}, user_id={user_id}")
            return member_id
        except Exception as e:
            logger.error(f"Failed to add member: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def remove_member(room_id: int, user_id: int) -> bool:
        """
        从房间移除用户，并同步清理排行榜记录
        :param room_id: 房间ID
        :param user_id: 用户ID
        :return: 是否删除成功
        """
        # 1. 删除房间成员记录
        member_sql = """
        DELETE FROM RoomMembers 
        WHERE room_id = %s AND user_id = %s
        """
        member_params = (room_id, user_id)

        # 2. 删除排行榜记录
        leaderboard_sql = """
        DELETE FROM Leaderboard
        WHERE room_id = %s AND user_id = %s
        """
        leaderboard_params = (room_id, user_id)

        try:
            # 删除成员记录
            member_success = delete(member_sql, member_params)
                
            # 删除排行榜记录（即使成员不存在也尝试清理）
            leaderboard_success = delete(leaderboard_sql, leaderboard_params)
                
            if member_success and leaderboard_success:
                logger.info(
                    f"Removed member and leaderboard: room_id={room_id}, user_id={user_id}"
                )
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to remove member and leaderboard: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def is_member(room_id: int, user_id: int) -> bool:
        """
        检查用户是否是房间成员
        :param room_id: 房间ID
        :param user_id: 用户ID
        :return: 是否是成员
        """
        sql = """
        SELECT 1 FROM RoomMembers 
        WHERE room_id = %s AND user_id = %s
        LIMIT 1
        """
        params = (room_id, user_id)
        
        try:
            result = query(sql, params)
            return bool(result)
        except Exception as e:
            logger.error(f"Failed to check membership: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_members(room_id: int) -> List[Dict]:
        """
        获取房间所有成员
        :param room_id: 房间ID
        :return: 成员列表
        """
        sql = """
        SELECT rm.id, rm.room_id, rm.user_id, rm.joined_at, 
               u.nickname, u.avatar, u.email
        FROM RoomMembers rm
        JOIN Users u ON rm.user_id = u.id
        WHERE rm.room_id = %s
        ORDER BY rm.joined_at ASC
        """
        params = (room_id,)
        
        try:
            result = query(sql, params)
            logger.info(f"Fetched members for room_id={room_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to fetch members: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_rooms_for_user(user_id: int) -> List[Dict]:
        """
        获取用户加入的所有房间
        :param user_id: 用户ID
        :return: 房间列表
        """
        sql = """
        SELECT rm.id as member_id, rm.joined_at, 
               r.id as room_id, r.room_name, r.owner_id, r.created_at
        FROM RoomMembers rm
        JOIN Rooms r ON rm.room_id = r.id
        WHERE rm.user_id = %s
        ORDER BY rm.joined_at DESC
        """
        params = (user_id,)
        
        try:
            result = query(sql, params)
            logger.info(f"Fetched rooms for user_id={user_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to fetch rooms for user: {str(e)}", exc_info=True)
            raise