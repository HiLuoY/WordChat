from flask import Blueprint, request, jsonify, session
from models.room_model import Room
from models.room_member_model import RoomMember
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建蓝图
room_bp = Blueprint('rooms', __name__, url_prefix='/rooms')

@room_bp.route('', methods=['GET'])
def get_all_rooms():
    """获取所有房间信息"""
    try:
        logger.info("Fetching all rooms information")
        
        # 获取所有房间基本信息
        rooms = Room.get_all_rooms()
        
        # 为每个房间添加成员信息
        for room in rooms:
            room['members'] = RoomMember.get_room_members(room['id'])
            # 不返回密码等敏感信息
            if 'password' in room:
                del room['password']
        
        return jsonify({
            'code': 200,
            'data': rooms
        })
    except Exception as e:
        logger.error(f"获取所有房间信息失败: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@room_bp.route('/<int:room_id>/join', methods=['POST'])
def join_room(room_id):
    """加入房间"""
    try:
        # 检查用户是否已登录
        if 'user_id' not in session:
            logger.warning("Unauthorized attempt to join room")
            return jsonify({'code': 401, 'message': '请先登录'}), 401

        data = request.get_json()
        password = data.get('password') if data else None
        
        # 检查房间是否存在
        room = Room.get_room_by_id(room_id)
        if not room:
            logger.warning(f"Room not found: {room_id}")
            return jsonify({'code': 404, 'message': '房间不存在'}), 404
        
        # 检查用户是否已在房间中
        if RoomMember.is_member(room_id, session['user_id']):
            logger.warning(f"User {session['user_id']} already in room {room_id}")
            return jsonify({'code': 400, 'message': '你已经在房间中'}), 400
        
        # 检查密码是否正确（如果房间有密码）
        if room.get('password') and room['password'] != password:
            logger.warning(f"Incorrect password for room {room_id}")
            return jsonify({'code': 403, 'message': '密码错误'}), 403
        
        # 添加用户到房间
        RoomMember.add_member(room_id, session['user_id'])
        logger.info(f"User {session['user_id']} joined room {room_id}")
        
        return jsonify({
            'code': 200,
            'message': '加入房间成功',
            'data': {
                'room_id': room_id,
                'room_name': room['room_name']
            }
        })
    except Exception as e:
        logger.error(f"加入房间失败: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@room_bp.route('/<int:room_id>/kick', methods=['POST'])
def kick_member(room_id):
    """房主踢人"""
    try:
        # 检查用户是否已登录
        if 'user_id' not in session:
            return jsonify({'code': 401, 'message': '请先登录'}), 401

        data = request.get_json()
        if not data or 'user_id' not in data:
            return jsonify({'code': 400, 'message': '缺少必要参数'}), 400

        target_user_id = data['user_id']
        
        # 检查房间是否存在
        room = Room.get_room_by_id(room_id)
        if not room:
            return jsonify({'code': 404, 'message': '房间不存在'}), 404
        
        # 检查当前用户是否是房主
        if room['owner_id'] != session['user_id']:
            return jsonify({'code': 403, 'message': '只有房主可以踢人'}), 403
        
        # 检查不能踢自己
        if target_user_id == session['user_id']:
            return jsonify({'code': 400, 'message': '不能踢自己'}), 400
        
        # 检查目标用户是否在房间中
        if not RoomMember.is_member(room_id, target_user_id):
            return jsonify({'code': 400, 'message': '目标用户不在房间中'}), 400
        
        # 踢出用户
        RoomMember.remove_member(room_id, target_user_id)
        logger.info(f"User {target_user_id} was kicked from room {room_id} by owner {session['user_id']}")
        
        return jsonify({
            'code': 200,
            'message': '踢出成员成功'
        })
    except Exception as e:
        logger.error(f"踢出成员失败: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@room_bp.route('/<int:room_id>/leave', methods=['POST'])
def leave_room(room_id):
    """离开房间"""
    try:
        # 检查用户是否已登录
        if 'user_id' not in session:
            return jsonify({'code': 401, 'message': '请先登录'}), 401

        # 检查房间是否存在
        room = Room.get_room_by_id(room_id)
        if not room:
            return jsonify({'code': 404, 'message': '房间不存在'}), 404

        # 检查用户是否在房间中
        if not RoomMember.is_member(room_id, session['user_id']):
            return jsonify({'code': 400, 'message': '你不在该房间中'}), 400

        if room['owner_id'] == session['user_id']:
            # 房主离开，删除房间
            Room.delete_room(room_id)
            logger.info(f"Room {room_id} deleted by owner {session['user_id']}")
            return jsonify({
                'code': 200,
                'message': '房间已删除'
            })
        else:
            # 普通成员离开
            RoomMember.remove_member(room_id, session['user_id'])
            logger.info(f"User {session['user_id']} left room {room_id}")
            return jsonify({
                'code': 200,
                'message': '已离开房间'
            })
    except Exception as e:
        logger.error(f"离开房间失败: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500
    
@room_bp.route('/check_owner/<int:room_id>', methods=['GET'])
def check_room_owner(room_id):
    """
    判断当前用户是否是特定房间的房主
    ---
    tags:
      - 房间管理
    parameters:
      - name: room_id
        in: path
        type: integer
        required: true
        description: 房间ID
    responses:
      200:
        description: 返回是否是房主的结果
        schema:
          type: object
          properties:
            is_owner:
              type: boolean
              description: 是否是房主
      401:
        description: 用户未登录
      500:
        description: 服务器内部错误
    """
    # 检查用户是否已登录
    logger.info(f"尝试判断是否为房主房间 | 用户session: {session} | 请求数据: {room_id}")
    if 'user_id' not in session:
        logger.warning("Unauthorized access attempt to check room ownership")
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session['user_id']
    logger.info(f"Checking ownership for room={room_id}, user={user_id}")

    try:
        # 使用Room类的静态方法判断是否是房主
        is_owner = Room.is_owner(room_id, user_id)
        
        # 记录结果
        logger.info(f"Ownership check result for room={room_id}, user={user_id}: {is_owner}")
        
        return jsonify({
            "is_owner": is_owner,
            "room_id": room_id,
            "user_id": user_id
        }), 200

    except Exception as e:
        logger.error(f"Error checking ownership for room={room_id}, user={user_id}: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500