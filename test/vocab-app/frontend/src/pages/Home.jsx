import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/Home.css';

const api = {
  get: (url) => axios.get(url, { withCredentials: true }),
  post: (url, data) => axios.post(url, data, { withCredentials: true })
};

const Home = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [roomId, setRoomId] = useState('');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  // 会话验证
  useEffect(() => {
    const verifySession = async () => {
      try {
        const { data } = await api.get('/api/auth/session');
        if (data.code === 200) {
          setUserData(data.data);
          localStorage.setItem('userInfo', JSON.stringify(data.data));
        } else {
          navigate('/');
        }
      } catch (err) {
        console.error('会话验证失败:', err);
        setError('无法获取用户信息');
        setTimeout(() => navigate('/'), 3000);
      } finally {
        setLoading(false);
      }
    };
    verifySession();
  }, [navigate]);

  // 退出登录
  const handleLogout = async () => {
    try {
      await api.post('/api/auth/logout');
      localStorage.removeItem('userInfo');
      navigate('/');
    } catch (err) {
      setError('注销失败，请检查网络连接');
    } finally {
      setIsDropdownOpen(false);
    }
  };

  // 房间操作
  const handleCreateRoom = async () => {
    try {
      const { data } = await api.post('/api/rooms/create');
      if (data.code === 201) {
        navigate(`/room/${data.data.roomId}`);
      }
    } catch (err) {
      setError('创建房间失败，请稍后重试');
    }
  };

  // 加入房间
  const handleJoinRoom = (e) => {
    e.preventDefault();
    if (!roomId.trim()) {
      setError('请输入有效的房间ID');
      return;
    }
    navigate(`/chatpage`);
  };

  if (loading) return (
    <div className="loading-container">
      <div className="spinner"></div>
      <p>正在加载用户信息...</p>
    </div>
  );

  return (
    <div className="page-container">
      {/* 导航栏 */}
      <nav className="app-navbar">
        <div className="nav-brand">单词对战平台</div>
        <div className="nav-links">
          <Link to="/home" className="nav-link active">首页</Link>
          <Link to="/chat" className="nav-link">聊天室</Link>
          <div className="user-menu-container">
            <img 
              src={userData?.avatar || '/default-avatar.jpg'}
              alt="用户头像"
              className="nav-avatar"
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            />
            {isDropdownOpen && (
              <div className="dropdown-menu">
                <div className="menu-item" onClick={() => navigate('/profile')}>
                  个人信息
                </div>
                <div className="menu-item" onClick={handleLogout}>
                  退出登录
                </div>
              </div>
            )}
          </div>
        </div>
      </nav>

      {/* 主内容区 */}
      <main className="home-container">
        {error && <div className="error-banner">{error}</div>}

        <div className="room-actions">
          {/* 创建房间区块 */}
          <div className="action-card create-room">
            <h2>创建新房间</h2>
            <p>发起一个全新的单词对战</p>
            <button 
              className="action-button primary"
              onClick={handleCreateRoom}
            >
              立即创建
            </button>
          </div>

          {/* 分割线 */}
          <div className="divider">
            <span>或</span>
          </div>

          {/* 加入房间区块 */}
          <form className="action-card join-room" onSubmit={handleJoinRoom}>
            <h2>加入已有房间</h2>
            <input
              type="text"
              placeholder="输入房间ID"
              value={roomId}
              onChange={(e) => setRoomId(e.target.value)}
              className="room-input"
            />
            <button 
              type="submit"
              className="action-button secondary"
            >
              加入房间
            </button>
          </form>
        </div>

        {/* 快速指引 */}
        <div className="quick-guide">
          <h3>如何开始？</h3>
          <div className="guide-steps">
            <div className="step">
              <div className="step-number">1</div>
              <p>创建新房间或输入已有房间ID</p>
            </div>
            <div className="step">
              <div className="step-number">2</div>
              <p>邀请好友加入对战</p>
            </div>
            <div className="step">
              <div className="step-number">3</div>
              <p>开始单词比拼竞赛</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Home;