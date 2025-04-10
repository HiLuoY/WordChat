-- 创建数据库
CREATE DATABASE IF NOT EXISTS elp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE elp;

-- 创建房间表
CREATE TABLE IF NOT EXISTS rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建单词表
CREATE TABLE IF NOT EXISTS words (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(255) NOT NULL,
    meaning TEXT NOT NULL,
    hint TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建挑战表
CREATE TABLE IF NOT EXISTS word_challenges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_id INT NOT NULL,
    word_id INT NOT NULL,
    round_number INT DEFAULT 1,
    status ENUM('ongoing', 'finished') DEFAULT 'ongoing',
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (word_id) REFERENCES words(id)
);

-- 创建挑战尝试表
CREATE TABLE IF NOT EXISTS challenge_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    challenge_id INT NOT NULL,
    answer VARCHAR(255) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    attempted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (challenge_id) REFERENCES word_challenges(id)
); 