import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { LogOut, User, LayoutDashboard, Menu, X, Sparkles, ShoppingBag, ImageIcon, BotMessageSquare } from 'lucide-react'
import './Navbar.css'

const navLinks = [
  { to: '/analyze', label: 'วิเคราะห์ใบหน้า', icon: Sparkles },
  { to: '/products', label: 'สินค้า', icon: ShoppingBag },
  { to: '/editor', label: 'แต่งรูป', icon: ImageIcon },
  { to: '/gemini', label: 'Gemini AI', icon: BotMessageSquare },
]

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <nav className="navbar">
      <div className="navbar__inner">
        <div className="navbar__row">

          {/* Logo */}
          <Link to="/" className="navbar-logo">
            <span className="navbar-logo__circle">
              <span className="navbar-logo__circle-bg" />
              <span className="navbar-logo__letter">A</span>
            </span>
            <span className="navbar-logo__text">
              AuraMatch
            </span>
          </Link>

          {/* Desktop nav links */}
          {user && (
            <div className="navbar-desktop-links">
              {navLinks.map(({ to, label }) => (
                <Link
                  key={to}
                  to={to}
                  className="navbar-link"
                >
                  {label}
                  <span className="navbar-link__underline" />
                </Link>
              ))}
              {user.role === 'admin' && (
                <Link
                  to="/admin"
                  className="navbar-link navbar-link--admin"
                >
                  <LayoutDashboard size={15} />
                  Admin
                  <span className="navbar-link__underline" />
                </Link>
              )}
            </div>
          )}

          {/* Desktop right side */}
          <div className="navbar-desktop-right">
            {user ? (
              <>
                <Link to="/profile" className="navbar-profile-btn">
                  <User size={18} />
                </Link>
                <button onClick={handleLogout} className="navbar-logout-btn">
                  <LogOut size={16} />
                  <span className="navbar-logout-btn__label">ออกจากระบบ</span>
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="navbar-login-link">
                  เข้าสู่ระบบ
                </Link>
                <Link to="/register" className="navbar-register-link">
                  สมัครสมาชิก
                </Link>
              </>
            )}
          </div>

          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileOpen((prev) => !prev)}
            className="navbar-hamburger"
            aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
          >
            {mobileOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="navbar-mobile-menu">
          <div className="navbar-mobile-menu__inner">
            {user ? (
              <>
                {navLinks.map(({ to, label, icon: Icon }) => (
                  <Link
                    key={to}
                    to={to}
                    onClick={() => setMobileOpen(false)}
                    className="navbar-mobile-link"
                  >
                    <Icon size={18} className="navbar-mobile-link__icon" />
                    {label}
                  </Link>
                ))}
                {user.role === 'admin' && (
                  <Link
                    to="/admin"
                    onClick={() => setMobileOpen(false)}
                    className="navbar-mobile-link navbar-mobile-link--admin"
                  >
                    <LayoutDashboard size={18} />
                    Admin
                  </Link>
                )}
                <hr className="navbar-mobile-divider" />
                <Link
                  to="/profile"
                  onClick={() => setMobileOpen(false)}
                  className="navbar-mobile-link navbar-mobile-link--profile"
                >
                  <User size={18} className="navbar-mobile-link__icon" />
                  โปรไฟล์
                </Link>
                <button
                  onClick={() => { setMobileOpen(false); handleLogout(); }}
                  className="navbar-mobile-logout"
                >
                  <LogOut size={18} />
                  ออกจากระบบ
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  onClick={() => setMobileOpen(false)}
                  className="navbar-mobile-login"
                >
                  เข้าสู่ระบบ
                </Link>
                <Link
                  to="/register"
                  onClick={() => setMobileOpen(false)}
                  className="navbar-mobile-register"
                >
                  สมัครสมาชิก
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  )
}
