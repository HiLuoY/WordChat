// src/Login.js
import React, { useState, useEffect } from 'react';
import styles from '../styles/Login.module.css'; // 修改导入方式

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [rememberMe, setRememberMe] = useState(false);

    useEffect(() => {
        // 添加 loginBody 类到 body 元素
        document.body.classList.add(styles.loginBody);

        // 组件卸载时移除 loginBody 类
        return () => {
            document.body.classList.remove(styles.loginBody);
        };
    }, []); // 空依赖数组确保只在挂载和卸载时运行

    const handleSubmit = (e) => {
        e.preventDefault();
        
        // 这里添加登录验证逻辑
        console.log('Email:', email);
        console.log('Password:', password);
        console.log('Remember Me:', rememberMe);
        
        // 模拟登录成功
        alert('登录成功，正在跳转...');
        // window.location.href = '/dashboard';
    };

    return (
        <div className={styles.loginBody}>
        <div className={styles.loginContainer}>
            <div className={styles.logo}>
                <div className={styles.logoIcon}>
                    <span style={{ color: 'white', fontSize: '24px' }}>WC</span>
                </div>
                <h1>欢迎使用 WordChat</h1>
                <p className={styles.subtitle}>边聊边学 · 轻松掌握外语</p>
            </div>

            <form id="loginForm" onSubmit={handleSubmit}>
                <div className={styles.formGroup}>
                    <input 
                        type="email" 
                        id="email" 
                        placeholder="电子邮箱" 
                        value={email} 
                        onChange={(e) => setEmail(e.target.value)} 
                        required 
                    />
                </div>
                <div className={styles.formGroup}>
                    <input 
                        type="password" 
                        id="password" 
                        placeholder="密码" 
                        value={password} 
                        onChange={(e) => setPassword(e.target.value)} 
                        required 
                    />
                </div>
                
                <div className={styles.rememberForgot}>
                    <label>
                        <input 
                            type="checkbox" 
                            checked={rememberMe} 
                            onChange={(e) => setRememberMe(e.target.checked)} 
                        /> 记住我
                    </label>
                    <a href="#" style={{ color: 'rgb(28, 50, 0)', textDecoration: 'none' }}>忘记密码？</a>
                </div>

                <button type="submit">立即登录</button>
            </form>

            <div className={styles.signupLink}>
                还没有账号？ <a href="#">立即注册</a>
            </div>
        </div>
        </div>
    );
};

export default Login;