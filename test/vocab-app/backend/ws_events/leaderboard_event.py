from flask import session
from flask_socketio import emit, join_room
from datetime import datetime
import threading
import time


from models.wordchallenge_models import WordChallenge
from models.challenge_attempts_model import ChallengeAttempt
from redis_utils import get_room_state, set_room_state, del_room_state
from models.room_model import Room
from models.room_member_model import RoomMember
from models.message_model import Message
from models.Leaderboard_model import Leaderboard
from models.user_model import User

import logging

# 创建日志器
logger = logging.getLogger("RankingSocket")
logger.setLevel(logging.DEBUG)  # 设置日志级别为 DEBUG

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# 创建文件处理器
file_handler = logging.FileHandler("ranking_socket.log")
file_handler.setLevel(logging.DEBUG)

# 创建日志格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 将处理器添加到日志器
logger.addHandler(console_handler)
logger.addHandler(file_handler)

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

        join_room(f"ranking_{room_id}")  # 使用专用房间频道
        logger.info(f"用户 {user_id} 加入排行榜房间 {room_id}")
        
        # 推送初始排行榜
        leaderboard = Leaderboard.get_room_leaderboard(room_id)
        
        if leaderboard:
            processed = [{
                'id': item[3],
                'nickname': item[0],
                'score': item[1],
                'avatar': item[4]  # 从数据库获取的头像URL
            } for item in leaderboard]
            emit('leaderboard_update', processed)
        logger.debug(f"初始排行榜查询结果: {leaderboard}")

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
            # 在 handle_score_submission 中添加
            logger.info(f"收到分数提交: 用户={user_id} 房间={room_id} 分数变化={score_delta}")
            time.sleep(0.5)
            # 更新分数
            if Leaderboard.update_score(room_id, user_id, score_delta):
                # 获取更新后的排行榜
                leaderboard = Leaderboard.get_room_leaderboard(room_id)
                # 在所有返回排行榜的地方使用这个结构
                processed = [{
                    'id': item[3],           # 用户ID -> 对应前端的 id
                    'nickname': item[0],         # 昵称 -> 对应前端的 name
                    'score': item[1],        # 分数
                    'avatar': item[4]        # 新增头像字段
                } for item in leaderboard]
                
                
                # 广播给房间内所有成员
                emit('leaderboard_update', processed, room=room_id)
                # 在 handle_score_submission 中添加
                logger.debug(f"更新前分数: {Leaderboard.get_user_score(room_id, user_id)}")
                logger.debug(f"更新后分数: {Leaderboard.get_user_score(room_id, user_id)}")
                logger.info(f"用户 {user_id} 提交分数变化: {score_delta}")
                logger.debug(f"更新后分数: {Leaderboard.get_user_score(room_id, user_id)}")
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
                    'id': item[3],
                    'nickname': item[0],
                    'score': item[1],
                    'avatar': item[4]  # 从数据库获取的头像URL
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

        # 打印接收到的请求数据
        logger.debug(f"接收到个人排名请求: 用户ID={user_id}, 房间ID={room_id}")

        try:
            # 检查用户是否已登录
            if not user_id:
                logger.warning(f"用户未登录，无法获取排名。请求数据: {data}")
                emit('error', {'code': 401, 'message': '未登录'})
                return

            # 检查房间ID是否有效
            if not room_id:
                logger.warning(f"房间ID无效或未提供。用户ID={user_id}, 请求数据: {data}")
                emit('error', {'code': 400, 'message': '无效的房间ID'})
                return

            # 获取用户排名
            rank = Leaderboard.get_user_rank(room_id, user_id)
            logger.debug(f"查询用户排名: 用户ID={user_id}, 房间ID={room_id}, 返回排名={rank}")

            if rank:
                # 如果获取到排名，发送排名数据
                emit('user_ranking', {'rank': rank})
                logger.info(f"用户 {user_id} 在房间 {room_id} 中的排名为 {rank}")
            else:
                # 如果未获取到排名，发送排名为 None
                emit('user_ranking', {'rank': None})
                logger.info(f"用户 {user_id} 在房间 {room_id} 中未上榜")

        except Exception as e:
            # 捕获异常并记录错误日志
            logger.error(f"获取用户排名失败: 用户ID={user_id}, 房间ID={room_id}, 错误信息={str(e)}")
            emit('error', {'code': 500, 'message': '获取排名失败'})


