from flask import Flask, request, jsonify
from database.db_utils import get_db_connection

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 确保 JSON 返回中文字符

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    nickname = data.get('nickname')

    if not email or not password or not nickname:
        return jsonify({'code': 400, 'message': '邮箱、密码和昵称不能为空'}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # 检查邮箱是否已存在
            sql = "SELECT * FROM Users WHERE email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()
            if user:
                return jsonify({'code': 400, 'message': '邮箱已存在'}), 400

            # 插入新用户
            sql = """
                INSERT INTO Users (email, password, nickname, created_at, updated_at)
                VALUES (%s, %s, %s, NOW(), NOW())
            """
            cursor.execute(sql, (email, password, nickname))
            connection.commit()

            return jsonify({'code': 200, 'message': '注册成功'}), 200
    except Exception as e:
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'}), 500
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)