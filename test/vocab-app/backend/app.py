from flask import Flask, request, jsonify, session, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import secrets
from models.user_model import User
from models.room_model import Room
from models.message_model import Message
from models.room_member_model import RoomMember
from werkzeug.security import generate_password_hash, check_password_hash  # 添加导入

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # 会话加密密钥
app.config['SESSION_TYPE'] = 'filesystem'  # 会话存储方式

# 初始化SocketIO（使用eventlet异步模式）
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# ==================== HTTP路由部分 ====================


@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    nickname = data.get('nickname')
    avatar = data.get('avatar')

    if not email or not password or not nickname:
        return jsonify({'message': 'Missing arguments'}), 400

    try:
        # 密码哈希
        password_hash = generate_password_hash(password)
        # 创建用户
        user_id = User.create_user(email, password_hash, nickname, avatar)
        return jsonify({'message': 'User created successfully', 'user_id': user_id}), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Missing arguments'}), 400

    try:
        user_info = User.get_user_by_email(email)
        if user_info and check_password_hash(user_info["password_hash"], password):
            session['user_id'] = user_info['id']
            session['nickname'] = user_info['nickname']
            session.permanent = True  # 设置会话为永久会话
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# ---------- 房间管理 ----------
@app.route('/rooms', methods=['GET'])
def get_rooms():
    """获取房间列表"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        rooms = Room.list_rooms(page, per_page)
        return jsonify({'rooms': rooms}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/rooms', methods=['POST'])
def create_room():
    """创建新房间"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'message': '请先登录'}), 401
    
    data = request.get_json()
    room_name = data.get('room_name')
    password = data.get('password', None)
    
    if not room_name:
        return jsonify({'message': '房间名不能为空'}), 400
    
    try:
        room_id = Room.create_room(room_name, session['user_id'], password)
        # 自动将创建者加入房间
        RoomMember.add_member(room_id, session['user_id'])
        return jsonify({
            'message': '房间创建成功',
            'room_id': room_id
        }), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500



@app.route('/rooms/<int:room_id>/leave', methods=['POST'])
def leave_room(room_id):
    """离开房间"""
    if 'user_id' not in session:
        return jsonify({'message': '请先登录'}), 401
    
    try:
        RoomMember.remove_member(room_id, session['user_id'])
        
        # 通知房间成员
        socketio.emit('member_left', {
            'user_id': session['user_id'],
            'nickname': session['nickname'],
            'room_id': room_id,
            'timestamp': datetime.now().isoformat()
        }, room=str(room_id))
        
        return jsonify({'message': '已离开房间'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/rooms/<int:room_id>/members', methods=['GET'])
def get_room_members(room_id):
    """获取房间成员列表"""
    try:
        members = RoomMember.get_members(room_id)
        return jsonify({'members': members}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/rooms/<int:room_id>/messages', methods=['GET'])
def get_room_messages(room_id):
    """获取房间历史消息"""
    try:
        messages = Message.get_messages_by_room(room_id)
        return jsonify({'messages': messages}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# ==================== WebSocket部分 ====================
@socketio.on('connect')
def handle_connect():
    """WebSocket连接建立"""
    if 'user_id' in session:
        print(f"用户 {session['nickname']} 已连接")
    else:
        emit('error', {'message': '未认证的连接'})

@socketio.on('join_room')
def handle_join_room(data):
    """加入聊天房间"""
    room_id = data.get('room_id')
    if 'user_id' not in session:
        emit('error', {'message': '请先登录'})
        return

    # 如果用户不是房间成员，则加入房间
    if not RoomMember.is_member(room_id, session['user_id']):
        RoomMember.add_member(room_id, session['user_id'])

    join_room(room_id)
    emit('system_message', {
        'message': f"{session['nickname']} 进入了房间",
        'timestamp': datetime.now().isoformat()
    }, room=room_id)

@socketio.on('send_message')
def handle_send_message(data):
    """处理聊天消息"""
    room_id = data.get('room_id')
    content = data.get('content')

    if 'user_id' not in session:
        emit('error', {'message': '请先登录'})
        return

    if not RoomMember.is_member(room_id, session['user_id']):
        emit('error', {'message': '无权在此房间发言'})
        return

    # 保存到数据库
    message_id = Message.send_message(
        room_id=room_id,
        user_id=session['user_id'],
        message=content,
        message_type='normal'
    )

    # 广播消息
    emit('new_message', {
        'message_id': message_id,
        'user_id': session['user_id'],
        'nickname': session['nickname'],
        'content': content,
        'timestamp': datetime.now().isoformat()
    }, room=room_id)

# ==================== 启动应用 ====================
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)