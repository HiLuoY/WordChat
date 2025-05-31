import React from 'react';
import { FaTrophy, FaCrown, FaUser } from 'react-icons/fa';
import PropTypes from 'prop-types';
import "../styles/Ranking.css";

const RankingSidebar = ({ rankings, userRank, currentUserId }) => {
  // 获取当前用户在排行榜中的位置
  const currentUserInRankings = rankings.find(user => user.id === currentUserId);
  
  return (
    <div className="ranking-sidebar">
      {/* 显示当前用户排名 */}
      {userRank !== null && (
        <div className="current-user-rank">
          <span>您的排名: </span>
          <span className="rank-number">#{userRank}</span>
          {currentUserInRankings && (
            <span className="user-score">({currentUserInRankings.score}分)</span>
          )}
        </div>
      )}

      <div className="ranking-list">
        {rankings.length > 0 ? (
          rankings.map((user, index) => (
            <div 
              key={user.id} 
              className={`ranking-item ${user.id === currentUserId ? 'current-user' : ''}`}
            >
              <span className="rank">
                {index + 1}.
                {index === 0 && <FaCrown className="crown-icon" />}
              </span>
              
              <span className="user-avatar">
                {user.avatar ? (
                  <img src={user.avatar} alt={user.name} />
                ) : (
                  <FaUser className="default-avatar" />
                )}
              </span>
              
              <span className="user-name" title={user.name}>
                {user.name}
                {user.id === currentUserId && <span className="you-tag">(你)</span>}
              </span>
              
              <span className="score">{user.score}分</span>
            </div>
          ))
        ) : (
          <div className="no-rankings">
            <p>暂无排名数据</p>
            <p>等待比赛开始...</p>
          </div>
        )}
      </div>
    </div>
  );
};

RankingSidebar.propTypes = {
  rankings: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
      name: PropTypes.string.isRequired,
      score: PropTypes.number.isRequired,
      avatar: PropTypes.string,
    })
  ),
  userRank: PropTypes.number,
  currentUserId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
};

RankingSidebar.defaultProps = {
  rankings: [],
  userRank: null,
  currentUserId: null,
};

export default RankingSidebar;