import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import io from 'socket.io-client';
import '../styles/Home.css';
import api from './api';

const Home = () => {
  const navigate = useNavigate();
  const [socket, setSocket] = useState(null);
  const [userData, setUserData] = useState(() => {
    const savedUser = localStorage.getItem('userInfo');
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [rooms, setRooms] = useState([]);
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [passwordInput, setPasswordInput] = useState('');
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  
  // 新增状态：创建房间弹窗
  const [showCreateRoomModal, setShowCreateRoomModal] = useState(false);
  const [newRoomName, setNewRoomName] = useState('');
  const [newRoomPassword, setNewRoomPassword] = useState('');
  
  // 新增状态：个人信息修改弹窗
  const [showEditProfileModal, setShowEditProfileModal] = useState(false);
  const [editFormData, setEditFormData] = useState({
    email: '',
    newPassword: '',
    confirmPassword: ''
  });
  
  // 在组件顶部添加状态
  const [currentPage, setCurrentPage] = useState(0);
  const roomsPerPage = 36; // 6行×6列

  // 计算当前页的房间
  const getCurrentPageRooms = () => {
    const start = currentPage * roomsPerPage;
    const end = start + roomsPerPage;
    return rooms.slice(start, end);
  };

  // 计算总页数
  const totalPages = Math.ceil(rooms.length / roomsPerPage);

  // 处理翻页
  const handlePageChange = (newPage) => {
    if (newPage >= 0 && newPage < totalPages) {
      setCurrentPage(newPage);
    }
  };

  // 处理编辑表单变化
  const handleEditFormChange = (e) => {
    const { name, value } = e.target;
    setEditFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // 提交个人信息修改
  const handleProfileUpdate = async () => {
    try {
      // 验证密码是否匹配
      if (editFormData.newPassword !== editFormData.confirmPassword) {
        setError('两次输入的密码不一致');
        return;
      }

      const updateData = {};
      if (editFormData.email !== userData.email) {
        updateData.email = editFormData.email;
      }
      if (editFormData.newPassword) {
        updateData.password = editFormData.newPassword;
      }

      // 如果没有修改内容
      if (Object.keys(updateData).length === 0) {
        setError('没有修改任何信息');
        return;
      }

      const response = await api.put('/api/user/update', updateData);
      
      // 更新本地存储的用户信息
      const updatedUser = {
        ...userData,
        email: editFormData.email || userData.email
      };
      localStorage.setItem('userInfo', JSON.stringify(updatedUser));
      setUserData(updatedUser);
      
      setError('');
      setShowEditProfileModal(false);
    } catch (err) {
      setError(err.response?.data?.message || '更新个人信息失败');
    }
  };

  // 初始化WebSocket连接
  useEffect(() => {
    if (userData && !socket) {
      const newSocket = io('http://localhost:5000', {
        withCredentials: true
      });

      newSocket.on('connect', () => {
        console.log('WebSocket connected');
        newSocket.emit('get_all_rooms');
      });

      newSocket.on('all_rooms_data', handleRoomsData);
      newSocket.on('system_message', handleSocketError);
      // 新增监听：房间创建成功事件
      newSocket.on('room_created', handleRoomCreated);

      setSocket(newSocket);
      setLoading(false);
    }

    return () => {
      if (socket) {
        socket.off('all_rooms_data', handleRoomsData);
        socket.off('system_message', handleSocketError);
        socket.off('room_created', handleRoomCreated);
        socket.disconnect();
      }
    };
  }, [userData]);

  const handleRoomsData = (data) => {
    setRooms(data.rooms);
  };
  // 新增处理：房间创建成功
  const handleRoomCreated = (newRoom) => {
    //setRooms(prev => [...prev, newRoom]); // 更新房间列表
    if( userData.user_id === newRoom.owner_id){
      setShowCreateRoomModal(false); // 关闭创建弹窗
      
      // 自动跳转到房主界面
      const roomInfo = {
        room_id: newRoom.id,
        room_name: newRoom.name,
        is_owner: true
      };
      localStorage.setItem('currentRoom', JSON.stringify(roomInfo));
      navigate('/chat/owner');
    }
  };

  const handleSocketError = (error) => {
    setError(error.message || '发生连接错误');
  };

  const handleLogout = async () => {
    try {
      await api.post('/api/auth/logout');
      localStorage.removeItem('userInfo');
      if (socket) socket.disconnect();
      navigate('/');
    } catch (err) {
      setError('注销失败，请检查网络连接');
    } finally {
      setIsDropdownOpen(false);
    }
  };

  // 修改后的创建房间逻辑
  const handleCreateRoomClick = () => {
    setNewRoomName(``); // 默认房间名
    setNewRoomPassword(''); // 清空密码
    setShowCreateRoomModal(true);
  };

  const handleConfirmCreateRoom = () => {
    if (!socket || !newRoomName.trim()) {
      setError('请输入房间名称');
      return;
    }
    
    socket.emit('create_room', {
      room_name: newRoomName,
      user_id: userData.user_id,
      password: newRoomPassword || null // 空密码转为null
    });
  };

  const handleSelectRoom = (room) => {
    if (!socket) return;
    
    setSelectedRoom(room);
    if (room.has_password) {
      setShowPasswordModal(true);
    } else {
      joinRoom(room.id, '');
    }
  };

  const handleSubmitPassword = () => {
    if (!socket) return;
    
    if (!passwordInput.trim()) {
      setError('请输入密码');
      return;
    }
    joinRoom(selectedRoom.id, passwordInput);
  };

  // 修改后的加入房间逻辑
  const joinRoom = async (roomId, password) => {
    try {
      // 2. 检查是否是房主
      const ownerCheck = await api.get(`/rooms/check_owner/${roomId}`);
      const isOwner = ownerCheck.data.is_owner;

      // 3. 存储房间信息并跳转
      const roomInfo = {
        room_id: roomId,
        room_name: selectedRoom?.name || `房间${roomId}`,
        is_owner: isOwner
      };
      localStorage.setItem('currentRoom', JSON.stringify(roomInfo));
      
      navigate(isOwner ? '/chat/owner' : '/chat/guest');
      
    } catch (error) {
      setError(error.response?.data?.message || '加入房间失败');
    }
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
        <div className="nav-brand">Vocabulary Arena —— 词汇竞技场</div>
        <div className="nav-links">
          <Link to="/home" className="nav-link active">首页</Link>
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
                <div className="menu-item" onClick={() => {
                  setShowEditProfileModal(true);
                  setIsDropdownOpen(false);
                }}>
                  修改信息
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
              onClick={handleCreateRoomClick}
              disabled={!socket}
            >
              立即创建
            </button>
          </div>

          {/* 房间列表区块 */}
          <div className="rooms-list-container">
            <h2>现有房间列表</h2>
            <div className="rooms-grid">
              {getCurrentPageRooms().map(room => (
                <div 
                  key={room.id} 
                  className="room-card"
                  onClick={() => handleSelectRoom(room)}
                >
                  <div className="room-name">{room.name}</div>
                  <div className="room-id">ID: {room.id}</div>
                  {room.has_password && (
                    <div className="room-lock-icon">🔒</div>
                  )}
                </div>
              ))}
            </div>
            <div className="pagination-controls">
              <button 
                className="pagination-button"
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 0}
              >
                上一页
              </button>
              <span className="page-info">
                第 {currentPage + 1} 页 / 共 {totalPages} 页
              </span>
              <button 
                className="pagination-button"
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage >= totalPages - 1}
              >
                下一页
              </button>
            </div>
          </div>
        </div>

      {/* 个人信息修改模态框 */}
      {showEditProfileModal && (
        <div className="modal-overlay">
          <div className="edit-profile-modal">
            <h3>修改个人信息</h3>
            {error && <div className="error-message">{error}</div>}
            
            <div className="form-group">
              <label>电子邮箱</label>
              <input
                type="email"
                name="email"
                value={editFormData.email}
                onChange={handleEditFormChange}
                placeholder="输入新邮箱"
              />
            </div>
            
            <div className="form-group">
              <label>新密码</label>
              <input
                type="password"
                name="newPassword"
                value={editFormData.newPassword}
                onChange={handleEditFormChange}
                placeholder="输入新密码（留空则不修改）"
              />
            </div>
            
            <div className="form-group">
              <label>确认密码</label>
              <input
                type="password"
                name="confirmPassword"
                value={editFormData.confirmPassword}
                onChange={handleEditFormChange}
                placeholder="再次输入新密码"
              />
            </div>
            
            <div className="modal-buttons">
              <button 
                className="cancel-button"
                onClick={() => {
                  setShowEditProfileModal(false);
                  setError('');
                }}
              >
                取消
              </button>
              <button 
                className="confirm-button"
                onClick={handleProfileUpdate}
              >
                保存修改
              </button>
            </div>
          </div>
        </div>
      )}

        {/* 密码输入模态框（加入房间） */}
        {showPasswordModal && (
          <div className="modal-overlay">
            <div className="password-modal">
              <h3>请输入房间密码</h3>
              <p>加入房间: {selectedRoom?.name}</p>
              <input
                type="password"
                placeholder="房间密码"
                value={passwordInput}
                onChange={(e) => setPasswordInput(e.target.value)}
                className="password-input"
              />
              <div className="modal-buttons">
                <button 
                  className="cancel-button"
                  onClick={() => setShowPasswordModal(false)}
                >
                  取消
                </button>
                <button 
                  className="confirm-button"
                  onClick={handleSubmitPassword}
                  disabled={!socket}
                >
                  确认
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 创建房间模态框 */}
        {showCreateRoomModal && (
          <div className="modal-overlay">
            <div className="create-room-modal">
              <h3>创建新房间</h3>
              <div className="form-group">
                <input
                  type="text"
                  value={newRoomName}
                  onChange={(e) => setNewRoomName(e.target.value)}
                  placeholder="输入房间名称"
                />
              </div>
              <div className="form-group">
                <input
                  type="password"
                  value={newRoomPassword}
                  onChange={(e) => setNewRoomPassword(e.target.value)}
                  placeholder="设置密码（留空为公开房间）"
                />
              </div>
              <div className="modal-buttons">
                <button 
                  className="cancel-button"
                  onClick={() => setShowCreateRoomModal(false)}
                >
                  取消
                </button>
                <button 
                  className="confirm-button"
                  onClick={handleConfirmCreateRoom}
                  disabled={!socket || !newRoomName.trim()}
                >
                  创建房间
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default Home;
