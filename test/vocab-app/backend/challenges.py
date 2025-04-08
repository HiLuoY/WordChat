from flask import Blueprint, request, jsonify
from models.wordchallenge_models import WordChallenge
from datetime import datetime
import logging

# 创建蓝图对象
challenge_bp = Blueprint('challenges', __name__, url_prefix='/challenges')
logger = logging.getLogger(__name__)

@challenge_bp.route('/create', methods=['POST'])
def create_challenge():
    """创建新单词挑战"""
    try:
        data = request.get_json()
        if not data or 'room_id' not in data or 'word_id' not in data:
            return jsonify({'code': 400, 'message': '缺少必要参数'}), 400

        challenge_id = WordChallenge.create_challenge(
            room_id=data['room_id'],
            word_id=data['word_id'],
            round_number=data.get('round_number', 1)
        )
        return jsonify({
            'code': 201,
            'message': '挑战创建成功',
            'data': {'challenge_id': challenge_id}
        }), 201
    except Exception as e:
        logger.error(f"创建挑战失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@challenge_bp.route('/<int:challenge_id>', methods=['GET'])
def get_challenge(challenge_id):
    """获取指定挑战详情"""
    try:
        challenge = WordChallenge.get_challenge_by_id(challenge_id)
        if not challenge:
            return jsonify({'code': 404, 'message': '挑战不存在'}), 404
            
        # 转换datetime对象为字符串
        challenge['started_at'] = challenge['started_at'].isoformat()  
        return jsonify({
            'code': 200,
            'data': challenge
        })
    except Exception as e:
        logger.error(f"获取挑战失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@challenge_bp.route('/current/<int:room_id>', methods=['GET'])
def get_current_challenge(room_id):
    """获取房间当前挑战"""
    try:
        challenge = WordChallenge.get_current_challenge(room_id)
        if not challenge:
            return jsonify({'code': 404, 'message': '当前没有进行中的挑战'}), 404
            
        challenge['started_at'] = challenge['started_at'].isoformat()
        return jsonify({
            'code': 200,
            'data': challenge
        })
    except Exception as e:
        logger.error(f"获取当前挑战失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@challenge_bp.route('/history/<int:room_id>', methods=['GET'])
def get_challenge_history(room_id):
    """获取房间挑战历史"""
    try:
        limit = request.args.get('limit', default=10, type=int)
        challenges = WordChallenge.get_challenges_by_room(room_id, limit)
        
        # 格式化时间字段
        for c in challenges:
            c['started_at'] = c['started_at'].isoformat()
            
        return jsonify({
            'code': 200,
            'data': {
                'total': len(challenges),
                'challenges': challenges
            }
        })
    except Exception as e:
        logger.error(f"获取挑战历史失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@challenge_bp.route('/<int:challenge_id>/status', methods=['PUT'])
def update_challenge_status(challenge_id):
    """更新挑战状态"""
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({'code': 400, 'message': '缺少状态参数'}), 400

        success = WordChallenge.update_challenge_status(
            challenge_id, 
            data['status']
        )
        return jsonify({
            'code': 200 if success else 400,
            'message': '状态更新成功' if success else '状态更新失败'
        })
    except ValueError as ve:
        return jsonify({'code': 400, 'message': str(ve)}), 400
    except Exception as e:
        logger.error(f"更新挑战状态失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@challenge_bp.route('/<int:challenge_id>/round', methods=['PUT'])
def increment_round(challenge_id):
    """增加挑战轮次"""
    try:
        success = WordChallenge.increment_round(challenge_id)
        return jsonify({
            'code': 200 if success else 400,
            'message': '轮次增加成功' if success else '轮次增加失败'
        })
    except Exception as e:
        logger.error(f"增加轮次失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@challenge_bp.route('/<int:challenge_id>/finish', methods=['PUT'])
def finish_challenge(challenge_id):
    """结束挑战"""
    try:
        success = WordChallenge.finish_challenge(challenge_id)
        return jsonify({
            'code': 200 if success else 400,
            'message': '挑战已结束' if success else '结束挑战失败'
        })
    except Exception as e:
        logger.error(f"结束挑战失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@challenge_bp.route('/<int:challenge_id>/word', methods=['GET'])
def get_challenge_word(challenge_id):
    """获取挑战对应的单词"""
    try:
        word = WordChallenge.get_challenge_word(challenge_id)
        if not word:
            return jsonify({'code': 404, 'message': '未找到相关单词'}), 404
            
        return jsonify({
            'code': 200,
            'data': word
        })
    except Exception as e:
        logger.error(f"获取挑战单词失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500 