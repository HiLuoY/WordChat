import requests
import socketio
import time
import json

# HTTP API测试
def test_http_api():
    base_url = 'http://localhost:5000'
    
    # 1. 创建房间
    print("创建房间...")
    room_response = requests.post(
        f'{base_url}/rooms',
        json={'name': '测试房间'}
    )
    room_id = room_response.json()['id']
    print(f"房间创建成功，ID: {room_id}")
    
    # 2. 创建单词
    print("\n创建单词...")
    word_response = requests.post(
        f'{base_url}/words',
        json={
            'word': 'test',
            'meaning': '测试',
            'hint': '这是一个测试单词'
        }
    )
    word_id = word_response.json()['id']
    print(f"单词创建成功，ID: {word_id}")
    
    # 3. 创建挑战
    print("\n创建挑战...")
    challenge_response = requests.post(
        f'{base_url}/challenges/create',
        json={
            'room_id': room_id,
            'word_id': word_id
        }
    )
    challenge_id = challenge_response.json()['data']['challenge_id']
    print(f"挑战创建成功，ID: {challenge_id}")
    
    return room_id, challenge_id

# WebSocket测试
def test_websocket(room_id, challenge_id):
    # 创建Socket.IO客户端
    sio = socketio.Client()
    
    @sio.event
    def connect():
        print('\n已连接到WebSocket服务器')
    
    @sio.event
    def disconnect():
        print('与WebSocket服务器断开连接')
    
    @sio.event
    def answer_result(data):
        print('收到答案结果:', json.dumps(data, ensure_ascii=False, indent=2))
    
    @sio.event
    def status(data):
        print('收到状态更新:', json.dumps(data, ensure_ascii=False, indent=2))
    
    try:
        # 连接到服务器
        sio.connect('http://localhost:5000')
        
        # 加入房间
        print(f"\n加入房间 {room_id}...")
        sio.emit('join', {'room_id': room_id})
        time.sleep(1)
        
        # 提交答案
        print("\n提交答案...")
        sio.emit('submit_answer', {
            'room_id': room_id,
            'challenge_id': challenge_id,
            'answer': 'test',
            'user_id': 1
        })
        
        # 等待结果
        time.sleep(2)
        
    finally:
        # 离开房间
        sio.emit('leave', {'room_id': room_id})
        sio.disconnect()

if __name__ == '__main__':
    print("开始测试单词挑战功能...")
    
    # 测试HTTP API
    room_id, challenge_id = test_http_api()
    
    # 测试WebSocket
    test_websocket(room_id, challenge_id)
    
    print("\n测试完成!") 