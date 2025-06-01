import datetime
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

    @socketio.on('get_all_rooms')
    def handle_get_all_rooms():
        """获取所有房间信息并进行展示（优化实时版本）"""
        try:
            # 获取所有基础房间信息（一次性查询提高效率）
            rooms = Room.get_all_rooms()
            if not rooms:
                emit('all_rooms_data', {'rooms': []})
                return
            # 构建响应数据
            room_list = []
            for room in rooms:
                has_password = room['password'] is not None  # 直接检查是否为None
                room_info = {
                    'id': room['id'],
                    'name': room['room_name'],
                    'has_password': has_password
                }
                room_list.append(room_info)

            emit('all_rooms_data', {
                'rooms': room_list
            },broadcast=True)
            
        except Exception as e:
            logger.error(f"获取所有房间信息失败: {str(e)}", exc_info=True)
            emit('system_message', {
                'code': 'ROOM_FETCH_ERROR',
                'message': '获取房间列表失败，请稍后重试'
            })
    @socketio.on('join_room')
    def handle_join_room(data):
        logger.info(f"尝试加入房间 | 用户session: {session} | 请求数据: {data}")
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
            logger.error(f"获取排行榜失败: room_id={room_id}")

        # 获取用户排名
        rank = Leaderboard.get_user_rank(room_id, user_id)
        if rank is not None:
            #socketio.emit('user_ranking', {'rank': rank}, room=request.sid)
            socketio.emit('user_ranking', 
                    {'user_id': user_id, 'rank': rank},
                    room=str(room_id))
        else:
            logger.error(f"获取用户排名失败: room_id={room_id}, user_id={user_id}")

        # 通知所有客户端更新房间列表
        handle_get_all_rooms()

    @socketio.on('leave_room')
    def handle_leave_room(data):
        logger.info(f"尝试退出房间 | 用户session: {session} | 请求数据: {data}")
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

        # 从房间成员中移除
        RoomMember.remove_member(room_id, session['user_id'])

        emit('system_message', {
            'message': f"{user['nickname']} 离开了房间"
        }, room=str(room_id))

        emit('room_left', {'room_id': room_id})

        # 如果是房主离开，解散房间
        room = Room.get_room_by_id(room_id)
        if room and room['owner_id'] == session['user_id']:
            Room.delete_room(room_id)
            emit('room_dismissed', {'room_id': room_id}, room=str(room_id))
            logger.info(f"房间 {room_id} 已被房主解散")

        # 通知所有客户端更新房间列表
        handle_get_all_rooms()

    @socketio.on('kick_member')
    def handle_kick_member(data):
        """房主踢人功能"""
        if 'user_id' not in session:
            emit('system_message', {'message': '请先登录'}, room=request.sid)
            return

        room_id = data.get('room_id')
        target_user_id = data.get('target_user_id')
        
        if not room_id or not target_user_id:
            emit('system_message', {'message': '缺少必要参数'}, room=request.sid)
            return

        # 获取房间信息
        room = Room.get_room_by_id(room_id)
        if not room:
            emit('system_message', {'message': '房间不存在'}, room=request.sid)
            return

        # 检查当前用户是否是房主
        if room['owner_id'] != session['user_id']:
            emit('system_message', {'message': '只有房主可以踢人'}, room=request.sid)
            return

        # 检查不能踢自己
        if target_user_id == session['user_id']:
            emit('system_message', {'message': '不能踢自己'}, room=request.sid)
            return

        # 检查目标用户是否在房间中
        if not RoomMember.is_member(room_id, target_user_id):
            emit('system_message', {'message': '目标用户不在房间中'}, room=request.sid)
            return

        # 获取目标用户信息
        target_user = User.get_user_by_id(target_user_id)
        if not target_user:
            emit('system_message', {'message': '目标用户不存在'}, room=request.sid)
            return

        # 执行踢人操作
        RoomMember.remove_member(room_id, target_user_id)
        
        # 通知被踢用户
        emit('kicked_from_room', {
            'room_id': room_id,
            'reason': '你已被房主移出房间'
        }, room=target_user_id)  # 假设用户的socket ID与user_id相关联

        # 通知房间其他成员
        emit('system_message', {
            'message': f"{target_user['nickname']} 已被房主移出房间"
        }, room=str(room_id))

        logger.info(f"用户 {target_user_id} 被房主 {session['user_id']} 从房间 {room_id} 踢出")

        # 更新排行榜（如果需要）
        leaderboard = Leaderboard.get_room_leaderboard(room_id, limit=10)
        if leaderboard is not None:
            socketio.emit('leaderboard_update', leaderboard, room=str(room_id))

        # 通知所有客户端更新房间列表
        handle_get_all_rooms()

        # WebSocket 事件处理器
    @socketio.on('create_room')
    def handle_create_room(data):
        try:
            # 1. 调用ORM层创建房间（包含业务逻辑验证）
            room_id = Room.create_room(
                room_name=data['room_name'],
                owner_id=data['user_id'],
                password=data.get('password')
            )
            # 获取更新后的完整房间列表
            updated_rooms = Room.get_all_rooms()
            formatted_rooms = [{
            'id': r['id'],
            'name': r['room_name'],
            'has_password': r['password'] is not None
            } for r in updated_rooms]
            # 2. 广播新房间给所有客户端
            new_room = {
                'id': room_id,
                'name': data['room_name'],
                'owner_id': data['user_id'],
                'has_password': bool(data.get('password'))
            }
            emit('room_created', new_room, room=request.sid) 
            # 2. 向所有人发送完整房间列表
            emit('all_rooms_data', {
                'rooms': formatted_rooms
            }, broadcast=True)
           
            
        except ValueError as e:
            emit('error', {'message': str(e)})  # 只返回给当前用户
        except Exception as e:
            logger.error(f"Room creation failed: {str(e)}")
            emit('error', {'message': '服务器错误'})