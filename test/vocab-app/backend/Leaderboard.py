from flask import Blueprint, request, jsonify, session
from models.Leaderboard_model import Leaderboard


import logging

logger = logging.getLogger("leaderboard_logger")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

leaderboard_api = Blueprint("leaderboard_api", __name__)

@leaderboard_api.route('/api/score/update', methods=['POST'])
def update_user_score():
    data = request.get_json()
    room_id = data.get('room_id')
    user_id = session.get('user_id')

    if not room_id or not user_id:
        logger.error("缺少必要参数: room_id 或 user_id")
        return jsonify({'code': 400, 'message': '参数不完整'}), 400

    delta = data.get('delta', 0)
    Leaderboard.update_score(room_id, user_id, delta)

    return jsonify({'code': 200, 'message': '分数更新成功'}), 200

@leaderboard_api.route('/api/leaderboard/request', methods=['POST'])
def request_leaderboard():
    data = request.get_json()
    room_id = data.get('room_id')
    limit = data.get('limit', 10)

    if not room_id:
        logger.error("缺少必要参数: room_id")
        return jsonify({'code': 400, 'message': '参数不完整'}), 400

    leaderboard = Leaderboard.get_leaderboard(room_id, limit)
    return jsonify({
        'code': 200,
        'data': leaderboard
    }), 200

@leaderboard_api.route('/api/user/ranking', methods=['POST'])
def get_user_ranking_route():
    data = request.get_json()
    room_id = data.get('room_id')
    user_id = session.get('user_id')

    if not room_id or not user_id:
        logger.error("缺少必要参数: room_id 或 user_id")
        return jsonify({'code': 400, 'message': '参数不完整'}), 400

    rank = Leaderboard.get_user_ranking(room_id, user_id)
    return jsonify({
        'code': 200,
        'data': {'rank': rank}
    }), 200