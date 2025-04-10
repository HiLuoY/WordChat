from database.db_utils import insert, query, update, delete
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Word:
    @staticmethod
    def create_word(word: str, meaning: str, hint: str = None) -> int:
        """
        创建新单词
        :param word: 单词
        :param meaning: 含义
        :param hint: 提示（可选）
        :return: 新创建的单词ID
        """
        sql = """
        INSERT INTO words (word, meaning, hint, created_at)
        VALUES (%s, %s, %s, %s)
        """
        params = (word, meaning, hint, datetime.utcnow())
        
        try:
            word_id = insert(sql, params)
            logger.info(f"Word created successfully: id={word_id}, word={word}")
            return word_id
        except Exception as e:
            logger.error(f"Failed to create word: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_word_by_id(word_id: int):
        """
        根据ID获取单词信息
        :param word_id: 单词ID
        :return: 单词信息字典或None(如果单词不存在)
        """
        sql = "SELECT * FROM words WHERE id = %s"
        try:
            result = query(sql, (word_id,))
            if not result:
                logger.warning(f"Word not found: id={word_id}")
                return None
                
            word = result[0]
            logger.info(f"Fetched word by id={word_id}: {word}")
            return word
        except Exception as e:
            logger.error(f"Failed to get word by id={word_id}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_word_by_text(word: str):
        """
        根据单词文本获取单词信息
        :param word: 单词文本
        :return: 单词信息字典或None(如果单词不存在)
        """
        sql = "SELECT * FROM words WHERE word = %s"
        try:
            result = query(sql, (word,))
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to get word by text={word}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def update_word(word_id: int, meaning: str = None, hint: str = None) -> bool:
        """
        更新单词信息
        :param word_id: 单词ID
        :param meaning: 新的含义（可选）
        :param hint: 新的提示（可选）
        :return: 是否更新成功
        """
        updates = []
        params = []
        
        if meaning is not None:
            updates.append("meaning = %s")
            params.append(meaning)
        if hint is not None:
            updates.append("hint = %s")
            params.append(hint)
            
        if not updates:
            return True
            
        sql = f"UPDATE words SET {', '.join(updates)} WHERE id = %s"
        params.append(word_id)
        
        try:
            success = update(sql, tuple(params))
            logger.info(f"Word updated successfully: id={word_id}")
            return success
        except Exception as e:
            logger.error(f"Failed to update word: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def delete_word(word_id: int) -> bool:
        """
        删除单词
        :param word_id: 单词ID
        :return: 是否删除成功
        """
        sql = "DELETE FROM words WHERE id = %s"
        try:
            success = delete(sql, (word_id,))
            logger.info(f"Word deleted successfully: id={word_id}")
            return success
        except Exception as e:
            logger.error(f"Failed to delete word: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_all_words():
        """获取所有单词"""
        logger.info('开始从数据库获取所有单词')
        sql = "SELECT * FROM words ORDER BY word ASC"
        try:
            words = query(sql)
            if not words:
                logger.warning("数据库中没有单词")
                return []
                
            logger.info(f"从数据库获取到 {len(words)} 个单词")
            for word in words:
                logger.debug(f"单词信息: id={word.get('id')}, word={word.get('word')}, meaning={word.get('meaning')}")
            return words
        except Exception as e:
            logger.error(f"获取所有单词失败: {str(e)}", exc_info=True)
            raise 