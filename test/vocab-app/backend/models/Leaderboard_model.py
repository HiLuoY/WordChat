from database.db_utils import get_db_connection
from datetime import datetime

class Leaderboard:
    @staticmethod
    def update_score(room_id, user_id, score_delta):
        """
        更新用户在房间中的得分（如果记录不存在则创建）
        :param room_id: 房间ID
        :param user_id: 用户ID
        :param score_delta: 分数变化量（可正可负）
        :return: 成功返回True，失败返回False
        """
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 使用ON DUPLICATE KEY UPDATE实现插入或更新
                sql = """
                    INSERT INTO Leaderboard (room_id, user_id, score)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                    score = score + VALUES(score)
                """
                cursor.execute(sql, (room_id, user_id, score_delta))
                connection.commit()
                return True
        except Exception as e:
            print(f"更新排行榜失败: {e}")
            return False
        finally:
            connection.close()

    @staticmethod
    def get_room_leaderboard(room_id, limit=10):
        """
        获取房间排行榜（按分数降序排列）
        :param room_id: 房间ID
        :param limit: 返回的记录数
        :return: 排行榜列表或None
        """
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    SELECT u.nickname, l.score, l.updated_at 
                    FROM Leaderboard l
                    JOIN Users u ON l.user_id = u.id
                    WHERE l.room_id = %s
                    ORDER BY l.score DESC
                    LIMIT %s
                """
                cursor.execute(sql, (room_id, limit))
                return cursor.fetchall()
        except Exception as e:
            print(f"获取排行榜失败: {e}")
            return None
        finally:
            connection.close()

    @staticmethod
    def get_user_rank(room_id, user_id):
        """
        获取用户在房间中的排名
        :param room_id: 房间ID
        :param user_id: 用户ID
        :return: 排名（从1开始）或None（如果无记录）
        """
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 使用子查询计算排名
                sql = """
                    SELECT position FROM (
                        SELECT 
                            user_id,
                            RANK() OVER (ORDER BY score DESC) as position
                        FROM Leaderboard
                        WHERE room_id = %s
                    ) as ranks
                    WHERE user_id = %s
                """
                cursor.execute(sql, (room_id, user_id))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"获取用户排名失败: {e}")
            return None
        finally:
            connection.close()

    @staticmethod
    def reset_room_leaderboard(room_id):
        """
        重置房间排行榜（清空所有记录）
        :param room_id: 房间ID
        :return: 成功返回True，失败返回False
        """
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM Leaderboard WHERE room_id = %s"
                cursor.execute(sql, (room_id,))
                connection.commit()
                return True
        except Exception as e:
            print(f"重置排行榜失败: {e}")
            return False
        finally:
            connection.close()