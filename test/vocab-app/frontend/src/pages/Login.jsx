import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import '../styles/AuthForm.css' // 新增CSS导入
import api  from './api'

export default function AuthForm() {
  const navigate = useNavigate()
  const [isLogin, setIsLogin] = useState(true)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    nickname: '',
    confirmPassword: ''
  })
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      if (!isLogin) {
        if (formData.password !== formData.confirmPassword) {
          throw new Error('两次密码输入不一致')
        }
        if (!formData.nickname) {
          throw new Error('昵称不能为空')
        }
      }

      const payload = isLogin 
        ? { email: formData.email, password: formData.password }
        : { 
            email: formData.email,
            password: formData.password,
            nickname: formData.nickname
          }

      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/register'
      const { data } = await api.post(endpoint, payload)

      if (data.code === 200 || data.code === 201) {
        // 保存用户数据到localStorage
        localStorage.setItem('userInfo', JSON.stringify(data.data));
        navigate('/home')
      } else {
        throw new Error(data.message)
      }
    } catch (err) {
      const errorMessage = err.response?.data?.message || err.message
      setError(errorMessage.includes("已存在") ? "邮箱已被注册" : errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="tabs">
        <button 
          className={isLogin ? 'active' : ''}
          onClick={() => setIsLogin(true)}
          type="button"
        >
          登录
        </button>
        <button
          className={!isLogin ? 'active' : ''}
          onClick={() => setIsLogin(false)}
          type="button"
        >
          注册
        </button>
      </div>

      <form onSubmit={handleSubmit}>
        {!isLogin && (
          <div className="form-group">
            <label>昵称</label>
            <input
              type="text"
              name="nickname"
              value={formData.nickname}
              onChange={handleChange}
              required
              placeholder="请输入昵称"
            />
          </div>
        )}

        <div className="form-group">
          <label>邮箱</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
            placeholder="请输入邮箱"
          />
        </div>

        <div className="form-group">
          <label>密码</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
            minLength="6"
            placeholder="请输入密码"
          />
        </div>

        {!isLogin && (
          <div className="form-group">
            <label>确认密码</label>
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              placeholder="请再次输入密码"
            />
          </div>
        )}

        {error && <div className="error">{error}</div>}

        <button type="submit" disabled={isLoading}>
          {isLoading ? '处理中...' : (isLogin ? '登录' : '注册')}
        </button>
      </form>
    </div>
  )
}