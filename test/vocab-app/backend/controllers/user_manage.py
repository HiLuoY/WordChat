from flask import Blueprint, jsonify, session, request
from models.user_model import  User
from werkzeug.security import generate_password_hash, check_password_hash
import logging


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

# ==================== 用户认证模块 ====================
@user_bp.route('/register', methods=['POST'])
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
    
@user_bp.route('/login', methods=['POST'])
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