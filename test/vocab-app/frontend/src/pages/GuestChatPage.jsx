import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaComments } from 'react-icons/fa';
import { io } from 'socket.io-client';
import Navbar from '../components/Navbar';
import RankingSidebar from '../components/RankingPanel';
import '../styles/ChatPage.css';

// 默认头像URL
const DEFAULT_AVATAR = '/default-avatar.jpg';

const GuestChatPage = () => {
  const navigate = useNavigate();
  
  // 从 localStorage 读取用户信息和房间信息
  const [userData, setUserData] = useState(() => {
    const savedUser = localStorage.getItem('userInfo');
    return savedUser ? JSON.parse(savedUser) : null;
  });

  const [roomInfo, setRoomInfo] = useState(() => {
    const savedRoom = localStorage.getItem('currentRoom');
    return savedRoom ? JSON.parse(savedRoom) : null;
  });

  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [socket, setSocket] = useState(null);
  const [roomId, setRoomId] = useState(roomInfo?.room_id || '');
  const [challenge, setChallenge] = useState(null);
  const [countdown, setCountdown] = useState(0);
  const [rankings, setRankings] = useState([]);
  const [userRank, setUserRank] = useState(null);
  const [systemPopup, setSystemPopup] = useState({ show: false, message: '' });

  // 消息自动滚动
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 显示系统弹窗
  const showSystemPopup = (message) => {
    setSystemPopup({ show: true, message });
    setTimeout(() => {
      setSystemPopup({ show: false, message: '' });
    }, 3000); // 3秒后自动关闭
  };

  // 初始化 Socket.IO 连接
  useEffect(() => {
    console.log('当前用户信息:', userData);
    if (!userData || !roomInfo) {
      navigate('/');
      return;
    }

    const socketInstance = io('http://localhost:5000', {
      withCredentials: true,
      transports: ['websocket'],
      query: { room_id: roomInfo.room_id }
    });

    setSocket(socketInstance);

    // Socket.IO 事件监听
    socketInstance.on('connect', () => {
      console.log('Socket.IO 连接已建立');
      socketInstance.emit('join_room', {
        room_id: roomInfo.room_id,
        user_id: userData.user_id
      });
    });

    socketInstance.on('room_joined', (data) => {
      console.log('成功加入房间:', data);
    });

    socketInstance.on('leaderboard_update', (data) => {
      console.log('收到排行榜更新:', data);
      const normalized = data.map(item => ({
        id: item.user_id,
        nickname: item.nickname || item.name, // 统一为name
        score: item.score,
        avatar: item.avatar
      }));
      setRankings(normalized);
    });

  // 监听个人排名更新（双保险）
  socketInstance.on('user_ranking', (data) => {
    if (data.user_id === userData.user_id) {
      setUserRank(data.rank);
    }
  });
  /*
    socketInstance.on('user_ranking', (data) => {
      console.log('收到用户排名:', data.rank);
      setUserRank(data.rank);
    });*/

    socketInstance.on('new_message', (data) => {
      setMessages(prev => [...prev, {
        content: data.content,
        sender: data.nickname,
        avatar: data.avatar || DEFAULT_AVATAR,
        isMe: data.user_id === userData.user_id,
        correct: data.correct
      }]);
    });

    socketInstance.on('reveal_word', (data) => {
      setChallenge({
        challengeId: data.challenge_id,
        meaning: data.word_meaning,
      });
      setCountdown(30);
      showSystemPopup('新单词挑战已开始！');
    });

    socketInstance.on('reveal_answer', (data) => {
      setChallenge(prev => ({
        ...prev,
        word: data.word,
      }));
      setCountdown(5);
    });

    socketInstance.on('challenge_end', () => {
      showSystemPopup('单词挑战已结束！');
      setChallenge(null);
      setCountdown(0);
    });

    socketInstance.on('answer_feedback', (data) => {
      setMessages(prev => [...prev, {
        content: data.mask,
        sender: data.nickname,
        avatar: data.avatar || DEFAULT_AVATAR,
        isMe: data.user_id === userData.user_id,
        correct: data.correct,
      }]);
    });
    // 在useEffect的socket事件监听部分添加：
    socketInstance.on('room_dismissed', () => {
      showSystemPopup('房主已解散房间');
      setTimeout(() => {
        localStorage.removeItem('currentRoom');
        navigate('/home');
      }, 2000); // 2秒后跳转
    });

    socketInstance.on('system_message', (data) => {
      showSystemPopup(data.message);
    });

    // 倒计时
    const timer = setInterval(() => {
      setCountdown(prev => prev > 0 ? prev - 1 : 0);
    }, 1000);

    return () => {
      clearInterval(timer);
      socketInstance.disconnect();
    };
  }, [userData, roomInfo, navigate]);

  // 发送消息
  const sendMessage = () => {
    if (!newMessage.trim() || !socket || !socket.connected || !userData || !roomInfo) return;

    if (challenge) {
      socket.emit('submit_answer', {
        room_id: roomInfo.room_id,
        user_id: userData.user_id,
        answer: newMessage.trim(),
        nickname: userData.nickname,
        avatar: userData.avatar || DEFAULT_AVATAR
      });
    } else {
      socket.emit('message', {
        room_id: roomInfo.room_id,
        content: newMessage.trim(),
        user_id: userData.user_id
      });
    }
    
    setNewMessage('');
    setTimeout(scrollToBottom, 0);
  };

  const scrollToBottom = () => {
    const messagesContainer = document.querySelector('.chat-content');
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  };

  const handleLeaveRoom = () => {
    if (socket && socket.connected && userData && roomInfo) {
      socket.emit('leave_room', {
        room_id: roomInfo.room_id,
        user_id: userData.user_id
      });
    }
    setTimeout(() => {
    localStorage.removeItem('currentRoom');
    navigate('/home');
  }, 500); // 添加延迟确保消息发送
  };

  return (
    <div className="chat-container">
      {/* 系统消息弹窗 */}
      {systemPopup.show && (
        <div className="system-popup">
          <div className="system-popup-content">
            {systemPopup.message}
          </div>
        </div>
      )}

      <Navbar
        onLeaveRoom={handleLeaveRoom}
        onEditProfile={() => navigate('/profile/edit')}
        showKickButton={false}
      />
      <div className="main-content-container">
        <RankingSidebar 
          rankings={rankings} 
          userRank={userRank}
          currentUserId={userData ? userData.user_id : null}  // 关键修复
        />
      
        <div className="chat-area">
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
              <div 
                key={index} 
                className={`message ${msg.isMe ? 'my-message' : ''} ${msg.correct ? 'correct-answer' : msg.correct === false ? 'wrong-answer' : ''}`}
              >
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
              </div>
            ))}
          </div>

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
      </div>
    </div>
  );
};

export default GuestChatPage;