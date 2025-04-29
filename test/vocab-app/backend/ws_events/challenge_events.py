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

            result = WordChallenge.check_answer(challenge_id,user_id, answer)
            #ChallengeAttempt.create_attempt(challenge_id, user_id, answer, result['correct'])

            if challenge_id not in state['current_answers']:
                state['current_answers'][challenge_id] = {}
            state['current_answers'][challenge_id][user_id] = result['correct']
            set_room_state(room_id, state)

            emit('answer_feedback', {
                "user_id": user_id,
                "mask": "***" if result['correct'] else answer,
                "correct": result['correct']
            }, room=str(room_id))

        except Exception as e:
            logger.error(f"提交答案失败: {str(e)}")
            emit('system_message', {'message': '提交答案失败'})

    