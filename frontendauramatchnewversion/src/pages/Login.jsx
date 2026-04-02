import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../api/axios'
import './Login.css'

export default function Login() {
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const res = await api.post(`/auth/login?email=${form.email}&password=${form.password}`)
      login(res.data.access_token, res.data.role)
      navigate(res.data.role === 'admin' ? '/admin' : '/')
    } catch {
      setError('อีเมลหรือรหัสผ่านไม่ถูกต้อง')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">

        {/* Left decorative panel */}
        <div className="login-panel">
          {/* Decorative circles */}
          <div className="login-panel-circle login-panel-circle--top" />
          <div className="login-panel-circle login-panel-circle--bottom" />
          <div className="login-panel-circle login-panel-circle--middle" />

          <div className="login-panel__inner">
            <div className="login-brand">
              <span className="login-brand__dot" />
              <span className="login-brand__name">
                AuraMatch
              </span>
            </div>
          </div>

          <div className="login-panel__tagline-wrapper">
            <h2 className="login-panel__tagline">
              ค้นพบความสวย<br />ที่เป็นคุณ
            </h2>
            <p className="login-panel__desc">
              วิเคราะห์โครงหน้าและสีผิว เพื่อค้นหาเครื่องสำอางที่เหมาะกับคุณมากที่สุด
            </p>
          </div>

          <div className="login-panel__footer">
            <p className="login-panel__copyright">
              &copy; 2026 AuraMatch
            </p>
          </div>
        </div>

        {/* Right form panel */}
        <div className="login-form-panel">

          {/* Mobile logo */}
          <div className="login-mobile-logo">
            <span className="login-brand__dot login-brand__dot--gradient" />
            <span className="login-brand__name login-brand__name--dark">
              AuraMatch
            </span>
          </div>

          <h1 className="login-heading">
            ยินดีต้อนรับกลับ
          </h1>
          <p className="login-subheading">
            เข้าสู่ระบบเพื่อดำเนินการต่อ
          </p>

          {error && (
            <div className="login-error">
              <p className="login-error__text">
                {error}
              </p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="login-form">
            <div>
              <label className="login-label">
                อีเมล
              </label>
              <input
                type="email"
                required
                value={form.email}
                onChange={e => setForm({ ...form, email: e.target.value })}
                className="login-input"
                placeholder="example@email.com"
              />
            </div>

            <div>
              <label className="login-label">
                รหัสผ่าน
              </label>
              <input
                type="password"
                required
                value={form.password}
                onChange={e => setForm({ ...form, password: e.target.value })}
                className="login-input"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="login-btn"
            >
              {loading ? 'กำลังเข้าสู่ระบบ...' : 'เข้าสู่ระบบ'}
            </button>
          </form>

          <p className="login-footer">
            ยังไม่มีบัญชี?{' '}
            <Link to="/register" className="login-footer__link">
              สมัครสมาชิก
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
