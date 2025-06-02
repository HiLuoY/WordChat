import { check } from 'k6';
import { WebSocket } from 'k6/experimental/websockets';
import http from 'k6/http';  // 必须导入才能使用 http.get() 或 http.post()
export const options = {
  stages: [
    { duration: '1m', target: 50 },  // 1分钟内升至50用户
    { duration: '3m', target: 200 }, // 3分钟内升至200用户
    { duration: '1m', target: 0 },   // 逐步降载
  ],
  thresholds: {
    ws_session_duration: ['p(95)<500'], // 95%的WebSocket会话应在500ms内完成
  },
};

export default function () {
  // 1. 先进行HTTP登录
  const loginRes = http.post('http://localhost:5000/api/auth/login', JSON.stringify({
    email: `user${__VU}@test.com`,
    password: 'password123'
  }), {
    headers: { 'Content-Type': 'application/json' },
  });
  
  const userData = loginRes.json().data;
  
  // 2. 建立WebSocket连接
  const wsUrl = `ws://localhost:5000/?room_id=${userData.current_room}`;
  const ws = new WebSocket(wsUrl);
  
  ws.onopen = () => {
    // 加入房间
    ws.send(JSON.stringify({
      event: 'join_room',
      data: {
        room_id: userData.current_room,
        user_id: userData.user_id
      }
    }));
    
    // 模拟发送消息
    for (let i = 0; i < 10; i++) {
      ws.send(JSON.stringify({
        event: 'message',
        data: {
          room_id: userData.current_room,
          content: `测试消息${i}`,
          user_id: userData.user_id
        }
      }));
      
      // 随机提交答案
      if (Math.random() > 0.7) {
        ws.send(JSON.stringify({
          event: 'submit_answer',
          data: {
            room_id: userData.current_room,
            user_id: userData.user_id,
            answer: `answer${i}`,
            nickname: userData.nickname
          }
        }));
      }
      
      sleep(1);
    }
  };
  
  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    check(msg, {
      '收到有效响应': (m) => m.event !== undefined
    });
  };
  
  ws.onclose = () => {
    console.log(`VU ${__VU}: WebSocket连接关闭`);
  };
  
  sleep(10); // 保持连接10秒
  ws.close();
}