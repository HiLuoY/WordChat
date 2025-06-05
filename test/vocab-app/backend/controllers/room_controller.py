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