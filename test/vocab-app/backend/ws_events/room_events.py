from flask import request, session
from flask_socketio import emit, join_room, leave_room
import logging

from models.user_model import User
from models.room_model import Room
from models.room_member_model import RoomMember
from models.Leaderboard_model import Leaderboard

logger = logging.getLogger("WSRoom")

def register_room_events(socketio):

    @socketio.on('connect')
    def handle_connect():
        logger.info(f"客户端连接成功 | SID={request.sid}")
        emit('connection_response', {'status': 'connected'})

    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info(f"客户端断开连接 | SID={request.sid}")

    @socketio.on('join_room')
    def handle_join_room(data):
        if 'user_id' not in session:
            emit('system_message', {'message': '请先登录'})
            return

        room_id = data.get('room_id')
        if not room_id:
            emit('system_message', {'message': '房间ID不能为空'})
            return

        room = Room.get_room_by_id(room_id)
        if not room:
            emit('system_message', {'message': '房间不存在'})
            return

        user_id = session['user_id']
        user = User.get_user_by_id(user_id)
        if not user:
            emit('system_message', {'message': '用户不存在'})
            return

        if not RoomMember.is_member(room_id, user_id):
            RoomMember.add_member(room_id, user_id)

        join_room(str(room_id))

        emit('room_joined', {
            'room_id': room_id,
            'room_name': room['room_name'],
            'is_owner': room['owner_id'] == user_id
        })

        emit('system_message', {
            'message': f"{user['nickname']} 加入了房间"
        }, room=str(room_id))
        
        # 确保用户在排行榜中有记录
        if not Leaderboard.get_user_score(room_id, user_id):
            Leaderboard.initialize_user_score(room_id, user_id)

        # 获取排行榜数据
        leaderboard = Leaderboard.get_room_leaderboard(room_id, limit=10)
        if leaderboard is not None:
            socketio.emit('leaderboard_update', leaderboard, room=str(room_id))
        else:
            print(f"获取排行榜失败: room_id={room_id}")

        # 获取用户排名
        rank = Leaderboard.get_user_rank(room_id, user_id)
        if rank is not None:
            socketio.emit('user_ranking', {'rank': rank}, room=request.sid)
        else:
            print(f"获取用户排名失败: room_id={room_id}, user_id={user_id}")

    @socketio.on('leave_room')
    def handle_leave_room(data):
        if 'user_id' not in session:
            emit('system_message', {'message': '请先登录'})
            return

        room_id = data.get('room_id')
        if not room_id:
            emit('system_message', {'message': '房间ID不能为空'})
            return

        user = User.get_user_by_id(session['user_id'])
        if not user:
            emit('system_message', {'message': '用户不存在'})
            return

        leave_room(str(room_id))

        emit('system_message', {
            'message': f"{user['nickname']} 离开了房间"
        }, room=str(room_id))

        emit('room_left', {'room_id': room_id})
