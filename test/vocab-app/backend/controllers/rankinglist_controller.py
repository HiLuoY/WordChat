from flask import Blueprint, request, jsonify
from models.Leaderboard_model import Leaderboard  # 导入 Leaderboard 类

# 创建蓝图
rankinglist_bp = Blueprint('rankinglist', __name__)

@rankinglist_bp.route('/update', methods=['POST'])
def update_score(room_id, user_id, delta):
    try:
        # 获取当前用户在房间中的分数
        user_score = Leaderboard.query.filter_by(room_id=room_id, user_id=user_id).first()
        
        if user_score:
            user_score.score += delta
        else:
            # 如果用户没有分数记录，创建一个新的记录
            new_score = Leaderboard(room_id=room_id, user_id=user_id, score=delta)
            db.session.add(new_score)
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"更新分数失败: {str(e)}")
        return False

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