from flask import Blueprint, jsonify, session
from models.message_model import Message
from models.room_member_model import RoomMember
import logging

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

@chat_bp.route('/history/<int:room_id>', methods=['GET'])
def get_history(room_id):
    """获取聊天历史(HTTP API)"""
    try:
        if 'user_id' not in session:
            return jsonify({'code': 401, 'message': 'Unauthorized'}), 401
            
        if not RoomMember.is_member(room_id, session['user_id']):
            return jsonify({'code': 403, 'message': 'Forbidden'}), 403

        messages = Message.get_messages_by_room(room_id)
        return jsonify({'code': 200, 'data': messages})
        
    except Exception as e:
        logging.error(f"Error fetching chat history: {str(e)}")
        return jsonify({'code': 500, 'message': 'Internal Server Error'}), 500