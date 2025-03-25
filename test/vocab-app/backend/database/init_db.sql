CREATE DATABASE IF NOT EXISTS elp;
USE elp;

-- 用户表
CREATE TABLE IF NOT EXISTS Users (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID(主键, 自增)',
    email VARCHAR(255) NOT NULL UNIQUE COMMENT '用户邮箱(唯一)',
    password_hash VARCHAR(255) NOT NULL COMMENT '用户密码哈希',
    nickname VARCHAR(100) NOT NULL COMMENT '用户昵称',
    avatar VARCHAR(255) COMMENT '用户头像URL',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '用户注册时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间'
) COMMENT='用户信息表';

-- 房间表
CREATE TABLE IF NOT EXISTS Rooms (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '房间ID(主键, 自增)',
    room_name VARCHAR(255) NOT NULL UNIQUE COMMENT '房间名称(唯一)',
    password VARCHAR(255) COMMENT '房间密码(可为空)',
    owner_id INT UNSIGNED NOT NULL COMMENT '房主ID(外键)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '房间创建时间',
    FOREIGN KEY (owner_id) REFERENCES Users(id)
) COMMENT='房间信息表';

-- 房间成员表
CREATE TABLE IF NOT EXISTS RoomMembers (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '成员ID(主键, 自增)',
    room_id INT UNSIGNED NOT NULL COMMENT '房间ID(外键)',
    user_id INT UNSIGNED NOT NULL COMMENT '用户ID(外键)',
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
    UNIQUE KEY (room_id, user_id) COMMENT '确保用户在一个房间只能加入一次',
    FOREIGN KEY (room_id) REFERENCES Rooms(id),
    FOREIGN KEY (user_id) REFERENCES Users(id)
) COMMENT='房间成员关系表';

-- 聊天消息表
CREATE TABLE IF NOT EXISTS Messages (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '消息ID(主键, 自增)',
    room_id INT UNSIGNED NOT NULL COMMENT '房间ID(外键)',
    user_id INT UNSIGNED NOT NULL COMMENT '用户ID(外键)',
    message TEXT NOT NULL COMMENT '消息内容',
    message_type ENUM('normal', 'correct') DEFAULT 'normal' COMMENT '消息类型: 普通消息/正确回答',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
    FOREIGN KEY (room_id) REFERENCES Rooms(id),
    FOREIGN KEY (user_id) REFERENCES Users(id)
) COMMENT='聊天消息表';

-- 单词表
CREATE TABLE IF NOT EXISTS Words (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '单词ID(主键, 自增)',
    word VARCHAR(100) NOT NULL UNIQUE COMMENT '单词内容',
    meaning TEXT NOT NULL COMMENT '单词的中文释义'
) COMMENT='单词信息表';

-- 单词挑战表
CREATE TABLE IF NOT EXISTS WordChallenges (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '挑战ID(主键, 自增)',
    room_id INT UNSIGNED NOT NULL COMMENT '房间ID(外键)',
    word_id INT UNSIGNED NOT NULL COMMENT '单词ID(外键)',
    round_number INT UNSIGNED NOT NULL COMMENT '当前轮次',
    status ENUM('ongoing', 'finished') DEFAULT 'ongoing' COMMENT '挑战状态: 进行中/结束',
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '挑战开始时间',
    FOREIGN KEY (room_id) REFERENCES Rooms(id),
    FOREIGN KEY (word_id) REFERENCES Words(id)
) COMMENT='单词挑战信息表';

-- 用户挑战记录表
CREATE TABLE IF NOT EXISTS ChallengeAttempts (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID(主键, 自增)',
    challenge_id INT UNSIGNED NOT NULL COMMENT '挑战ID(外键)',
    user_id INT UNSIGNED NOT NULL COMMENT '用户ID(外键)',
    submitted_word VARCHAR(255) NOT NULL COMMENT '用户提交的单词',
    is_correct BOOLEAN NOT NULL COMMENT '是否正确',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
    FOREIGN KEY (challenge_id) REFERENCES WordChallenges(id),
    FOREIGN KEY (user_id) REFERENCES Users(id)
) COMMENT='用户挑战记录表';

-- 排行榜表
CREATE TABLE IF NOT EXISTS Leaderboard (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID(主键, 自增)',
    room_id INT UNSIGNED NOT NULL COMMENT '房间ID(外键)',
    user_id INT UNSIGNED NOT NULL COMMENT '用户ID(外键)',
    score INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '得分',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY (room_id, user_id) COMMENT '确保每个用户在房间中只有一条记录',
    FOREIGN KEY (room_id) REFERENCES Rooms(id),
    FOREIGN KEY (user_id) REFERENCES Users(id)
) COMMENT='房间排行榜表';
