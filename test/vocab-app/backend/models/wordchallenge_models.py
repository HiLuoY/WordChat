from database.db_utils import query, insert, update, delete
from datetime import datetime
import logging
from database.db_utils import get_db_connection

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WordChallenge:
    @staticmethod
    def create_challenge(room_id, word_id, round_number=1):
        """创建挑战（带事务和重试）"""
        import pymysql
        
        logger.info(
            "[模型层] 创建挑战 | room_id=%s | word_id=%s | round=%s",
            room_id, word_id, round_number
        )

        conn = None
        try:
            conn = get_db_connection()  # 修改调用名称
            with conn.cursor() as cursor:
                # ===== 1. 预检查 =====
                # 检查房间是否存在
                cursor.execute("SELECT id FROM rooms WHERE id = %s", (room_id,))
                if not cursor.fetchone():
                    logger.error("[模型层] 房间不存在: %s", room_id)
                    raise ValueError("房间不存在")

                # 检查单词是否存在
                cursor.execute("SELECT word FROM words WHERE id = %s", (word_id,))
                if not cursor.fetchone():
                    logger.error("[模型层] 单词不存在: %s", word_id)
                    raise ValueError("单词不存在")

                # ===== 2. 插入挑战 =====
                sql = """
                INSERT INTO wordchallenges (
                    room_id, 
                    word_id, 
                    round_number, 
                    status, 
                    started_at
                ) VALUES (%s, %s, %s, 'ongoing', %s)
                """
                params = (
                    room_id,
                    word_id,
                    round_number,
                    datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                )
                
                logger.debug("[模型层] 执行SQL: %s | 参数: %s", sql, params)
                cursor.execute(sql, params)
                challenge_id = cursor.lastrowid
                conn.commit()

                logger.info("[模型层] 挑战创建成功: id=%s", challenge_id)
                return challenge_id

        except pymysql.IntegrityError as e:
            logger.error("[模型层] 外键约束错误: %s", e.args[1])
            raise ValueError("数据不完整，请检查房间/单词是否存在")
        except pymysql.OperationalError as e:
            logger.error("[模型层] 数据库连接错误: %s", e.args[1])
            raise
        finally:
            if conn:
                conn.close()   
    def get_challenge_by_id(challenge_id):
        """根据ID获取挑战信息"""
        sql = "SELECT * FROM wordchallenges WHERE id = %s"
        try:
            result = query(sql, (challenge_id,))
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to get challenge by id={challenge_id}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_current_challenge(room_id):
        """获取房间当前进行中的挑战"""
        sql = """
        SELECT * FROM WordChallenges 
        WHERE room_id = %s AND status = 'ongoing'
        ORDER BY started_at DESC
        LIMIT 1
        """
        try:
            result = query(sql, (room_id,))
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to get current challenge for room_id={room_id}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_challenges_by_room(room_id, limit=10):
        """获取房间的所有挑战历史"""
        sql = """
        SELECT * FROM WordChallenges 
        WHERE room_id = %s
        ORDER BY started_at DESC
        LIMIT %s
        """
        try:
            return query(sql, (room_id, limit))
        except Exception as e:
            logger.error(f"Failed to get challenges for room_id={room_id}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def update_challenge_status(challenge_id, new_status):
        """更新挑战状态"""
        if new_status not in ['ongoing', 'finished']:
            raise ValueError("Invalid status. Must be 'ongoing' or 'finished'")
            
        sql = "UPDATE WordChallenges SET status = %s WHERE id = %s"
        try:
            success = update(sql, (new_status, challenge_id))
            logger.info(f"Updated challenge {challenge_id} status to {new_status}")
            return success
        except Exception as e:
            logger.error(f"Failed to update challenge {challenge_id} status: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def increment_round(challenge_id):
        """增加挑战轮次"""
        sql = "UPDATE WordChallenges SET round_number = round_number + 1 WHERE id = %s"
        try:
            success = update(sql, (challenge_id,))
            logger.info(f"Incremented round for challenge {challenge_id}")
            return success
        except Exception as e:
            logger.error(f"Failed to increment round for challenge {challenge_id}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def finish_challenge(challenge_id):
        """结束挑战"""
        return WordChallenge.update_challenge_status(challenge_id, 'finished')

    @staticmethod
    def delete_challenge(challenge_id):
        """删除挑战"""
        sql = "DELETE FROM WordChallenges WHERE id = %s"
        try:
            success = delete(sql, (challenge_id,))
            logger.info(f"Deleted challenge {challenge_id}")
            return success
        except Exception as e:
            logger.error(f"Failed to delete challenge {challenge_id}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_challenge_word(challenge_id):
        """获取挑战对应的单词"""
        sql = """
        SELECT w.* FROM Words w
        JOIN WordChallenges wc ON w.id = wc.word_id
        WHERE wc.id = %s
        """
        try:
            result = query(sql, (challenge_id,))
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to get word for challenge {challenge_id}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def check_answer(challenge_id, user_id, answer):
        """验证用户答案"""
        try:
            # 获取挑战信息
            challenge = WordChallenge.get_challenge_by_id(challenge_id)
            if not challenge:
                return {'correct': False, 'message': '挑战不存在'}

            # 获取正确答案
            word = WordChallenge.get_challenge_word(challenge_id)
            if not word:
                return {'correct': False, 'message': '未找到相关单词'}

            # 验证答案
            correct_answer = word['word'].lower()
            user_answer = answer.lower().strip()
            
            # 记录答题记录
            WordChallenge.record_attempt(challenge_id, user_id, user_answer, correct_answer == user_answer)

            if correct_answer == user_answer:
                return {
                    'correct': True,
                    'message': '回答正确！',
                    'word': word['word'],
                    'meaning': word['meaning']
                }
            else:
                return {
                    'correct': False,
                    'message': '回答错误，请继续尝试',
                    'hint': '提示：' + (word['hint'] if 'hint' in word and word['hint'] is not None else '无提示')
                }

        except Exception as e:
            logger.error(f"Failed to check submitted_word for challenge {challenge_id}: {str(e)}", exc_info=True)
            return {'correct': False, 'message': '验证答案时发生错误'}

    @staticmethod
    def record_attempt(challenge_id, user_id, answer, is_correct):
        """记录答题记录"""
        sql = """
        INSERT INTO ChallengeAttempts (challenge_id, user_id, submitted_word, is_correct, timestamp)
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            insert(sql, (challenge_id, user_id, answer, is_correct, datetime.utcnow()))
        except Exception as e:
            logger.error(f"Failed to record attempt for challenge {challenge_id}: {str(e)}", exc_info=True)