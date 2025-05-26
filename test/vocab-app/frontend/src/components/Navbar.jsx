import React from 'react';
import { 
  FaDoorOpen,        // 退出房间
  FaTrophy,          // 排行榜
  FaUserSlash,       // 踢人
  FaUserEdit,        // 编辑资料
  FaUserCircle       // 默认头像
} from 'react-icons/fa';
import '../styles/Navbar.css';

const DEFAULT_AVATAR = '/default-avatar.jpg';

const Navbar = ({ 
  onLeaveRoom, 
  onShowRanking, 
  onKickUser, 
  onEditProfile,
  showRoomControls = true,
  showKickButton = true
}) => {
  const userAvatar = localStorage.getItem('userAvatar');

  return (
    <nav className="navbar">
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
                onClick={onKickUser} 
                className="nav-button icon-button" 
                title="踢人"
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