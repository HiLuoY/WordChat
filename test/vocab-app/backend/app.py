# ==================== 导入依赖 ====================
from flask import Flask, request, jsonify, session, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# 导入数据模型
from models.user_model import User
from models.room_model import Room
from models.message_model import Message
from models.room_member_model import RoomMember
from models.wordchallenge_models import WordChallenge  # 单词挑战模型
from models.word_model import Word  # 单词模型

# 导入控制器
from controllers.room_controller import room_bp  # 房间控制器
from challenges import challenge_bp  # 单词挑战蓝图

# ==================== 日志配置 ====================
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SocketIO")  # 全局日志记录器

# ==================== 应用初始化 ====================
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # 会话加密密钥
app.config['SESSION_TYPE'] = 'filesystem'  # 会话存储方式

# 初始化WebSocket
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# 注册蓝图
app.register_blueprint(room_bp)  # 注册房间相关路由
app.register_blueprint(challenge_bp)  # 注册单词挑战相关路由

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'code': 401, 'message': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ==================== 基础路由 ====================
@app.route('/')
def index():
    """首页"""
    return render_template('chat.html')

@app.route('/test')
def test():
    """测试页面路由"""
    return render_template('test.html')

@app.route('/upload')
def upload_page():
    """显示上传页面"""
    return render_template('upload.html')

# ==================== 用户认证模块 ====================
@app.route('/register', methods=['POST'])
def register():
    """用户注册
    请求体:
        email: 用户邮箱
        password: 用户密码
        nickname: 用户昵称
        avatar: 用户头像(可选)
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    nickname = data.get('nickname')
    avatar = data.get('avatar')

    if not email or not password or not nickname:
        return jsonify({'message': 'Missing arguments'}), 400

    try:
        # 密码哈希
        password_hash = generate_password_hash(password)
        # 创建用户
        user_id = User.create_user(email, password_hash, nickname, avatar)
        return jsonify({'message': 'User created successfully', 'user_id': user_id}), 201
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    
@app.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'code': 400, 'message': '缺少必要参数'}), 400

        user = User.get_user_by_email(data['email'])
        if not user or not check_password_hash(user['password_hash'], data['password']):
            return jsonify({'code': 401, 'message': '邮箱或密码错误'}), 401

        # 设置会话
        session['user_id'] = user['id']
        session.permanent = True

        return jsonify({
            'code': 200,
            'message': '登录成功',
            'data': {
                'id': user['id'],
                'nickname': user['nickname']
            }
        })
    except Exception as e:
        logger.error(f"登录失败: {str(e)}")
        return jsonify({'code': 500, 'message': '服务器内部错误'}), 500

# ==================== WebSocket事件处理 ====================
@socketio.on('connect')
def handle_connect():
    """处理客户端连接事件"""
    try:
        logger.info(f"客户端连接成功 | SID={request.sid}")
        emit('connection_response', {'status': 'connected'})
    except Exception as e:
        logger.error(f"连接事件处理失败: {str(e)}", exc_info=True)

@socketio.on('disconnect')
def handle_disconnect():
    """处理客户端断开连接事件（修正参数问题）"""
    try:
        logger.info(f"客户端断开连接 | SID={request.sid}")
    except Exception as e:
        logger.error(f"断开连接事件处理失败: {str(e)}", exc_info=True)

@socketio.on('join_room')
def handle_join_room(data):
    """处理加入房间事件（带错误回调）"""
    try:
        if 'user_id' not in session:
            logger.warning("未登录用户尝试加入房间")
            emit('system_message', {'message': '请先登录'})
            return {'error': '未登录用户'}, False  # 第二个参数是回调确认
        
        room_id = data.get('room_id')
        user_id = data.get('user_id')
        
        if not room_id or not user_id:
            logger.warning("缺少必要参数")
            emit('system_message', {'message': '房间ID和用户ID不能为空'})
            return {'error': '缺少必要参数'}, False
        
        # 验证用户ID是否匹配会话
        if str(session['user_id']) != str(user_id):
            logger.warning(f"会话用户ID不匹配: session={session['user_id']}, param={user_id}")
            emit('system_message', {'message': '用户身份验证失败'})
            return {'error': '用户身份验证失败'}, False
        
        logger.info(f"用户 {user_id} 尝试加入房间 {room_id}")
        
        # 获取房间信息
        room = Room.get_room_by_id(room_id)
        if not room:
            logger.warning(f"房间不存在: {room_id}")
            emit('system_message', {'message': '房间不存在'})
            return {'error': '房间不存在'}, False
        
        # 获取用户信息
        user = User.get_user_by_id(user_id)
        if not user:
            logger.error(f"用户不存在: {user_id}")
            emit('system_message', {'message': '用户不存在'})
            return {'error': '用户不存在'}, False
        
        try:
            # 添加房间成员
            if not RoomMember.is_member(room_id, user_id):
                RoomMember.add_member(room_id, user_id)
                logger.info(f"添加用户 {user_id} 到房间 {room_id}")
            
            # 加入Socket.io房间
            join_room(str(room_id))
            logger.info(f"用户 {user_id} 加入Socket房间 {room_id}")
            
            # 判断是否是房主
            is_owner = room['owner_id'] == user_id
            
            # 发送加入成功消息
            emit('room_joined', {
                'room_id': room_id,
                'room_name': room['room_name'],
                'is_owner': is_owner
            }, callback=lambda: logger.info(f"用户 {user_id} 收到房间加入确认"))
            
            # 广播用户加入消息
            emit('system_message', {
                'message': f"{user['nickname']} 加入了房间"
            }, room=str(room_id))
            
            return {'status': 'success'}, True
            
        except Exception as e:
            logger.error(f"加入房间时出错: {str(e)}", exc_info=True)
            emit('system_message', {'message': '加入房间失败'})
            return {'error': '服务器内部错误'}, False
            
    except Exception as e:
        logger.error(f"处理加入房间时发生异常: {str(e)}", exc_info=True)
        emit('system_message', {'message': '系统错误'})
        return {'error': '系统异常'}, False
@socketio.on('leave_room')
def handle_leave_room(data):
    """处理离开房间事件"""
    try:
        if 'user_id' not in session:
            emit('system_message', {'message': '请先登录'})
            return

        room_id = data.get('room_id')
        if not room_id:
            emit('system_message', {'message': '房间ID不能为空'})
            return

        # 获取用户信息
        user = User.get_user_by_id(session['user_id'])
        if not user:
            emit('system_message', {'message': '用户不存在'})
            return

        # 离开Socket.io房间
        leave_room(str(room_id))

        # 广播用户离开消息
        emit('system_message', {
            'message': f"{user['nickname']} 离开了房间"
        }, room=str(room_id))

        # 发送离开成功消息
        emit('room_left', {'room_id': room_id})

    except Exception as e:
        logger.error(f"离开房间失败: {str(e)}", exc_info=True)
        emit('system_message', {'message': '离开房间失败，请重试'})

@socketio.on('message')
def handle_message(data):
    """处理聊天消息事件"""
    try:
        if 'user_id' not in session:
            logger.warning("User not logged in when trying to send message")
            emit('system_message', {'message': '请先登录'})
            return

        room_id = data.get('room_id')
        content = data.get('content')
        user_id = data.get('user_id')

        if not room_id or not content or not user_id:
            logger.warning("Missing required fields in message")
            emit('system_message', {'message': '消息内容或用户ID不能为空'})
            return

        logger.info(f"User {user_id} sending message to room {room_id}: {content}")

        # 获取用户信息
        user = User.get_user_by_id(user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            emit('system_message', {'message': '用户不存在'})
            return

        # 检查用户是否在房间中
        if not RoomMember.is_member(room_id, user_id):
            logger.warning(f"User {user_id} not in room {room_id}")
            emit('system_message', {'message': '您不在该房间中'})
            return

        # 保存消息到数据库
        try:
            message_id = Message.send_message(room_id, user_id, content)
            logger.info(f"Message saved with id: {message_id}")
        except Exception as e:
            logger.error(f"Failed to save message: {str(e)}", exc_info=True)
            emit('system_message', {'message': '消息保存失败'})
            return

        # 广播消息给房间内其他用户
        message_data = {
            'user_id': str(user_id),
            'nickname': user['nickname'],
            'content': content,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Broadcasting message to room {room_id}: {message_data}")
        emit('new_message', message_data, room=str(room_id))

    except Exception as e:
        logger.error(f"发送消息失败: {str(e)}", exc_info=True)
        emit('system_message', {'message': '发送消息失败，请重试'})

@socketio.on('submit_answer')
def on_submit_answer(data):
    """处理提交答案事件"""
    try:
        room_id = data['room_id']
        challenge_id = data['challenge_id']
        answer = data['answer']
        user_id = data['user_id']
        
        # 验证答案并广播结果
        result = WordChallenge.check_answer(challenge_id, answer)
        emit('answer_result', {
            'user_id': user_id,
            'correct': result['correct'],
            'message': result['message']
        }, room=room_id)
        
    except Exception as e:
        logger.error(f"提交答案失败: {str(e)}")
        emit('system_message', {'message': '提交答案失败'})

# ==================== 应用启动 ====================
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)












