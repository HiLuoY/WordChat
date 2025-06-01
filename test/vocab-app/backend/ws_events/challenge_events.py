from flask import session
from flask_socketio import emit,join_room
from datetime import datetime
import threading
import time
import logging
from flask import request

from models.wordchallenge_models import WordChallenge
from models.challenge_attempts_model import ChallengeAttempt
from redis_utils import get_room_state, set_room_state, del_room_state
from models.room_model import Room
from models.Leaderboard_model import Leaderboard


# 创建日志器
logger = logging.getLogger("your_logger_name")
logger.setLevel(logging.DEBUG)  # 设置日志级别为 DEBUG

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# 创建文件处理器
file_handler = logging.FileHandler("your_log_file.log")
file_handler.setLevel(logging.DEBUG)

# 创建日志格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 将处理器添加到日志器
logger.addHandler(console_handler)
logger.addHandler(file_handler)
def register_challenge_events(socketio):


    @socketio.on('submit_answer')
    def on_submit_answer(data):
        try:
            # === 1. 检查参数 ===
            room_id = data.get('room_id')
            user_id = data.get('user_id')
            answer = data.get('answer')
            nickname = data.get('nickname')
            avatar = data.get('avatar')
            if not all([room_id, user_id, answer]):
                logger.error("提交答案失败: 缺少必要参数")
                emit('system_message', {'message': '提交答案失败: 缺少必要参数'})
                return

            # === 2. 获取房间状态 ===
            state = get_room_state(room_id)
            if not state:
                logger.error(f"提交答案失败: 房间状态不存在 | room_id={room_id}")
                emit('system_message', {'message': '状态不存在'})
                return

            # === 3. 检查房间状态结构 ===
            if 'current_index' not in state or 'challenge_ids' not in state:
                logger.error(f"提交答案失败: 房间状态结构错误 | room_id={room_id} | state={state}")
                emit('system_message', {'message': '房间状态错误'})
                return

            current_index = state['current_index']
            challenge_ids = state['challenge_ids']

            # === 4. 检查当前索引和挑战ID ===
            if current_index >= len(challenge_ids):
                logger.error(f"提交答案失败: 当前索引超出范围 | room_id={room_id} | index={current_index} | total={len(challenge_ids)}")
                emit('system_message', {'message': '挑战已结束'})
                return

            challenge_id = challenge_ids[current_index]

            # === 5. 验证答案 ===
            result = WordChallenge.check_answer(challenge_id, user_id, answer)
            if not isinstance(result, dict) or 'correct' not in result:
                logger.error(f"提交答案失败: check_answer 返回值无效 | room_id={room_id} | challenge_id={challenge_id} | result={result}")
                emit('system_message', {'message': '答案验证失败'})
                return

            # === 6. 更新房间状态 ===
            if challenge_id not in state['current_answers']:
                state['current_answers'][challenge_id] = {}
            state['current_answers'][challenge_id][user_id] = result['correct']
            set_room_state(room_id, state)

            # === 7. 发送反馈 ===
            emit('answer_feedback', {
                "user_id": user_id,
                "mask": "***" if result['correct'] else answer,
                "correct": result['correct'],
                "nickname": nickname,
                "avatar": avatar
            }, room=str(room_id))

            # === 8. 更新分数 ===
            if result['correct']:
                Leaderboard.update_score(room_id, user_id, 10)

                # 广播排行榜更新
                leaderboard = Leaderboard.get_room_leaderboard(room_id, limit=10)
                socketio.emit('leaderboard_update', leaderboard, room=str(room_id))

                # 发送排名更新
                
                socketio.emit('update_all_rankings', {'room_id': room_id}, room=f"ranking_{room_id}")

        except Exception as e:
            logger.error(f"提交答案失败: {str(e)}", exc_info=True)
            emit('system_message', {'message': '提交答案失败'})