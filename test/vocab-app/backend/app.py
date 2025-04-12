# ==================== 导入依赖 ====================
from flask import Flask, request, jsonify, session, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_cors import CORS


# 导入数据模型
# from models.user_model import User
# from models.room_model import Room
# from models.message_model import Message
# from models.room_member_model import RoomMember
# from models.wordchallenge_models import WordChallenge  # 单词挑战模型
# from models.word_model import Word  # 单词模型

# 导入控制器
from controllers.room_controller import room_bp  # 房间控制器
from challenges import challenge_bp  # 单词挑战蓝图
from controllers.user_manage import user_bp
from controllers.auth_controller import auth_bp  # 用户认证蓝图

from ws_events.chat_events import register_chat_events
from ws_events.room_events import register_room_events
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
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# 注册蓝图
app.register_blueprint(room_bp)  # 注册房间相关路由
app.register_blueprint(challenge_bp)  # 注册单词挑战相关路由
app.register_blueprint(user_bp)  #注册用户管理相关路由
app.register_blueprint(auth_bp)  # 用户注册认证路由

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

#--------------注册登录 -----------------



# --------------用户认证 -----------------




# --------------单词挑战 -----------------



#--------------房间聊天 -----------------






# ==================== WebSocket事件处理 ====================
register_room_events(socketio)
register_chat_events(socketio)
# ==================== 应用启动 ====================
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    












