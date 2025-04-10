# live_chat.py
from flask import Blueprint, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import logging
from models.user_model import User
from models.room_model import Room
from models.message_model import Message
from models.room_member_model import RoomMember
from models.wordchallenge_models import WordChallenge  # 单词挑战模型

# 创建蓝图
live_chat_bp = Blueprint('live_chat', __name__)
socketio = SocketIO(manage_session=False)

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SocketIO")  # 全局日志记录器

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'code': 401, 'message': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated_function

# WebSocket事件处理
@socketio.on('connect')
def handle_connect():
    """处理客户端连接事件"""
    try:
        logger.info(f"客户端连接成功 | SID={request.sid}")
        emit('connection_response', {'status': 'connected'})
    except Exception as e:
        logger.error(f"连接事件处理失败: {str(e)}", exc_info=True)

@socketio.on('disconnect')
def handle_disconnect():
    """处理客户端断开连接事件"""
    try:
        logger.info(f"客户端断开连接 | SID={request.sid}")
    except Exception as e:
        logger.error(f"断开连接事件处理失败: {str(e)}", exc_info=True)

@socketio.on('join_room')
def handle_join_room(data):
    """处理加入房间事件"""
    try:
        if 'user_id' not in session:
            logger.warning("User not logged in when trying to join room")
            emit('system_message', {'message': '请先登录'})
            return

        room_id = data.get('room_id')
        if not room_id:
            logger.warning("Room ID not provided")
            emit('system_message', {'message': '房间ID不能为空'})
            return

        logger.info(f"User {session['user_id']} attempting to join room {room_id}")

        # 获取房间信息
        room = Room.get_room_by_id(room_id)
        if not room:
            logger.warning(f"Room {room_id} does not exist")
            emit('system_message', {'message': '房间不存在'})
            return

        # 获取用户信息
        user = User.get_user_by_id(session['user_id'])
        if not user:
            logger.error(f"User {session['user_id']} not found")
            emit('system_message', {'message': '用户不存在'})
            return

        try:
            # 将用户添加到房间成员中
            if not RoomMember.is_member(room_id, session['user_id']):
                RoomMember.add_member(room_id, session['user_id'])
                logger.info(f"Added user {session['user_id']} to room {room_id}")

            # 加入Socket.io房间
            join_room(str(room_id))
            logger.info(f"User {session['user_id']} joined socket room {room_id}")

            # 判断是否是房主
            is_owner = room['owner_id'] == session['user_id']

            # 发送加入成功消息
            emit('room_joined', {
                'room_id': room_id,
                'room_name': room['room_name'],
                'is_owner': is_owner
            })
            logger.info(f"Sent room_joined event to user {session['user_id']}")

            # 广播用户加入消息
            emit('system_message', {
                'message': f"{user['nickname']} 加入了房间"
            }, room=str(room_id))
            logger.info(f"Broadcast join message for user {user['nickname']}")

        except Exception as e:
            logger.error(f"Error while joining room: {str(e)}", exc_info=True)
            emit('system_message', {'message': '加入房间失败，请重试'})
            return

    except Exception as e:
        logger.error(f"加入房间失败: {str(e)}", exc_info=True)
        emit('system_message', {'message': '加入房间失败，请重试'})

@socketio.on('leave_room')
def handle_leave_room(data):
    """处理离开房间事件"""
    try:
        if 'user_id' not in session:
            emit('system_message', {'message': '请先登录'})
            return

        room_id = data.get('room_id')
        if not room_id:
            emit('system_message', {'message': '房间ID不能为空'})
            return

        # 获取用户信息
        user = User.get_user_by_id(session['user_id'])
        if not user:
            emit('system_message', {'message': '用户不存在'})
            return

        # 离开Socket.io房间
        leave_room(str(room_id))

        # 广播用户离开消息
        emit('system_message', {
            'message': f"{user['nickname']} 离开了房间"
        }, room=str(room_id))

        # 发送离开成功消息
        emit('room_left', {'room_id': room_id})

    except Exception as e:
        logger.error(f"离开房间失败: {str(e)}", exc_info=True)
        emit('system_message', {'message': '离开房间失败，请重试'})

@socketio.on('message')
def handle_message(data):
    """处理聊天消息事件"""
    try:
        if 'user_id' not in session:
            logger.warning("User not logged in when trying to send message")
            emit('system_message', {'message': '请先登录'})
            return

        room_id = data.get('room_id')
        content = data.get('content')
        user_id = data.get('user_id')

        if not room_id or not content or not user_id:
            logger.warning("Missing required fields in message")
            emit('system_message', {'message': '消息内容或用户ID不能为空'})
            return

        logger.info(f"User {user_id} sending message to room {room_id}: {content}")

        # 获取用户信息
        user = User.get_user_by_id(user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            emit('system_message', {'message': '用户不存在'})
            return

        # 检查用户是否在房间中
        if not RoomMember.is_member(room_id, user_id):
            logger.warning(f"User {user_id} not in room {room_id}")
            emit('system_message', {'message': '您不在该房间中'})
            return

        # 保存消息到数据库
        try:
            message_id = Message.send_message(room_id, user_id, content)
            logger.info(f"Message saved with id: {message_id}")
        except Exception as e:
            logger.error(f"Failed to save message: {str(e)}", exc_info=True)
            emit('system_message', {'message': '消息保存失败'})
            return

        # 广播消息给房间内其他用户
        message_data = {
            'user_id': str(user_id),
            'nickname': user['nickname'],
            'content': content,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Broadcasting message to room {room_id}: {message_data}")
        emit('new_message', message_data, room=str(room_id))

    except Exception as e:
        logger.error(f"发送消息失败: {str(e)}", exc_info=True)
        emit('system_message', {'message': '发送消息失败，请重试'})

@socketio.on('submit_answer')
def on_submit_answer(data):
    """处理提交答案事件"""
    try:
        room_id = data['room_id']
        challenge_id = data['challenge_id']
        answer = data['answer']
        user_id = data['user_id']
        
        # 验证答案并广播结果
        result = WordChallenge.check_answer(challenge_id, answer)
        emit('answer_result', {
            'user_id': user_id,
            'correct': result['correct'],
            'message': result['message']
        }, room=room_id)
        
    except Exception as e:
        logger.error(f"提交答案失败: {str(e)}")
        emit('system_message', {'message': '提交答案失败'})