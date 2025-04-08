from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from models.user_model import User
from database.db_utils import get_db_connection
from challenges import challenge_bp  # 导入挑战蓝图

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 确保 JSON 返回中文字符
app.config['SECRET_KEY'] = 'your-secret-key'  # 用于session加密

# 初始化SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# 注册蓝图
app.register_blueprint(challenge_bp)

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

# WebSocket事件处理
@socketio.on('join')
def on_join(data):
    """用户加入房间"""
    room = data['room_id']
    join_room(room)
    emit('status', {'msg': f'用户加入房间 {room}'}, room=room)

@socketio.on('leave')
def on_leave(data):
    """用户离开房间"""
    room = data['room_id']
    leave_room(room)
    emit('status', {'msg': f'用户离开房间 {room}'}, room=room)

@socketio.on('submit_answer')
def on_submit_answer(data):
    """处理用户提交的答案"""
    room = data['room_id']
    challenge_id = data['challenge_id']
    answer = data['answer']
    user_id = data['user_id']
    
    # 验证答案并广播结果
    result = WordChallenge.check_answer(challenge_id, answer)
    emit('answer_result', {
        'user_id': user_id,
        'correct': result['correct'],
        'message': result['message']
    }, room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)