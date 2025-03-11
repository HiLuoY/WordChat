import React from "react";
import { Outlet, Link } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "../styles/Home.css";

const Home = () => {
  // 模拟用户数据
  const user = {
    name: "小明",
    learnedWords: 1066,
    totalWords: 1600,
    currentBook: "六级词汇",
  };

  return (
    <div className="home">
      <Navbar />
      <div className="home-container">
      <Sidebar />
        <div className="white-back"></div>
          <div className="main-content">
            <div className="green-block">
              <div className="book-info">
                <div className="book-name">
                  <h3>在学词书</h3>
                  <p>{user.currentBook}</p>
                </div>
                <img src="/src/assets/sixvocab.png" alt="单词书" className="book-image" />
              </div>
            </div>
            <div className="progress">
              <p>
                已学习 {user.learnedWords} / 总词数 {user.totalWords}
              </p>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${(user.learnedWords / user.totalWords) * 100}%` }}
                ></div>
              </div>
            </div>
            <div className="actions">
              <Link to="/learn" className="action-button">
                Learn
                <span className="button-text">434</span>
                </Link>
              <Link to="/review" className="action-button">
                Review
                <span className="button-text">46</span>
                </Link>
            </div>
          
        </div>
      </div>
      {/* <Footer /> */}
    </div>
  );
};

export default Home;