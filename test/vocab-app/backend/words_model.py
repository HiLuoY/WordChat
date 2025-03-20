import pandas as pd
from database.db_utils import get_db_connection

class WordsImporter:
    @staticmethod
    def import_from_csv(csv_file_path):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # 读取 CSV 文件
                df = pd.read_csv(csv_file_path, header=None, names=['word', 'meaning'],nrows=100)
                
                # 准备 SQL 插入语句
                insert_query = """
                INSERT INTO Words (word, meaning)
                VALUES (%s, %s)
                """
                # 为 DataFrame 中的每一行执行插入操作
                for index, row in df.iterrows():
                    cursor.execute(insert_query, (row['word'], row['meaning']))
                connection.commit()
                print("Data imported successfully.")
        except Exception as e:
            print(f"Error importing data: {e}")
        finally:
            connection.close()

# CSV 文件路径
csv_file_path = 'kaoyan.csv'  # 替换为你的 CSV 文件路径

# 调用函数导入数据
WordsImporter.import_from_csv(csv_file_path)