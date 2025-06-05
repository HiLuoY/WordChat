import pandas as pd
from database.db_utils import insert, query, update, delete
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Word:
    @staticmethod
    def create_word(word: str, meaning: str) -> int:
        """
        创建新单词
        :param word: 单词
        :param meaning: 含义
        """
        sql = """
        INSERT INTO Words (word, meaning)
        VALUES (%s, %s)
        """
        params = (word, meaning)
        
        try:
            word_id = insert(sql, params)
            logger.info(f"word created successfully: id={word_id}, word={word}")
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
        sql = "SELECT * FROM Words WHERE id = %s"
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
        sql = "SELECT * FROM Words WHERE word = %s"
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
        sql = "DELETE FROM Words WHERE id = %s"
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
        sql = "SELECT * FROM Words ORDER BY word ASC"
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

    @staticmethod
    def add_word(word, meaning):
        """添加新单词"""
        sql = "INSERT INTO words (word, meaning) VALUES (%s, %s)"
        try:
            word_id = insert(sql, (word, meaning))
            logger.info(f"Added new word: {word} (ID: {word_id})")
            return word_id
        except Exception as e:
            logger.error(f"Failed to add word {word}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_random_word():
        """获取随机单词"""
        sql = "SELECT * FROM words ORDER BY RAND() LIMIT 1"
        try:
            result = query(sql)
            logger.debug("Fetched random word from database")
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to get random word: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_all_words():
        """获取所有单词"""
        sql = "SELECT * FROM words"
        try:
            result = query(sql)
            logger.info(f"Fetched all words from database (count: {len(result)})")
            return result
        except Exception as e:
            logger.error(f"Failed to get all words: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def import_from_csv(csv_file, limit=None):
        """
        从CSV文件导入单词
        :param csv_file: CSV文件路径
        :param limit: 限制导入的单词数量，None表示导入所有单词
        :return: 成功导入的单词数量
        """
        try:
            # 读取CSV文件
            df = pd.read_csv(csv_file)
            
            # 如果设置了限制，只取前limit行
            if limit is not None:
                df = df.head(limit)
            
            # 导入单词
            success_count = 0
            for _, row in df.iterrows():
                try:
                    word = row[0]
                    meaning = row[1]
                
                    # 检查单词是否已存在
                    existing_word = Word.get_word_by_text(word)
                    if existing_word:
                        logger.info(f"单词已存在，跳过: {word}")
                        continue
                    
                    # 创建新单词
                    Word.create_word(word, meaning)
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"导入单词失败 {word}: {str(e)}")
                    continue
            
            logger.info(f"从 {csv_file} 成功导入 {success_count} 个单词")
            return success_count
            
        except Exception as e:
            logger.error(f"导入CSV文件失败: {str(e)}")
            raise
