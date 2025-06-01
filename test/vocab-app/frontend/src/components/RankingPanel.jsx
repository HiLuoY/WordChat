import React from 'react';
import { FaTrophy, FaCrown, FaUser, FaStar } from 'react-icons/fa'; // 新增FaStar图标
import PropTypes from 'prop-types';
import "../styles/Ranking.css";

const RankingSidebar = ({ rankings, userRank, currentUserId }) => {
  const currentUserInRankings = rankings.find(user => user.id === currentUserId);
  
  return (
    <div className="ranking-sidebar">
      {/* 优化后的当前用户排名区域 */}
      {userRank !== null && (
        <div className="current-user-rank">
          <FaTrophy className="trophy-icon" /> {/* 新增奖杯图标 */}
          <span>您的排名: </span>
          <span className="rank-number">#{userRank}</span>
          {currentUserInRankings && (
            <span className="user-score">
              <FaStar style={{ marginRight: "6px", fontSize: "0.9em" }} /> {/* 新增星星图标 */}
              {currentUserInRankings.score}分
            </span>
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