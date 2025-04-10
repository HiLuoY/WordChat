from flask import Blueprint, request, jsonify, session
from models.room_model import Room
from models.room_member_model import RoomMember
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建蓝图
room_bp = Blueprint('rooms', __name__, url_prefix='/rooms')

@room_bp.route('', methods=['POST'])
def create_room():
    """创建新房间"""
    try:
        data = request.get_json()
        logger.info(f"Received create room request with data: {data}")
        
        if not data or 'room_name' not in data:
            logger.warning("Missing required parameters in create room request")
            return jsonify({'code': 400, 'message': '缺少必要参数'}), 400

        # 检查用户是否已登录
        if 'user_id' not in session:
            logger.warning("User not logged in when trying to create room")
            return jsonify({'code': 401, 'message': '请先登录'}), 401

        logger.info(f"Creating room with name: {data['room_name']}, owner_id: {session['user_id']}")

        # 检查用户是否存在
        try:
            from models.user_model import User
            user = User.get_user_by_id(session['user_id'])
            if not user:
                logger.error(f"User not found: {session['user_id']}")
                return jsonify({'code': 404, 'message': '用户不存在'}), 404
        except Exception as e:
            logger.error(f"Error checking user existence: {str(e)}", exc_info=True)
            return jsonify({'code': 500, 'message': '检查用户失败'}), 500

        # 创建房间
        try:
            room_id = Room.create_room(
                room_name=data['room_name'],
                owner_id=session['user_id'],
                password=data.get('password')
            )
            logger.info(f"Room created successfully with id: {room_id}")
        except ValueError as ve:
            logger.error(f"Value error while creating room: {str(ve)}")
            return jsonify({'code': 400, 'message': str(ve)}), 400
        except Exception as e:
            logger.error(f"Database error while creating room: {str(e)}", exc_info=True)
            return jsonify({'code': 500, 'message': '数据库操作失败'}), 500

        # 将房主添加到房间成员
        try:
            RoomMember.add_member(room_id, session['user_id'])
            logger.info(f"Added owner {session['user_id']} to room {room_id}")
        except Exception as e:
            logger.error(f"Failed to add owner to room: {str(e)}", exc_info=True)
            # 如果添加成员失败，删除已创建的房间
            Room.delete_room(room_id)
            return jsonify({'code': 500, 'message': '添加房主到房间失败'}), 500

        return jsonify({
            'code': 201,
            'message': '房间创建成功',
            'data': {
                'room_id': room_id,
                'room_name': data['room_name']
            }
        }), 201
    except Exception as e:
        logger.error(f"Unexpected error in create_room: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@room_bp.route('/<int:room_id>', methods=['GET'])
def get_room(room_id):
    """获取房间信息"""
    try:
        room = Room.get_room_by_id(room_id)
        if not room:
            return jsonify({'code': 404, 'message': '房间不存在'}), 404

        # 获取房间成员
        members = RoomMember.get_room_members(room_id)
        
        return jsonify({
            'code': 200,
            'data': {
                'room': room,
                'members': members
            }
        })
    except Exception as e:
        logger.error(f"获取房间信息失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@room_bp.route('/<int:room_id>/leave', methods=['POST'])
def leave_room(room_id):
    """离开房间"""
    try:
        # 检查用户是否已登录
        if 'user_id' not in session:
            return jsonify({'code': 401, 'message': '请先登录'}), 401

        # 检查用户是否是房主
        room = Room.get_room_by_id(room_id)
        if not room:
            return jsonify({'code': 404, 'message': '房间不存在'}), 404

        if room['owner_id'] == session['user_id']:
            # 房主离开，删除房间
            Room.delete_room(room_id)
            return jsonify({
                'code': 200,
                'message': '房间已删除'
            })
        else:
            # 普通成员离开
            RoomMember.remove_member(room_id, session['user_id'])
            return jsonify({
                'code': 200,
                'message': '已离开房间'
            })
    except Exception as e:
        logger.error(f"离开房间失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500 
    

    