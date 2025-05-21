from flask import session
from flask_socketio import emit, join_room
import logging
import html  # 用于转义HTML字符
from datetime import datetime, timezone  # 导入datetime模块

from models.user_model import User
from models.room_member_model import RoomMember
from models.message_model import Message
from models.wordchallenge_models import WordChallenge

logger = logging.getLogger("WSChat")

# 定义常量以提高可维护性
KEY_ROOM_ID = 'room_id'
KEY_CONTENT = 'content'
KEY_USER_ID = 'user_id'

def emit_error(message, room=None):
    """封装错误响应逻辑"""
    emit('system_message', {'message': message}, room=room)

def register_chat_events(socketio):

    @socketio.on('message')
    def handle_message(data):
        try:
            # 提前提取必要字段，减少重复调用
            room_id = data.get(KEY_ROOM_ID)
            content = data.get(KEY_CONTENT)
            user_id = data.get(KEY_USER_ID)
            # --------------------------------加入房间命令，记得删除
            join_room(str(room_id))
            # # --------------------------------检查用户是否登录：记得恢复
            # if KEY_USER_ID not in session:
            #     emit_error('请先登录')
            #     return

            # 校验必要字段是否存在
            if not room_id or not content or not user_id:
                emit_error('消息内容或用户ID不能为空')
                return

            # 校验用户是否存在
            user = User.get_user_by_id(user_id)
            if not user:
                emit_error('用户不存在')
                return

            # 校验用户是否在房间内
            if not RoomMember.is_member(room_id, user_id):
                emit_error('您不在该房间中')
                return

            # 发送消息并检查返回值
            if not Message.send_message(room_id, user_id, content):
                emit_error('消息发送失败', room=str(room_id))
                return

            # 构造并发送新消息事件
            emit('new_message', {
                'user_id': str(user_id),
                'nickname': html.escape(user['nickname']),  # 转义防止 XSS 攻击
                'content': content,
                'avatar': user['avatar'] or '/default-avatar.jpg',  # 如果没有头像则使用默认头像
                'timestamp': datetime.now(tz=timezone.utc).isoformat()  # 替换为时区感知的时间
            }, room=str(room_id))

        except Exception as e:
            # 捕获异常并记录日志
            logger.error(f"处理消息时发生错误: {str(e)}")  # 使用 logger 替代 print
            emit_error('系统错误，请稍后再试', room=str(room_id))

    # @socketio.on('submit_answer')
    # def on_submit_answer(data):
    #     try:
    #         room_id = data['room_id']
    #         challenge_id = data['challenge_id']
    #         answer = data['answer']
    #         user_id = data['user_id']

    #         result = WordChallenge.check_answer(challenge_id, answer)
    #         emit('answer_result', {
    #             'user_id': user_id,
    #             'correct': result['correct'],
    #             'message': result['message']
    #         }, room=room_id)
    #     except Exception as e:
    #         logger.error(f"提交答案失败: {str(e)}")
    #         emit('system_message', {'message': '提交答案失败'})