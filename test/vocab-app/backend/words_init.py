from models.word_model import Word
from datetime import datetime

def init_words():
    """初始化一些测试单词"""
    words = [
        {"word": "apple", "meaning": "苹果", "hint": "一种水果"},
        {"word": "banana", "meaning": "香蕉", "hint": "黄色的水果"},
        {"word": "orange", "meaning": "橙子", "hint": "圆形的水果"},
        {"word": "grape", "meaning": "葡萄", "hint": "紫色或绿色的水果"},
        {"word": "pear", "meaning": "梨", "hint": "形状像葫芦的水果"}
    ]
    
    for word_data in words:
        try:
            # 检查单词是否已存在
            existing_word = Word.get_word_by_text(word_data["word"])
            if not existing_word:
                Word.create_word(
                    word=word_data["word"],
                    meaning=word_data["meaning"],
                    hint=word_data["hint"]
                )
                print(f"已添加单词: {word_data['word']}")
            else:
                print(f"单词已存在: {word_data['word']}")
        except Exception as e:
            print(f"添加单词失败 {word_data['word']}: {str(e)}")

if __name__ == "__main__":
    print("开始初始化单词...")
    init_words()
    print("初始化完成！")
