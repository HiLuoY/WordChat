import os
from models.word_model import Word

def import_words_from_csv(csv_file):
    """从CSV文件导入单词"""
    try:
        success_count = Word.import_from_csv(csv_file)
        print(f"成功导入 {success_count} 个单词")
    except Exception as e:
        print(f"导入失败: {str(e)}")

if __name__ == "__main__":
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 构建CSV文件路径
    csv_files = ["yasi.csv", "kaoyan.csv"]
    
    for csv_file in csv_files:
        csv_path = os.path.join(current_dir, csv_file)
        
        if os.path.exists(csv_path):
            print(f"开始导入单词... ({csv_file})")
            import_words_from_csv(csv_path)
            print(f"导入完成！ ({csv_file})")
        else:
            print(f"错误：找不到文件 {csv_path}")