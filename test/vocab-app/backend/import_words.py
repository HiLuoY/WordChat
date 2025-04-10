import csv
import os
from models.word_model import Word
from database.db_utils import get_db_connection

def import_words_from_csv(csv_file):
    """从CSV文件导入单词"""
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:  # 确保至少有单词和含义
                    word = row[0].strip()
                    meaning = row[1].strip()
                    hint = row[2].strip() if len(row) > 2 else None
                    
                    # 检查单词是否已存在
                    existing_word = Word.get_word_by_text(word)
                    if not existing_word:
                        Word.create_word(word, meaning, hint)
                        print(f"已导入单词: {word}")
                    else:
                        print(f"单词已存在: {word}")
    except Exception as e:
        print(f"导入失败: {str(e)}")

if __name__ == "__main__":
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建CSV文件路径
    csv_file = os.path.join(current_dir, "yasi.csv")
    
    if os.path.exists(csv_file):
        print("开始导入单词...")
        import_words_from_csv(csv_file)
        print("导入完成！")
    else:
        print(f"错误：找不到文件 {csv_file}") 