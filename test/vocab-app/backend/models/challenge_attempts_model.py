from database.db_utils import get_db_connection
from datetime import datetime

class ChallengeAttempt:
    @staticmethod
    def create_attempt(challenge_id, user_id, submitted_word, is_correct):
        """
        创建新的挑战记录
        :param challenge_id: 挑战ID
        :param user_id: 用户ID
        :param submitted_word: 提交的单词
        :param is_correct: 是否正确
        :return: 成功返回True，失败返回False
        """
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO ChallengeAttempts 
                    (challenge_id, user_id, submitted_word, is_correct, timestamp)
                    VALUES (%s, %s, %s, %s, NOW())
                """
                cursor.execute(sql, (challenge_id, user_id, submitted_word, is_correct))
                connection.commit()
                return True
        except Exception as e:
            print(f"创建挑战记录失败: {e}")
            return False
        finally:
            connection.close()

    @staticmethod
    def get_attempts_by_user(user_id, limit=10):
        """
        获取用户最近的挑战记录
        :param user_id: 用户ID
        :param limit: 返回的记录数
        :return: 记录列表或None
        """
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    SELECT * FROM ChallengeAttempts 
                    WHERE user_id = %s 
                    ORDER BY timestamp DESC 
                    LIMIT %s
                """
                cursor.execute(sql, (user_id, limit))
                return cursor.fetchall()
        except Exception as e:
            print(f"获取用户挑战记录失败: {e}")
            return None
        finally:
            connection.close()

    @staticmethod
    def get_correct_rate(user_id):
        """
        计算用户挑战正确率
        :param user_id: 用户ID
        :return: 正确率(0-1)或None
        """
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 查询总尝试次数
                sql_total = "SELECT COUNT(*) FROM ChallengeAttempts WHERE user_id = %s"
                cursor.execute(sql_total, (user_id,))
                total = cursor.fetchone()[0]
                
                if total == 0:
                    return 0.0
                
                # 查询正确次数
                sql_correct = """
                    SELECT COUNT(*) FROM ChallengeAttempts 
                    WHERE user_id = %s AND is_correct = TRUE
                """
                cursor.execute(sql_correct, (user_id,))
                correct = cursor.fetchone()[0]
                
                return round(correct / total, 2)
        except Exception as e:
            print(f"计算正确率失败: {e}")
            return None
        finally:
            connection.close()

    @staticmethod
    def get_recent_attempts(challenge_id, limit=20):
        """
        获取某个挑战的最近记录
        :param challenge_id: 挑战ID
        :param limit: 返回的记录数
        :return: 记录列表或None
        """
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    SELECT * FROM ChallengeAttempts 
                    WHERE challenge_id = %s 
                    ORDER BY timestamp DESC 
                    LIMIT %s
                """
                cursor.execute(sql, (challenge_id, limit))
                return cursor.fetchall()
        except Exception as e:
            print(f"获取挑战记录失败: {e}")
            return None
        finally:
            connection.close()