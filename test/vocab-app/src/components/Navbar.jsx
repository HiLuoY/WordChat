import React from "react";
import { Link } from "react-router-dom";
import "../styles/Navbar.css";

const Navbar = () => {
    return (
        <div className="navbar">
          <div className="logo">
            word<span style={{ color: 'white' }}>chat</span>
            </div>
          <div className="nav-links">
            
            <Link to="/profile" className="nav-link">
              <div className="icon-container">
                <img src="/profile.svg" alt="个人资料" className="nav-icon" />
              </div>
            </Link>
          </div>
        </div>
      );
    };

export default Navbar;