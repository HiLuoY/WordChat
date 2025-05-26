import React from 'react';
import { FaTrophy } from 'react-icons/fa';
import PropTypes from 'prop-types';
import "../styles/Ranking.css"
const RankingSidebar = ({ rankings }) => {
  return (
    <div className="ranking-sidebar">
      <div className="ranking-list">
        {rankings.length > 0 ? (
          rankings.map((user, index) => (
            <div key={user.id} className="ranking-item">
              <span className="rank">{index + 1}.</span>
              <span className="user-name">{user.name}</span>
              <span className="score">{user.score}分</span>
            </div>
          ))
        ) : (
          <div className="no-rankings">暂无排名数据</div>
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
  ).isRequired,
};

RankingSidebar.defaultProps = {
  rankings: [
    { id: 1, name: '用户A', score: 100 },
    { id: 2, name: '用户B', score: 80 },
    { id: 3, name: '用户C', score: 60 },
  ],
};

export default RankingSidebar;