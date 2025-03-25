CREATE DATABASE IF NOT EXISTS elp;
USE elp;

CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    nickname VARCHAR(100) NOT NULL,
    avatar_url VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


CREATE TABLE Messages (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '消息 id(自增主键)',
    room_id INT UNSIGNED COMMENT '消息所属房间 id',
    user_id INT UNSIGNED COMMENT '发送消息的用户 id',
    message TEXT NOT NULL COMMENT '消息内容',
    message_type ENUM('normal', 'correct') DEFAULT 'normal' COMMENT '消息类型: 普通消息/正确回答',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '消息发送时间',
    FOREIGN KEY (room_id) REFERENCES Rooms(room_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
) COMMENT='存储消息信息的表';

CREATE TABLE Words (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '单词 id',
    word VARCHAR(100) NOT NULL UNIQUE COMMENT '单词内容',
    meaning TEXT NOT NULL COMMENT '中文释义'
) COMMENT='存储单词及其中文释义的表';

CREATE TABLE WordsChallenge (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '挑战 id',
    room_id INT UNSIGNED COMMENT '房间号',
    word_id INT UNSIGNED COMMENT '当前挑战单词',
    round_number INT UNSIGNED NOT NULL COMMENT '当前轮次',
    status ENUM('ongoing', 'finished') DEFAULT 'ongoing' COMMENT '挑战状态',
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '挑战开始时间',
    FOREIGN KEY (room_id) REFERENCES Rooms(room_id),
    FOREIGN KEY (word_id) REFERENCES Words(id)
) COMMENT='存储单词挑战信息的表';


-- 存储用户挑战记录的表
CREATE TABLE ChallengeAttempts (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '挑战记录唯一标识',
    challenge_id BIGINT UNSIGNED COMMENT '关联的单词挑战 ID',
    user_id BIGINT UNSIGNED COMMENT '提交挑战的用户 ID',
    submitted_word VARCHAR(255) NOT NULL COMMENT '用户提交的单词',
    is_correct BOOLEAN NOT NULL COMMENT '提交结果是否正确',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间（自动记录）',
    FOREIGN KEY (challenge_id) REFERENCES WordsChallenge(id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
) COMMENT='用户单词挑战提交记录表';

-- 存储房间排行榜数据的表
CREATE TABLE Leaderboard (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '排行榜记录唯一标识',
    room_id BIGINT UNSIGNED COMMENT '关联的房间 ID',
    user_id BIGINT UNSIGNED COMMENT '关联的用户 ID',
    score INT UNSIGNED NOT NULL COMMENT '用户得分（非负整数）',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    FOREIGN KEY (room_id) REFERENCES Rooms(room_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
) COMMENT='房间实时排行榜数据表';