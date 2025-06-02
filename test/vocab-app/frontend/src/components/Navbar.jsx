import React, { useState } from 'react';
import { 
  FaDoorOpen,        // 退出房间
  FaTrophy,          // 排行榜
  FaUserSlash,       // 踢人
  FaUserEdit,        // 编辑资料
  FaUserCircle,      // 默认头像
  FaTimes            // 关闭
} from 'react-icons/fa';
import '../styles/Navbar.css';

const DEFAULT_AVATAR = '/default-avatar.jpg';

const Navbar = ({ 
  onLeaveRoom, 
  onShowRanking, 
  onKickUser, 
  onEditProfile,
  showRoomControls = true,
  showKickButton = true,
  rankings = [],
  currentUserId
}) => {
  const [showKickModal, setShowKickModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const userAvatar = localStorage.getItem('userAvatar');

  const handleKickClick = () => {
    if (rankings.length <= 1) {
      alert("房间内没有其他用户可踢出");
      return;
    }
    setShowKickModal(true);
  };

  const confirmKick = () => {
    if (!selectedUser) return;
    
    const confirm = window.confirm(`确定要踢出用户 ${selectedUser.nickname} 吗？`);
    if (confirm) {
      onKickUser(selectedUser.user_id);
      setShowKickModal(false);
      setSelectedUser(null);
    }
  };

  return (
    <nav className="navbar">
      {/* 踢人模态框 */}
      {showKickModal && (
        <div className="kick-modal-overlay">
          <div className="kick-modal">
            <div className="modal-header">
              <h3>选择要踢出的用户</h3>
              <button 
                onClick={() => setShowKickModal(false)}
                className="close-button"
              >
                <FaTimes />
              </button>
            </div>
            
            <div className="user-list">
              {rankings
                .filter(user => user.user_id !== currentUserId)
                .map(user => (
                  <div 
                    key={user.user_id} 
                    className={`user-item ${selectedUser?.user_id === user.user_id ? 'selected' : ''}`}
                    onClick={() => setSelectedUser(user)}
                  >
                    <img 
                      src={user.avatar || DEFAULT_AVATAR} 
                      alt={user.nickname}
                      onError={(e) => {
                        e.target.onerror = null;
                        e.target.src = DEFAULT_AVATAR;
                      }}
                    />
                    <span>{user.nickname}</span>
                    {user.score && <span className="score">{user.score}分</span>}
                  </div>
                ))}
            </div>
            
            <div className="modal-actions">
              <button 
                onClick={confirmKick}
                disabled={!selectedUser}
                className="confirm-button"
              >
                确认踢出
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="navbar-left">
        {showRoomControls && (
          <>
            <button onClick={onLeaveRoom} className="nav-button icon-button" title="退出房间">
              <FaDoorOpen className="nav-icon" />
            </button>
            <button onClick={onShowRanking} className="nav-button icon-button" title="排行榜">
              <FaTrophy className="nav-icon active" />
            </button>
            {showKickButton && (
              <button 
                onClick={handleKickClick} 
                className="nav-button icon-button" 
                title="踢出用户"
              >
                <FaUserSlash className="nav-icon" />
              </button>
            )}
          </>
        )}
      </div>
      
      <div className="navbar-right">
        <button onClick={onEditProfile} className="avatar-button">
          {userAvatar ? (
            <img 
              src={userAvatar} 
              alt="用户头像" 
              className="user-avatar"
              onError={(e) => {
                e.target.onerror = null;
                e.target.src = DEFAULT_AVATAR;
              }}
            />
          ) : (
            <img 
              src={DEFAULT_AVATAR}
              alt="默认头像"
              className="user-avatar"
            />
          )}
        </button>
      </div>
    </nav>
  );
};

export default Navbar;