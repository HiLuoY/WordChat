import pandas as pd
from backend.models.word_models import Word

# CSV 文件路径
csv_file_path1 = 'yasi.csv'  # 替换为你的 CSV 文件路径
csv_file_path2 = 'kaoyan.csv'  # 替换为你的 CSV 文件路径

if __name__ == '__main__':
    Word.import_from_csv(csv_file_path1)
    Word.import_from_csv(csv_file_path2)
