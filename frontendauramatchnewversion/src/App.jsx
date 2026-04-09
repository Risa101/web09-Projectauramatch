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
import Blog from './pages/Blog'
import BlogPostPage from './pages/BlogPost'
import BlogManager from './pages/admin/BlogManager'
import Analytics from './pages/admin/Analytics'
import BannerManager from './pages/admin/BannerManager'

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
        <Route path="/blog" element={<Blog />} />
        <Route path="/blog/:slug" element={<BlogPostPage />} />
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/admin/blog" element={<BlogManager />} />
        <Route path="/admin/analytics" element={<Analytics />} />
        <Route path="/admin/banners" element={<BannerManager />} />
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
