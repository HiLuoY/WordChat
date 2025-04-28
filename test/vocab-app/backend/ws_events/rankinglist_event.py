from flask import session
from flask_socketio import emit, join_room
from datetime import datetime
import threading
import time
import logging

from models.wordchallenge_models import WordChallenge
from models.challenge_attempts_model import ChallengeAttempt
from redis_utils import get_room_state, set_room_state, del_room_state
from models.room_model import Room
from models.room_member_model import RoomMember
from models.message_model import Message
from models.Leaderboard_model import Leaderboard

logger = logging.getLogger("RankingSocket")

def register_rankinglist_events(socketio):

    @socketio.on('join_ranking_room')
    def handle_join_ranking_room(data):
        """用户加入排行榜房间频道"""
        user_id = session.get('user_id')
        room_id = data.get('room_id')
        
        if not user_id:
            emit('error', {'code': 401, 'message': '未登录'})
            return

        if not RoomMember.is_member(room_id, user_id):
            emit('error', {'code': 403, 'message': '不在房间中'})
            return

        join_room(room_id)
        logger.info(f"用户 {user_id} 加入排行榜房间 {room_id}")
        
        # 推送初始排行榜
        leaderboard = Leaderboard.get_room_leaderboard(room_id)
        if leaderboard:
            processed = [{
                'nickname': item[0],
                'score': item[1],
                'updated_at': item[2].isoformat()
            } for item in leaderboard]
            emit('leaderboard_update', processed)

    @socketio.on('submit_score')
    def handle_score_submission(data):
        """处理分数提交事件"""
        user_id = session.get('user_id')
        room_id = data.get('room_id')
        score_delta = data.get('delta', 0)

        if not all([user_id, room_id, isinstance(score_delta, (int, float))]):
            emit('error', {'code': 400, 'message': '无效参数'})
            return

        try:
            # 验证房间成员身份
            if not RoomMember.is_member(room_id, user_id):
                emit('error', {'code': 403, 'message': '不在房间中'})
                return

            # 更新分数
            if Leaderboard.update_score(room_id, user_id, score_delta):
                # 获取更新后的排行榜
                leaderboard = Leaderboard.get_room_leaderboard(room_id)
                processed = [{
                    'nickname': item[0],
                    'score': item[1],
                    'updated_at': item[2].isoformat()
                } for item in leaderboard]
                
                # 广播给房间内所有成员
                emit('leaderboard_update', processed, room=room_id)
            else:
                emit('error', {'code': 500, 'message': '分数更新失败'})
        except Exception as e:
            logger.error(f"分数提交错误: {str(e)}")
            emit('error', {'code': 500, 'message': '服务器错误'})

    @socketio.on('request_leaderboard')
    def handle_leaderboard_request(data):
        """处理排行榜数据请求"""
        room_id = data.get('room_id')
        limit = data.get('limit', 10)

        try:
            leaderboard = Leaderboard.get_room_leaderboard(room_id, limit)
            if leaderboard:
                processed = [{
                    'nickname': item[0],
                    'score': item[1],
                    'updated_at': item[2].isoformat()
                } for item in leaderboard]
                emit('leaderboard_data', processed)
            else:
                emit('leaderboard_data', [])
        except Exception as e:
            logger.error(f"获取排行榜失败: {str(e)}")
            emit('error', {'code': 500, 'message': '获取排行榜失败'})

    @socketio.on('reset_leaderboard')
    def handle_leaderboard_reset(data):
        """处理排行榜重置请求"""
        user_id = session.get('user_id')
        room_id = data.get('room_id')

        try:
            # 验证房主身份
            room = Room.get_room(room_id)
            if room.creator_id != user_id:
                emit('error', {'code': 403, 'message': '无操作权限'})
                return

            if Leaderboard.reset_room_leaderboard(room_id):
                emit('leaderboard_update', [], room=room_id)
                logger.info(f"房间 {room_id} 排行榜已重置")
            else:
                emit('error', {'code': 500, 'message': '重置失败'})
        except Exception as e:
            logger.error(f"重置排行榜失败: {str(e)}")
            emit('error', {'code': 500, 'message': '重置失败'})

    @socketio.on('get_my_ranking')
    def handle_my_ranking_request(data):
        """处理个人排名请求"""
        user_id = session.get('user_id')
        room_id = data.get('room_id')

        try:
            rank = Leaderboard.get_user_rank(room_id, user_id)
            if rank:
                emit('user_ranking', {'rank': rank})
            else:
                emit('user_ranking', {'rank': None})
        except Exception as e:
            logger.error(f"获取用户排名失败: {str(e)}")
            emit('error', {'code': 500, 'message': '获取排名失败'})