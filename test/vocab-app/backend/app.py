from flask import Flask, request, jsonify, session, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import secrets
from models.user_model import User
from models.room_model import Room
from models.message_model import Message

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # 会话加密密钥
app.config['SESSION_TYPE'] = 'filesystem'  # 会话存储方式

# 初始化SocketIO（使用eventlet异步模式）
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# ==================== HTTP路由部分 ====================



# ---------- 房间管理 ----------

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

    if not Room.is_member(room_id, session['user_id']):
        emit('error', {'message': '未加入该房间'})
        return

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

    if not Room.is_member(room_id, session['user_id']):
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