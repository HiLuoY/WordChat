from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from models.user_model import User
import logging
from typing import Dict, Optional
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        required_fields = {'email', 'password', 'nickname'}
        
        # 验证必要字段
        if not data or not all(field in data for field in required_fields):
            return jsonify({'code': 400, 'message': 'Missing required fields: email, password, nickname'}), 400

        # 密码长度检查
        if len(data['password']) < 6:
            return jsonify({'code': 400, 'message': 'Password must be at least 6 characters'}), 400

        # 创建用户 (密码哈希在控制器层处理)
        try:
            hashed_password = generate_password_hash(data['password'])
            user_id = User.create_user(
                email=data['email'],
                password_hash=hashed_password,
                nickname=data['nickname'],
                avatar=data.get('avatar')  # 可选字段
            )
            
            # 自动登录
            session['user_id'] = user_id
            session['user_email'] = data['email']
            return jsonify({
                'code': 201,
                'message': 'Registration successful',
                'data': {
                    'user_id': user_id,
                    'nickname': data['nickname']
                }
            }), 201
            
        except ValueError as e:
            return jsonify({'code': 409, 'message': str(e)}), 409
            
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': 'Internal server error'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'code': 400, 'message': 'Email and password required'}), 400

        # 获取用户信息
        user = User.get_user_by_email(data['email'])
        
        # 验证用户存在且密码正确
        if not user or not check_password_hash(user['password_hash'], data['password']):
            return jsonify({'code': 401, 'message': 'Invalid email or password'}), 401

        # 更新会话
        session['user_id'] = user['id']
        session['user_email'] = user['email']
        logger.info(f"登录 | 用户session: {session} ")
        return jsonify({
            'code': 200,
            'message': 'Login successful',
            'data': {
                'user_id': user['id'],
                'nickname': user['nickname'],
                'avatar': user.get('avatar')
            }
        })

    except Exception as e:
        logger.error(f"Login failed: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': 'Internal server error'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户注销"""
    try:
        # 记录注销操作
        logger.info(f"注销 | 用户session: {session} ")
        user_id = session.get('user_id')
        if user_id:
            logger.info(f"User logging out: id={user_id}")
        
        session.clear()
        return jsonify({'code': 200, 'message': 'Logout successful'})
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': 'Internal server error'}), 500

@auth_bp.route('/session', methods=['GET'])
def check_session():
    """检查当前会话状态"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'code': 401, 'message': 'Not logged in'}), 401

        user = User.get_user_by_id(user_id)
        if not user:
            session.clear()
            return jsonify({'code': 404, 'message': 'User not found'}), 404

        return jsonify({
            'code': 200,
            'data': {
                'is_logged_in': True,
                'user_id': user['id'],
                'email': user['email'],
                'nickname': user['nickname'],
                'avatar': user.get('avatar')
            }
        })
    except Exception as e:
        logger.error(f"Session check failed: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': 'Internal server error'}), 500

@auth_bp.route('/password', methods=['PUT'])
def change_password():
    """修改密码"""
    try:
        if 'user_id' not in session:
            return jsonify({'code': 401, 'message': 'Not logged in'}), 401

        data = request.get_json()
        required_fields = {'old_password', 'new_password'}
        if not data or not all(field in data for field in required_fields):
            return jsonify({'code': 400, 'message': 'Old and new password required'}), 400

        # 验证新密码长度
        if len(data['new_password']) < 6:
            return jsonify({'code': 400, 'message': 'New password must be at least 6 characters'}), 400

        user = User.get_user_by_id(session['user_id'])
        if not user:
            session.clear()
            return jsonify({'code': 404, 'message': 'User not found'}), 404

        # 验证旧密码
        if not check_password_hash(user['password_hash'], data['old_password']):
            return jsonify({'code': 403, 'message': 'Incorrect old password'}), 403

        # 更新密码
        new_hashed_password = generate_password_hash(data['new_password'])
        User.update_user(user['id'], {'password_hash': new_hashed_password})
        
        return jsonify({'code': 200, 'message': 'Password updated successfully'})
    except Exception as e:
        logger.error(f"Password change failed: {str(e)}", exc_info=True)
        return jsonify({'code': 500, 'message': 'Internal server error'}), 500