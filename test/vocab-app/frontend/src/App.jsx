import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import GuestChatPage from "./pages/GuestChatPage";
//import Learn from "./pages/Learn";
import Login from './pages/Login';
import ChatPage from "./pages/OwnerChatPage";
// import MyWords from "./pages/MyWords";
// import Chat from "./pages/Chat";
// import Profile from "./pages/Profile";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/chat/owner" element={<ChatPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/chat/guest" element={<GuestChatPage />} />
        {/* <Route path="/books" element={<Books />} />
        <Route path="/my-words" element={<MyWords />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/profile" element={<Profile />} /> */}
      </Routes>
    </Router>
  );
};

export default App;