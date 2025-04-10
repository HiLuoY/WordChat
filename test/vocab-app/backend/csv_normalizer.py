import csv

def process_csv(input_file, output_file):
    word_defs = []

    with open(input_file, mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                word = row[0].strip()
                definition = row[1].strip().replace('\n', ' ').replace('\r', '')
                word_defs.append([word, definition])

    with open(output_file, mode='w', newline='', encoding='utf-8-sig') as f_out:
        writer = csv.writer(f_out)
        writer.writerow(['Word', 'Definition'])
        writer.writerows(word_defs)

    print(f"✅ 成功处理并保存到：{output_file}")

# 用法
process_csv('.\\test\\vocab-app\\backend\kaoyan.csv', '.\\test\\vocab-app\\backend\standard_kaoyan.csv')
