from database.db_utils import query, insert, update, delete
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WordChallenge:
    @staticmethod
    def create_challenge(room_id, word_id, round_number=1):
        """创建新的单词挑战"""
        sql = """
        INSERT INTO WordChallenges (room_id, word_id, round_number, status, started_at)
        VALUES (%s, %s, %s, 'ongoing', %s)
        """
        params = (room_id, word_id, round_number, datetime.utcnow())
        try:
            challenge_id = insert(sql, params)
            logger.info(f"Created new word challenge: room_id={room_id}, word_id={word_id}")
            return challenge_id
        except Exception as e:
            logger.error(f"Failed to create word challenge: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_challenge_by_id(challenge_id):
        """根据ID获取挑战信息"""
        sql = "SELECT * FROM WordChallenges WHERE id = %s"
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