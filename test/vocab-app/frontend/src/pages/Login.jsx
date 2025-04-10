import { useState } from 'react'
import axios from 'axios'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleLogin = async () => {
    try {
      const res = await axios.post('http://localhost/api/user/login', {
        email, password
      }, { withCredentials: true })
      alert(res.data.message)
    } catch (e) {
      alert(e.response?.data?.message || '登录失败')
    }
  }

  return (
    <div>
      <h2>登录</h2>
      <input value={email} onChange={e => setEmail(e.target.value)} placeholder="Email" />
      <input value={password} onChange={e => setPassword(e.target.value)} type="password" placeholder="密码" />
      <button onClick={handleLogin}>登录</button>
    </div>
  )
}
