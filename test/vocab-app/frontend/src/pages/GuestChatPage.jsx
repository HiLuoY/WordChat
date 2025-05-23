import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaComments } from 'react-icons/fa';
import { io } from 'socket.io-client';
import Navbar from '../components/Navbar';
import '../styles/ChatPage.css';

// 默认头像URL
const DEFAULT_AVATAR = '/default-avatar.jpg';

const GuestChatPage = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [socket, setSocket] = useState(null);
  const [roomId, setRoomId] = useState('1'); // 测试房间ID--记得删改
  const [challenge, setChallenge] = useState(null);
  const [countdown, setCountdown] = useState(0);

  // 初始化测试数据-----------记得删除..........
  useEffect(() => {
    // 设置测试用户信息----应该是在注册/登录时设置
    const TEST_USER = {
      userId: '2', // 普通用户ID
      nickname: 'GuestUser',
      avatar: '/default-avatar.jpg'
    };
    localStorage.setItem('userInfo', JSON.stringify(TEST_USER));
    localStorage.setItem('userAvatar', TEST_USER.avatar);
    localStorage.setItem('currentRoomId', roomId);

    // 设置一些测试消息
    setMessages([
      {
        content: '欢迎来到房间！',
        type: 'system'
      }
    ]);
  }, []);

  // 在useEffect中添加自动滚动逻辑
    useEffect(() => {
      scrollToBottom();
    }, [messages]); // 当消息更新时自动滚动到底部
  

  // 初始化 Socket.IO 连接
  useEffect(() => {
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
    const currentRoomId = localStorage.getItem('currentRoomId');
    setRoomId(currentRoomId);

    // 创建 Socket.IO 连接
    const socketInstance = io('http://localhost:5000', {
      withCredentials: true,
      transports: ['websocket']
    });

    setSocket(socketInstance);

    // Socket.IO 事件监听 (与房主版本相同)
    socketInstance.on('connect', () => {
      console.log('Socket.IO 连接已建立');
    });

    socketInstance.on('new_message', (data) => {
      setMessages(prev => [...prev, {
        content: data.content,
        sender: data.nickname,
        avatar: data.avatar || DEFAULT_AVATAR,
        isMe: data.user_id === userInfo.userId,
        correct: data.correct
      }]);
    });

    socketInstance.on('reveal_word', (data) => {
      setChallenge({
        challengeId: data.challenge_id,
        meaning: data.word_meaning,
      });
      setCountdown(30); // 设置30秒倒计时
    });

    socketInstance.on('reveal_answer', (data) => {
      setChallenge(prev => ({
        ...prev,
        word: data.word,
      }));
      setCountdown(5); // 设置5秒答案展示时间
    });

    socketInstance.on('challenge_end', () => {
      setMessages(prev => [...prev, {
        content: '单词挑战已结束！',
        type: 'system'
      }]);
      setChallenge(null);
      setCountdown(0);
    });

    socketInstance.on('answer_feedback', (data) => {
      setMessages(prev => [...prev, {
        content: data.mask,
        sender: userInfo.nickname,
        avatar: userInfo.avatar || DEFAULT_AVATAR,
        isMe: data.user_id === userInfo.userId,
        correct: data.correct,
      }]);
    });

    socketInstance.on('system_message', (data) => {
      setMessages(prev => [...prev, {
        content: data.message,
        type: 'system'
      }]);
    });

    // 倒计时效果
    const timer = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 0) return 0;
        return prev - 1;
      });
    }, 1000);

    return () => {
      clearInterval(timer);
      socketInstance.disconnect();
    };
  }, []);

  // 发送消息（处理普通消息和答案）
  const sendMessage = () => {
    if (newMessage.trim() && socket && socket.connected) {
      const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
      
      if (challenge) {
        // 如果在挑战中，发送答案
        socket.emit('submit_answer', {
          room_id: roomId,
          user_id: userInfo.userId,
          answer: newMessage.trim()
        });
      } else {
        // 普通消息
        socket.emit('message', {
          room_id: roomId,
          content: newMessage.trim(),
          user_id: userInfo.userId
        });
      }
      
      setNewMessage('');
      // 关键：滚动到底部（使用 setTimeout 确保 DOM 更新完成）
      setTimeout(() => {
        scrollToBottom();
      }, 0);
    }
  };

  // 修改滚动函数
  const scrollToBottom = () => {
    const messagesContainer = document.querySelector('.chat-content');
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  };

  // 处理离开房间
  const handleLeaveRoom = () => {
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}');
    
    if (socket && socket.connected) {
      socket.emit('leave_room', {
        room_id: roomId,
        user_id: userInfo.userId
      });
    }
    
    localStorage.removeItem('currentRoomId');
    navigate('/lobby');
  };

  return (
    <div className="chat-container">
      <Navbar
        onLeaveRoom={handleLeaveRoom}
        onShowRanking={() => navigate('/ranking')}
        onEditProfile={() => navigate('/profile/edit')}
        showKickButton={false}   // 隐藏踢人按钮
      />

      {/* 聊天内容区域 */}
      <div className="chat-content">
        {challenge && (
          <div className="challenge-display">
            <div className="challenge-meaning">{challenge.meaning}</div>
            {countdown > 0 && (
              <div className="challenge-countdown">{countdown}秒</div>
            )}
            {challenge.word && (
              <div className="challenge-answer">{challenge.word}</div>
            )}
          </div>
        )}
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.type === 'system' ? 'system-message' : msg.isMe ? 'my-message' : ''} ${msg.correct !== undefined ? (msg.correct ? 'correct-answer' : 'wrong-answer') : ''}`}>
            {msg.type !== 'system' && (
              <div className="message-sender">
                <div className="avatar-container">
                  <img 
                    src={msg.avatar || DEFAULT_AVATAR}
                    alt={`${msg.sender}的头像`}
                    className="message-avatar"
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.src = DEFAULT_AVATAR;
                    }}
                  />
                  <span className="sender-name">{msg.sender}</span>
                </div>
                <div className="message-content">{msg.content}</div>
              </div>
            )}
            {msg.type === 'system' && (
              <div className="message-content">{msg.content}</div>
            )}
          </div>
        ))}
      </div>

      {/* 消息输入框（没有挑战按钮） */}
      <div className="message-input-container">
        <div className="message-input-wrapper">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder={challenge ? "请输入答案..." : "输入消息..."}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          />
          <button onClick={sendMessage} className="send-button">
            <FaComments />
          </button>
        </div>
      </div>
    </div>
  );
};

export default GuestChatPage;