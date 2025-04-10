# 这个文件使models目录成为一个Python包
# 导入所有模型，使它们可以直接从models包中导入
from .user_model import User
from .room_model import Room
from .message_model import Message
from .room_member_model import RoomMember
from .wordchallenge_models import WordChallenge
from .word_model import Word

__all__ = [
    'User',
    'Room',
    'Message',
    'RoomMember',
    'WordChallenge',
    'Word'
] 