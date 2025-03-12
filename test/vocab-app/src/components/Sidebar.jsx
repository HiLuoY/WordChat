import React from "react";
import { Link,useLocation } from "react-router-dom";
import "../styles/Sidebar.css";

const Sidebar = () => {
  const location = useLocation();
  return (
    <div className="sidebar">
      <Link to="/" className={`sidebar-button ${location.pathname === "/" ? "active" : ""}`}>
        背单词
      </Link>
      <Link to="/books" className={`sidebar-button ${location.pathname === "/books" ? "active" : ""}`}>
        词书
      </Link>
      <Link to="/my-words" className={`sidebar-button ${location.pathname === "/my-words" ? "active" : ""}`}>
        我的单词本
      </Link>
      <Link to="/chat" className={`sidebar-button ${location.pathname === "/chat" ? "active" : ""}`}>
        英语圈子
      </Link>
    </div>
  );
};

export default Sidebar;