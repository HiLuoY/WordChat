from flask import Blueprint, request, jsonify
from models.wordchallenge_models import WordChallenge
from models.word_model import Word
from datetime import datetime
import logging
from flask_socketio import emit
from flask import session

# 创建蓝图对象
challenge_bp = Blueprint('challenges', __name__, url_prefix='/challenges')
logger = logging.getLogger(__name__)

@challenge_bp.route('/words', methods=['GET'])
def get_words():
    """获取所有单词列表"""
    try:
        logger.info('开始获取单词列表')
        words = Word.get_all_words()
        logger.info(f'成功获取到 {len(words)} 个单词')
        return jsonify({
            'status': 'success',
            'words': words
        })
    except Exception as e:
        logger.error(f'获取单词列表失败: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': '获取单词列表失败'
        }), 500

'''
@challenge_bp.route('/create', methods=['POST'])
def create_challenge():
    """创建新挑战（增强版）"""
    try:
        # ========== 1. 参数验证 ==========
        data = request.get_json()
        logger.info(f"[挑战创建] 原始请求数据: {data}")

        if not data or 'room_id' not in data or 'word_id' not in data:
            logger.error("[挑战创建] 缺少必要参数")
            return jsonify({'code': 400, 'message': '缺少room_id或word_id'}), 400

        # 强制类型转换
        try:
            room_id = int(data['room_id'])
            word_id = int(data['word_id'])
        except ValueError as e:
            logger.error(f"[挑战创建] 参数类型错误: {e}")
            return jsonify({'code': 400, 'message': 'room_id和word_id必须是整数'}), 400

        logger.info(f"[挑战创建] 转换后参数: room_id={room_id}, word_id={word_id}")

        # ========== 2. 会话验证 ==========
        user_id = session.get('user_id')
        if not user_id:
            logger.error("[挑战创建] 用户未登录，当前session: %s", session)
            return jsonify({'code': 401, 'message': '请先登录'}), 401

        # ========== 3. 权限验证 ==========
        from models.room_model import Room
        room = Room.get_room_by_id(room_id)
        if not room:
            logger.error("[挑战创建] 房间不存在: room_id=%s", room_id)
            return jsonify({'code': 404, 'message': '房间不存在'}), 404

        if int(room['owner_id']) != int(user_id):
            logger.error(
                "[挑战创建] 权限拒绝 | 房主ID: %s | 当前用户ID: %s",
                room['owner_id'],
                user_id
            )
            return jsonify({'code': 403, 'message': '只有房主可以创建挑战'}), 403

        # ========== 4. 数据验证 ==========
        word = Word.get_word_by_id(word_id)
        if not word:
            logger.error("[挑战创建] 单词不存在: word_id=%s", word_id)
            return jsonify({'code': 404, 'message': '单词不存在'}), 404

        # ========== 5. 创建挑战 ==========
        logger.info("[挑战创建] 开始创建挑战...")
        challenge_id = WordChallenge.create_challenge(
            room_id=room_id,
            word_id=word_id,
            round_number=data.get('round_number', 1)
        )

        if not challenge_id:
            logger.error("[挑战创建] 数据库插入失败")
            return jsonify({'code': 500, 'message': '创建挑战失败'}), 500

        logger.info("[挑战创建] 挑战创建成功: challenge_id=%s", challenge_id)

        # ========== 6. WebSocket通知 ==========
        try:
            emit('challenge_created', {
                'challenge_id': challenge_id,
                'word_meaning': word['meaning'],
                'start_time': datetime.utcnow().isoformat()
            }, room=str(room_id), namespace='/')
        except Exception as e:
            logger.error("[挑战创建] WebSocket通知失败: %s", str(e))

        return jsonify({
            'code': 201,
            'message': '挑战创建成功',
            'data': {
                'challenge_id': challenge_id,
                'word': word['word']
            }
        }), 201

    except Exception as e:
        logger.error("[挑战创建] 全局异常: %s", str(e), exc_info=True)
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500
'''

@challenge_bp.route('/create', methods=['POST'])
def create_challenge():
    """创建新挑战（严格校验版）"""
    try:
        # ===== 1. 参数校验 =====
        data = request.get_json()
        logger.info(f"[挑战创建] 请求数据: {data}")
        
        if not data or 'room_id' not in data or 'word_id' not in data:
            logger.error("缺少必要参数: room_id 或 word_id")
            return jsonify({'code': 400, 'message': '参数不完整'}), 400

        # ===== 2. 类型转换 =====
        try:
            room_id = int(data['room_id'])
            word_id = int(data['word_id'])
        except ValueError as e:
            logger.error(f"参数类型错误: {e}")
            return jsonify({'code': 400, 'message': '参数需为整数'}), 400

        # ===== 3. 会话验证 =====
        user_id = session.get('user_id')
        if not user_id:
            logger.error("用户未登录，session: %s", session)
            return jsonify({'code': 401, 'message': '请先登录'}), 401

        # ===== 4. 权限验证 =====
        from models.room_model import Room
        room = Room.get_room_by_id(room_id)
        if not room:
            logger.error("房间不存在: room_id=%s", room_id)
            return jsonify({'code': 404, 'message': '房间不存在'}), 404

        if int(room['owner_id']) != user_id:
            logger.error("权限拒绝 | 房主ID: %s vs 当前用户: %s", room['owner_id'], user_id)
            return jsonify({'code': 403, 'message': '仅房主可创建挑战'}), 403

        # ===== 5. 单词验证 =====
        word = Word.get_word_by_id(word_id)
        if not word:
            logger.error("单词不存在: word_id=%s", word_id)
            return jsonify({'code': 404, 'message': '单词不存在'}), 404
        logger.info("验证通过，开始创建挑战...")

        # ===== 6. 创建挑战 =====
        challenge_id = WordChallenge.create_challenge(
            room_id=room_id,
            word_id=word_id,
            round_number=data.get('round_number', 1)
        )
        if not challenge_id:
            logger.error("数据库插入失败")
            return jsonify({'code': 500, 'message': '挑战创建失败'}), 500

        # ===== 7. WebSocket通知 =====
        # 修改WebSocket通知部分代码
        try:
            correct_meaning = word['meaning']
            logger.info(f"[WebSocket消息验证] 发送内容: {correct_meaning}")  # 新增关键日志
            
            emit('challenge_created', {
                'challenge_id': challenge_id,
                'word_meaning': correct_meaning,  # 确保使用确定字段
                'start_time': datetime.utcnow().isoformat()
            }, room=str(room_id), namespace='/')
        except Exception as e:
            logger.error(f"WebSocket错误详情: {str(e)}", exc_info=True)

        return jsonify({
            'code': 201,
            'message': '挑战创建成功',
            'data': {
                'challenge_id': challenge_id,
                'word': word['word'],
                'meaning': word.get('definition', '')  # 返回字段供调试
            }
        }), 201

    except Exception as e:
        logger.error("全局异常: %s", str(e), exc_info=True)
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

@challenge_bp.route('/word', methods=['POST'])
def create_word():
    """创建新单词"""
    try:
        data = request.get_json()
        if not data or 'word' not in data or 'meaning' not in data:
            return jsonify({'code': 400, 'message': '缺少必要参数'}), 400

        word_id = Word.create_word(
            word=data['word'],
            meaning=data['meaning'],
            hint=data.get('hint')  # 使用 get 方法安全获取，可能为 None
        )
        return jsonify({
            'code': 201,
            'message': '单词创建成功',
            'data': {'word_id': word_id}
        }), 201
    except Exception as e:
        logger.error(f"创建单词失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@challenge_bp.route('/current/<int:room_id>/answer', methods=['POST'])
def submit_answer(room_id):
    """提交答案"""
    try:
        data = request.get_json()
        if not data or 'answer' not in data:
            return jsonify({'code': 400, 'message': '缺少答案参数'}), 400

        # 获取当前挑战
        challenge = WordChallenge.get_current_challenge(room_id)
        if not challenge:
            return jsonify({'code': 404, 'message': '当前没有进行中的挑战'}), 404

        # 验证答案
        result = WordChallenge.check_answer(challenge['id'], data['answer'])
        return jsonify({
            'code': 200,
            'data': result
        })
    except Exception as e:
        logger.error(f"提交答案失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

@challenge_bp.route('/import', methods=['POST'])
def import_words():
    """导入单词"""
    try:
        if 'file' not in request.files:
            logger.error("没有上传文件")
            return jsonify({'code': 400, 'message': '请选择要上传的文件'}), 400
            
        file = request.files['file']
        if not file.filename.endswith('.csv'):
            logger.error("不支持的文件类型")
            return jsonify({'code': 400, 'message': '只支持CSV文件'}), 400
            
        # 清空现有单词表
        try:
            logger.info("开始清空单词表...")
            # 先检查单词表是否存在
            check_table_sql = "SHOW TABLES LIKE 'words'"
            from database.db_utils import query
            tables = query(check_table_sql)
            if not tables:
                logger.error("单词表不存在")
                return jsonify({'code': 500, 'message': '单词表不存在'}), 500
                
            # 获取当前单词数量
            count_sql = "SELECT COUNT(*) as count FROM words"
            result = query(count_sql)
            current_count = result[0]['count']
            logger.info(f"当前单词表中有 {current_count} 个单词")
            
            # 先删除wordchallenges表中的记录
            delete_challenges_sql = "DELETE FROM wordchallenges"
            from database.db_utils import delete
            delete(delete_challenges_sql)
            logger.info("已删除wordchallenges表中的记录")
            
            # 然后清空单词表
            delete_words_sql = "DELETE FROM words"
            delete(delete_words_sql)
            logger.info("单词表已清空")
        except Exception as e:
            logger.error(f"清空单词表失败: {str(e)}", exc_info=True)
            return jsonify({'code': 500, 'message': f'清空单词表失败: {str(e)}'}), 500
            
        # 读取CSV文件
        import csv
        import io
        content = file.stream.read().decode("UTF8")
        stream = io.StringIO(content, newline=None)
        
        # 使用csv.reader而不是DictReader，因为我们不需要列名
        csv_reader = csv.reader(stream)
        
        # 导入单词
        success_count = 0
        for row in csv_reader:
            try:
                if len(row) < 2:  # 确保至少有两个字段
                    logger.warning(f"跳过无效行: {row}")
                    continue
                    
                word = row[0].strip()
                meaning = row[1].strip()
                
                if not word or not meaning:
                    logger.warning(f"跳过无效行: word={word}, meaning={meaning}")
                    continue
                    
                Word.create_word(word, meaning)
                success_count += 1
                logger.info(f"成功导入单词: {word}")
            except Exception as e:
                logger.error(f"导入单词失败: {str(e)}")
                continue
                
        if success_count == 0:
            logger.error("没有成功导入任何单词")
            return jsonify({'code': 400, 'message': '没有成功导入任何单词'}), 400
            
        logger.info(f"成功导入 {success_count} 个单词")
        return jsonify({
            'code': 200,
            'message': f'成功导入 {success_count} 个单词'
        })
    except Exception as e:
        logger.error(f"导入单词失败: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': f'导入单词失败: {str(e)}'}), 500 