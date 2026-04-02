import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Analyze from './pages/Analyze'
import Products from './pages/Products'
import GeminiChat from './pages/GeminiChat'
import PhotoEditor from './pages/PhotoEditor'
import AdminDashboard from './pages/admin/Dashboard'
import Profile from './pages/Profile'

function Layout() {
  const location = useLocation()
  const hideNavbar = location.pathname === '/'

  return (
    <>
      {!hideNavbar && <Navbar />}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/analyze" element={<Analyze />} />
        <Route path="/products" element={<Products />} />
        <Route path="/gemini" element={<GeminiChat />} />
        <Route path="/editor" element={<PhotoEditor />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/admin" element={<AdminDashboard />} />
      </Routes>
    </>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Layout />
      </BrowserRouter>
    </AuthProvider>
  )
}
