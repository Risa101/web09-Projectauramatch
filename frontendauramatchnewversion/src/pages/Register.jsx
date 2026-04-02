import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api/axios'
import './Register.css'

export default function Register() {
  const [form, setForm] = useState({ username: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await api.post(`/auth/register?username=${form.username}&email=${form.email}&password=${form.password}`)
      navigate('/login')
    } catch (err) {
      setError(err.response?.data?.detail || 'เกิดข้อผิดพลาด')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="register-page">
      {/* Decorative background accents */}
      <div className="register-bg-wrapper">
        <div className="register-bg-accent--purple" />
        <div className="register-bg-accent--pink" />
      </div>

      <div className="register-container">
        {/* Card */}
        <div className="register-card">
          {/* Branding */}
          <div className="register-branding">
            <div className="register-logo">
              <span className="register-logo-text">Aura</span>
              <span className="register-logo-dot" />
              <span className="register-logo-text">Match</span>
            </div>
            <h1 className="register-title">Create Account</h1>
            <p className="register-subtitle">Discover your perfect aura connection</p>
          </div>

          {/* Error message */}
          {error && (
            <div className="register-error">
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="register-form">
            <div>
              <label className="register-label">Username</label>
              <input
                type="text"
                required
                value={form.username}
                onChange={e => setForm({ ...form, username: e.target.value })}
                className="register-input"
                placeholder="Choose a username"
              />
            </div>

            <div>
              <label className="register-label">Email</label>
              <input
                type="email"
                required
                value={form.email}
                onChange={e => setForm({ ...form, email: e.target.value })}
                className="register-input"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label className="register-label">Password</label>
              <input
                type="password"
                required
                value={form.password}
                onChange={e => setForm({ ...form, password: e.target.value })}
                className="register-input"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="register-btn"
            >
              {loading ? (
                <span className="register-btn-loading">
                  <svg className="register-spinner" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="register-spinner-track" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="register-spinner-head" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Creating account...
                </span>
              ) : 'Create Account'}
            </button>
          </form>

          {/* Divider */}
          <div className="register-divider">
            <div className="register-divider-line" />
            <span className="register-divider-text">or</span>
            <div className="register-divider-line" />
          </div>

          {/* Sign in link */}
          <p className="register-footer">
            Already have an account?{' '}
            <Link to="/login" className="register-link">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
