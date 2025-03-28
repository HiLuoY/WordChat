import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Learn from "./pages/Learn";
import Login from './pages/Login';
// import Books from "./pages/Books";
// import MyWords from "./pages/MyWords";
// import Chat from "./pages/Chat";
// import Profile from "./pages/Profile";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/learn" element={<Learn />} />
        <Route path="/login" element={<Login />} />
        {/* <Route path="/books" element={<Books />} />
        <Route path="/my-words" element={<MyWords />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/profile" element={<Profile />} /> */}
      </Routes>
    </Router>
  );
};

export default App;