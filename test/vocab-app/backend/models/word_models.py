from database.db_utils import query, insert, update, delete
import pandas as pd
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Word:
    @staticmethod
    def add_word(word, meaning):
        """添加新单词"""
        sql = "INSERT INTO Words (word, meaning) VALUES (%s, %s)"
        try:
            word_id = insert(sql, (word, meaning))
            logger.info(f"Added new word: {word} (ID: {word_id})")
            return word_id
        except Exception as e:
            logger.error(f"Failed to add word {word}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def import_from_csv(csv_file_path):
        """从CSV文件导入单词"""
        try:
            # 读取 CSV 文件
            df = pd.read_csv(csv_file_path, header=None, names=['word', 'meaning'], nrows=100)
            logger.info(f"Reading CSV file: {csv_file_path}, found {len(df)} records")
            
            # 准备 SQL 插入语句
            insert_query = "INSERT INTO Words (word, meaning) VALUES (%s, %s)"
            success_count = 0
            
            # 为 DataFrame 中的每一行执行插入操作
            for index, row in df.iterrows():
                try:
                    insert(insert_query, (row['word'], row['meaning']))
                    success_count += 1
                except Exception as e:
                    logger.warning(f"Failed to import word {row['word']}: {str(e)}")
            
            logger.info(f"Data import completed. Successfully imported {success_count}/{len(df)} words")
            return success_count
        except Exception as e:
            logger.error(f"Failed to import from CSV {csv_file_path}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_random_word():
        """获取随机单词"""
        sql = "SELECT * FROM Words ORDER BY RAND() LIMIT 1"
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
        sql = "SELECT * FROM Words"
        try:
            result = query(sql)
            logger.info(f"Fetched all words from database (count: {len(result)})")
            return result
        except Exception as e:
            logger.error(f"Failed to get all words: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_word_by_id(word_id):
        """根据ID获取单词"""
        sql = "SELECT * FROM Words WHERE id = %s"
        try:
            result = query(sql, (word_id,))
            logger.debug(f"Fetched word by ID: {word_id}")
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to get word by ID {word_id}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def update_word(word_id, word=None, meaning=None):
        """更新单词信息"""
        # 构建动态更新SQL
        updates = []
        params = []
        
        if word is not None:
            updates.append("word = %s")
            params.append(word)
        
        if meaning is not None:
            updates.append("meaning = %s")
            params.append(meaning)
        
        if not updates:
            logger.warning("No fields provided for update")
            return False
            
        sql = f"UPDATE Words SET {', '.join(updates)} WHERE id = %s"
        params.append(word_id)
        
        try:
            success = update(sql, tuple(params))
            if success:
                logger.info(f"Updated word ID {word_id}: {updates}")
            else:
                logger.warning(f"No word found with ID {word_id} to update")
            return success
        except Exception as e:
            logger.error(f"Failed to update word ID {word_id}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def delete_word(word_id):
        """删除单词"""
        sql = "DELETE FROM Words WHERE id = %s"
        try:
            success = delete(sql, (word_id,))
            if success:
                logger.info(f"Deleted word ID {word_id}")
            else:
                logger.warning(f"No word found with ID {word_id} to delete")
            return success
        except Exception as e:
            logger.error(f"Failed to delete word ID {word_id}: {str(e)}", exc_info=True)
            raise