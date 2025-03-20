from flask import Flask, request, jsonify
from models.user_model import User
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

    # 检查邮箱是否已存在
    if User.get_user_by_email(email):
        return jsonify({'code': 400, 'message': '邮箱已存在'}), 400

    # 创建用户
    if User.create_user(email, password, nickname):
        return jsonify({'code': 200, 'message': '注册成功'}), 200
    else:
        return jsonify({'code': 500, 'message': '服务器错误，请稍后重试'}), 500
if __name__ == '__main__':
    app.run(debug=True)