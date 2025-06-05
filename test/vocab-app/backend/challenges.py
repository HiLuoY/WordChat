import random
from flask import Blueprint, request, jsonify, current_app,session
from models.wordchallenge_models import WordChallenge
from models.word_model import Word
from datetime import datetime
import logging
from flask_socketio import SocketIO,emit
from database.db_utils import query
import threading
import eventlet
from redis_utils import get_room_state, set_room_state, del_room_state
# 配置日志记录器
logger = logging.getLogger("challenge_logger")
logger.setLevel(logging.ERROR)  # 设置日志级别为ERROR
handler = logging.StreamHandler()  # 创建控制台输出处理器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # 定义日志格式
handler.setFormatter(formatter)
logger.addHandler(handler)  # 将处理器添加到日志记录器

challenge_api = Blueprint("challenge_api", __name__)

socketio = None  # 全局变量，用于存储SocketIO实例

def init_socketio(sio):
    global socketio
    socketio = sio
@challenge_api.route('/api/challenge/create', methods=['POST'])
def create_challenge():
    """创建新挑战（严格校验版）"""
    try:
        # ===== 1. 参数校验 =====
        data = request.get_json()
        logger.info(f"[挑战创建] 请求数据: {data}")
        
        if not data or 'room_id' not in data or 'num_words' not in data:
            logger.error("缺少必要参数: room_id 或 num_words")
            return jsonify({'code': 400, 'message': '参数不完整'}), 400

        # ===== 2. 类型转换 =====
        try:
            room_id = int(data['room_id'])
            num_words = int(data['num_words'])
        except ValueError as e:
            logger.error(f"参数类型错误: {e}")
            return jsonify({'code': 400, 'message': '参数需为整数'}), 400

        if num_words <= 0:
            logger.error("num_words 必须为正整数")
            return jsonify({'code': 400, 'message': 'num_words 必须为正整数'}), 400
        #---------------------------当注册登录，创建/加入房间弄好后记得恢复----------------------------
        # ===== 3. 会话验证 =====
        user_id = session.get('user_id')
        if not user_id:
             logger.error("用户未登录，session: %s", session)
             return jsonify({'code': 401, 'message': '请先登录'}), 401
        #记得删除
        #user_id = int(data['user_id'])

        # ===== 4. 权限验证 =====
        from models.room_model import Room
        room = Room.get_room_by_id(room_id)
        if not room:
            logger.error("房间不存在: room_id=%s", room_id)
            return jsonify({'code': 404, 'message': '房间不存在'}), 404

        if int(room['owner_id']) != user_id:
            logger.error("权限拒绝 | 房主ID: %s vs 当前用户: %s", room['owner_id'], user_id)
            return jsonify({'code': 403, 'message': '仅房主可创建挑战'}), 403

        # ===== 5. 获取单词库 =====
        all_words = Word.get_all_words()
        if len(all_words) < num_words:
            logger.error("单词库不足: 需要 %d 个单词，但只有 %d 个单词", num_words, len(all_words))
            return jsonify({'code': 400, 'message': '单词库不足'}), 400

        # ===== 6. 随机选取单词 =====
        selected_words = random.sample(all_words, num_words)
        word_ids = [word['id'] for word in selected_words]

        # ===== 7. 创建挑战 =====
        challenge_ids = []
        for i, word_id in enumerate(word_ids):
            challenge_id = WordChallenge.create_challenge(
                room_id=room_id,
                word_id=word_id,
                round_number=i + 1
            )
            challenge_ids.append(challenge_id)

        logger.info(f"[挑战创建] 成功创建 {len(challenge_ids)} 个挑战: {challenge_ids}")

        # 初始化房间状态
        room_state = {
            "challenge_ids": challenge_ids,
            "current_index": 0,
            "current_answers": {},
            "start_time": datetime.utcnow().isoformat(),
            "status": "playing"
        }
        set_room_state(room_id, room_state)
        # ===== 8. WebSocket通知 =====
        # try:
        #     # for i, challenge_id in enumerate(challenge_ids):
        #     send_word_and_answer(room_id, challenge_ids, 0)
        # except Exception as e:
        #     logger.error(f"WebSocket错误详情: {str(e)}", exc_info=True)
        # ===== 7. 异步启动挑战流程 =====
        socketio.start_background_task(
            start_challenge_async,
            room_id=room_id,
            challenge_ids=challenge_ids
        )
        return jsonify({
            'code': 201,
            'message': '挑战创建成功',
            'data': {
                'challenge_ids': challenge_ids,
                'num_words': num_words
            }
        }), 201
        
    except Exception as e:
        logger.error("全局异常: %s", str(e), exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

def start_challenge_async(room_id, challenge_ids):
    """异步启动挑战流程"""
    try:
        logger.info(f"[异步挑战] 开始挑战流程，房间ID: {room_id}")
        send_word_and_answer(room_id, challenge_ids, 0)
    except Exception as e:
        logger.error(f"[异步挑战] 发生错误: {str(e)}", exc_info=True)
        
def send_word_and_answer(room_id, challenge_ids, index=0):
        print(f"DEBUG: 准备发送 reveal_word，房间ID={room_id}")  # 调试日志
        if index >= len(challenge_ids):
            logger.info(f"[定时器] 所有单词已展示完毕，房间ID: {room_id}")
            # 发送挑战结束事件
            socketio.emit('challenge_end', room=str(room_id))
            # 清除房间状态
            del_room_state(room_id)
            return
        # 更新当前索引
        room_state = get_room_state(room_id)
        if room_state:
            room_state["current_index"] = index
            set_room_state(room_id, room_state)

        challenge_id = challenge_ids[index]
        word = WordChallenge.get_challenge_word(challenge_id)
        if word:
            # 广播单词释义
            print(f"DEBUG: 正在发送单词: {word['word']}")  # 调试日志
            socketio.emit('reveal_word', {
                'challenge_id': challenge_id,
                'word_meaning': word['meaning'],
                'display_time': 30  # 单词展示时间（秒）
            }, room=str(room_id))
            print(f"DEBUG: 已发送 reveal_word 事件到房间 {room_id}")  # 确认发送  
            logger.info(f"[定时器] 广播单词: {word['word']}，房间ID: {room_id}")

            # 设置单词展示时间
            socketio.sleep(15)
            print(f"DEBUG: socketio 单词展示恢复 事件在房间 {room_id}")  # 确认发送  
            send_answer(room_id, challenge_ids, index)
            
        else:
            logger.error(f"单词挑战不存在: {challenge_id}")


def send_answer(room_id, challenge_ids, index=0):
        challenge_id = challenge_ids[index]
        word = WordChallenge.get_challenge_word(challenge_id)
        if word:
            # 更新当前答案状态
            room_state = get_room_state(room_id)
            if room_state:
                room_state["current_word"] = word['word']
                set_room_state(room_id, room_state)
            # 广播答案
            socketio.emit('reveal_answer', {
                'challenge_id': challenge_id,
                'word': word['word'],
                'start_time': datetime.utcnow().isoformat(),
                'answer_time': 5  # 答案展示时间（秒）
            }, room=str(room_id))
            logger.info(f"[定时器] 广播答案: {word['word']}，房间ID: {room_id}")

            # 设置答案展示时间
            socketio.sleep(5)
            WordChallenge.finish_challenge(challenge_id)
            send_word_and_answer(room_id, challenge_ids, index + 1)
        else:
            logger.error(f"单词挑战不存在: {challenge_id}")