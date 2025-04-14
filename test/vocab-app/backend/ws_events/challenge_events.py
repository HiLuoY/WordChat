from flask import session
from flask_socketio import emit,join_room
from datetime import datetime
import threading
import time
import logging

from models.wordchallenge_models import WordChallenge
from models.challenge_attempts_model import ChallengeAttempt
from redis_utils import get_room_state, set_room_state, del_room_state
from models.room_model import Room
logger = logging.getLogger("ChallengeSocket")

def register_challenge_events(socketio):

    @socketio.on('join')
    def on_join(data):
        try:
            logger.info(f"开始处理加入房间请求 | 房间={data['room_id']} 用户={data['user_id']}")
            room_id = int(data['room_id'])
            user_id = int(data['user_id'])
            session['user_id'] = user_id

            join_room(f"room_{room_id}")
            logger.info(f"用户已加入房间 | 房间=room_{room_id}")
            
            room = Room.get_room_by_id(room_id)
            is_owner = room and room['owner_id'] == user_id
            logger.info(f"房间查询结果 | 是否存在={room is not None} 房主={is_owner}")

            emit('room_joined', {
                'room_id': room_id,
                'is_owner': is_owner
            })
            logger.info(f"已发送room_joined事件 | 房间={room_id}")
            
        except Exception as e:
            logger.error(f"处理加入房间时出错: {str(e)}")
            emit('join_error', {'error': str(e)})

    @socketio.on('submit_answer')
    def on_submit_answer(data):
        try:
            room_id = data['room_id']
            user_id = data['user_id']
            answer = data['answer']
            state = get_room_state(room_id)
            
            if not state:
                emit('system_message', {'message': '状态不存在'})
                return

            current_index = state['current_index']
            challenge_id = state['challenge_ids'][current_index]

            result = WordChallenge.check_answer(challenge_id, answer)
            ChallengeAttempt.create_attempt(challenge_id, user_id, answer, result['correct'])

            if challenge_id not in state['current_answers']:
                state['current_answers'][challenge_id] = {}
            state['current_answers'][challenge_id][user_id] = result['correct']

            emit('answer_feedback', {
                "user_id": user_id,
                "mask": "***" if result['correct'] else answer,
                "correct": result['correct']
            }, room=f"room_{room_id}")

            if list(state['current_answers'][challenge_id].values()).count(True) >= 3:
                _reveal_and_next(room_id, state)
        except Exception as e:
            logger.error(f"提交答案失败: {str(e)}")
            emit('system_message', {'message': '提交答案失败'})

    @socketio.on('start_timer')
    def on_start_timer(data):
        try:
            logger.info(f"启动计时器 | 房间={data['room_id']}")
            socketio.start_background_task(
                safe_challenge_timer,
                room_id=data['room_id']
            )
        except Exception as e:
            logger.error(f"启动计时器失败: {str(e)}")
            emit('system_message', {'message': '无法启动计时'})
        
    def safe_challenge_timer(room_id):
        """带应用上下文的安全计时器"""
        try:
            # 获取当前应用实例（修正版）
            from flask import current_app
            
            # 方法1：直接使用current_app（推荐）
            with current_app.app_context():
                _challenge_timer(room_id)
                
            # 或者方法2：通过socketio获取app
            # with socketio.server.environ['flask.app'].app_context():
            #    _challenge_timer(room_id)
                
        except Exception as e:
            logger.error(f"安全计时器捕获错误: {str(e)}", exc_info=True)
            try:
                socketio.emit('system_message', 
                            {'message': '计时器错误'}, 
                            room=f"room_{room_id}")
            except:
                logger.critical("无法发送错误消息到前端")

    def _challenge_timer(room_id):
        try:
            time.sleep(10)  # 10秒计时
            
            state = get_room_state(room_id)
            if not state:
                logger.warning(f"房间状态不存在: {room_id}")
                return

            # 获取当前应用实例
            from flask import current_app
            with current_app.app_context():
                _reveal_and_next(room_id, state)
                
        except Exception as e:
            logger.error(f"计时器内部错误: {str(e)}", exc_info=True)
            raise  # 异常会由上层包装器捕获
    def _reveal_and_next(room_id, state):
        try:
            # 获取当前单词
            current_idx = state['current_index']
            challenge_id = state['challenge_ids'][current_idx]
            
            word = WordChallenge.get_challenge_word(challenge_id)
            if not word:
                raise ValueError(f"单词挑战不存在: {challenge_id}")

            # 发送揭示事件
            socketio.emit("reveal_word", {
                "word": word['word'],
                "meaning": word['meaning']
            }, room=f"room_{room_id}")

            time.sleep(2)  # 展示2秒

            # 检查是否结束
            if current_idx + 1 >= len(state['challenge_ids']):
                socketio.emit("challenge_end", {}, room=f"room_{room_id}")
                del_room_state(room_id)
                logger.info(f"挑战完成: 房间{room_id}")
            else:
                # 下一题
                state['current_index'] += 1
                set_room_state(room_id, state)
                socketio.emit("next_word", {
                    "challenge_id": state['challenge_ids'][state['current_index']]
                }, room=f"room_{room_id}")
                
        except Exception as e:
            logger.error(f"挑战流程错误: {str(e)}")
            socketio.emit('system_message', {
                'message': f'挑战出错: {str(e)}'
            }, room=f"room_{room_id}")
