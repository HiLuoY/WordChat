from flask import session
from flask_socketio import emit
from datetime import datetime
import logging

from models.user_model import User
from models.room_member_model import RoomMember
from models.message_model import Message
from models.wordchallenge_models import WordChallenge

logger = logging.getLogger("WSChat")

def register_chat_events(socketio):

    @socketio.on('message')
    def handle_message(data):
        if 'user_id' not in session:
            emit('system_message', {'message': '请先登录'})
            return

        room_id = data.get('room_id')
        content = data.get('content')
        user_id = data.get('user_id')

        if not room_id or not content or not user_id:
            emit('system_message', {'message': '消息内容或用户ID不能为空'})
            return

        user = User.get_user_by_id(user_id)
        if not user:
            emit('system_message', {'message': '用户不存在'})
            return

        if not RoomMember.is_member(room_id, user_id):
            emit('system_message', {'message': '您不在该房间中'})
            return

        Message.send_message(room_id, user_id, content)

        emit('new_message', {
            'user_id': str(user_id),
            'nickname': user['nickname'],
            'content': content,
            'timestamp': datetime.utcnow().isoformat()
        }, room=str(room_id))

    @socketio.on('submit_answer')
    def on_submit_answer(data):
        try:
            room_id = data['room_id']
            challenge_id = data['challenge_id']
            answer = data['answer']
            user_id = data['user_id']

            result = WordChallenge.check_answer(challenge_id, answer)
            emit('answer_result', {
                'user_id': user_id,
                'correct': result['correct'],
                'message': result['message']
            }, room=room_id)
        except Exception as e:
            logger.error(f"提交答案失败: {str(e)}")
            emit('system_message', {'message': '提交答案失败'})
