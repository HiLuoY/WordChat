# ==================== 导入依赖 ====================
from flask import Flask, request, jsonify, session, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_cors import CORS
import eventlet

# 导入控制器
from controllers.room_controller import room_bp  # 房间控制器
from challenges import challenge_api,init_socketio # 单词挑战蓝图
from controllers.auth_controller import auth_bp  # 用户认证蓝图

from ws_events.chat_events import register_chat_events
from ws_events.room_events import register_room_events
from ws_events.challenge_events import register_challenge_events
# ==================== 日志配置 ====================
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SocketIO")  # 全局日志记录器

# ==================== 应用初始化 ====================
app = Flask(__name__)
CORS(app, supports_credentials=True)  # 支持携带 Cookie
app.secret_key = secrets.token_hex(32)
app.config['SESSION_TYPE'] = 'filesystem'

# 初始化WebSocket
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet',supports_credentials=True)
# 初始化SocketIO实例并传递给challenges_edit.py
init_socketio(socketio)
# 注册蓝图
app.register_blueprint(room_bp)  # 注册房间相关路由
app.register_blueprint(challenge_api)  # 注册单词挑战相关路由
app.register_blueprint(auth_bp)  # 用户注册认证路由

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'code': 401, 'message': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated_function


# ==================== WebSocket事件处理 ====================
register_room_events(socketio)
register_chat_events(socketio)
register_challenge_events(socketio)
# ==================== 应用启动 ====================
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    