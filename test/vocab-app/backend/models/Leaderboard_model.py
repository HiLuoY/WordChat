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
                # 在 Leaderboard.get_room_leaderboard 方法中
                sql = """
                SELECT 
                    u.nickname, 
                    l.score, 
                    DATE_FORMAT(l.updated_at, '%%Y-%%m-%%dT%%H:%%i:%%sZ') AS updated_at,
                    l.user_id
                FROM Leaderboard l
                INNER JOIN Users u ON l.user_id = u.id
                WHERE l.room_id = %s
                ORDER BY l.score DESC
                LIMIT %s
            """
                cursor.execute(sql, (room_id, limit))
                print(f"执行查询：{sql % (room_id, limit)}")
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
        :return: 排名（从1开始）或 None（如果无记录）
        """
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
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
                if result and 'position' in result:
                    rank = result['position']
                    print(f"获取用户排名成功: room_id={room_id}, user_id={user_id}, rank={rank}")
                    return rank
                else:
                    print(f"获取用户排名失败: room_id={room_id}, user_id={user_id}, result={result}")
                    return None
        except Exception as e:
            print(f"获取用户排名失败: room_id={room_id}, user_id={user_id}, error={e}")
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

    @staticmethod
    def get_user_score(room_id, user_id):
        """
        获取用户在房间中的当前分数
        :param room_id: 房间ID
        :param user_id: 用户ID
        :return: 用户的当前分数，如果用户不存在于排行榜中，则返回0
        """
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT score FROM Leaderboard WHERE room_id = %s AND user_id = %s"
                cursor.execute(sql, (room_id, user_id))
                result = cursor.fetchone()
                return result['score'] if result else 0
        except Exception as e:
            print(f"获取用户分数失败: {e}")
            return 0
        finally:
            connection.close()

    @staticmethod
    def get_room_users(room_id):
        """
        获取房间内所有用户的ID列表
        :param room_id: 房间ID
        :return: 用户ID列表（如果无记录则返回空列表）
        """
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT user_id FROM Leaderboard WHERE room_id = %s"
                cursor.execute(sql, (room_id,))
                result = cursor.fetchall()
                # 提取所有user_id并返回列表
                return [row['user_id'] for row in result] if result else []
        except Exception as e:
            print(f"获取房间用户列表失败: {e}")
            return []  # 出错时返回空列表
        finally:
            connection.close()

    @staticmethod
    def initialize_user_score(room_id, user_id):
        """
        初始化用户在房间中的分数为0（不存在时创建，存在时重置为0）
        :param room_id: 房间ID 
        :param user_id: 用户ID
        :return: 成功返回True，失败返回False
        """
        print(f"[DEBUG] 开始初始化分数 | room_id={room_id} user_id={user_id}")

        connection = None
         # 确保 room_id 和 user_id 是整数
        try:
            room_id = int(room_id)
            user_id = int(user_id)
        except ValueError:
            print(f"初始化用户分数失败: room_id 或 user_id 无法转换为整数")
            return False

        try:
            # 验证参数有效性
            if not all([isinstance(room_id, int), isinstance(user_id, int)]):
                print(f"[ERROR] 参数类型错误 | room_id类型={type(room_id)} user_id类型={type(user_id)}")
                return False

            connection = get_db_connection()
            with connection.cursor() as cursor:
                # 构建SQL语句
                sql = """
                    INSERT INTO Leaderboard (room_id, user_id, score)
                    VALUES (%s, %s, 0)
                    ON DUPLICATE KEY UPDATE score = 0
                """
                params = (room_id, user_id)
                
                print(f"[SQL] 执行语句: {sql % params}")

                # 执行SQL并获取影响行数
                affected_rows = cursor.execute(sql, params)
                connection.commit()
                
                print(f"[SUCCESS] 操作成功 | 影响行数={affected_rows}")
                return True

        except pymysql.MySQLError as e:  # 假设使用PyMySQL驱动
            error_code, error_msg = e.args
            print(f"""
[ERROR] 数据库操作失败
┣ 错误代码：{error_code}
┣ 错误信息：{error_msg}
┣ 完整参数：room_id={room_id} user_id={user_id}
┗ 堆栈跟踪：{traceback.format_exc()}
            """)
            if connection:
                connection.rollback()
            return False

        except Exception as e:
            print(f"[CRITICAL] 未知错误: {str(e)}")
            return False

        finally:
            if connection:
                try:
                    connection.close()
                    print("[CONN] 数据库连接已关闭")
                except Exception as e:
                    print(f"[WARNING] 关闭连接失败: {str(e)}")


    