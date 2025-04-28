from flask import Blueprint, request, jsonify
from models.Leaderboard_model import Leaderboard  # 导入 Leaderboard 类

# 创建蓝图
rankinglist_bp = Blueprint('rankinglist', __name__)

@rankinglist_bp.route('/update', methods=['POST'])
def update_score():
    """更新用户分数"""
    data = request.get_json()
    required_fields = ['room_id', 'user_id', 'score_delta']
    
    # 验证请求参数
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    # 调用 Leaderboard 方法
    success = Leaderboard.update_score(
        room_id=data['room_id'],
        user_id=data['user_id'],
        score_delta=data['score_delta']
    )
    
    return jsonify({"success": success}), 200 if success else 500

@rankinglist_bp.route('/<int:room_id>', methods=['GET'])
def get_room_leaderboard(room_id):
    """获取房间排行榜"""
    limit = request.args.get('limit', default=10, type=int)
    result = Leaderboard.get_room_leaderboard(room_id, limit)
    
    if result is None:
        return jsonify({"error": "Failed to fetch leaderboard"}), 500
    
    return jsonify({"leaderboard": result}), 200

@rankinglist_bp.route('/<int:room_id>/user/<int:user_id>', methods=['GET'])
def get_user_rank(room_id, user_id):
    """获取用户排名"""
    rank = Leaderboard.get_user_rank(room_id, user_id)
    
    if rank is None:
        return jsonify({"error": "User not found in leaderboard"}), 404
    
    return jsonify({"rank": rank}), 200

@rankinglist_bp.route('/<int:room_id>/reset', methods=['DELETE'])
def reset_leaderboard(room_id):
    """重置房间排行榜"""
    success = Leaderboard.reset_room_leaderboard(room_id)
    return jsonify({"success": success}), 200 if success else 500