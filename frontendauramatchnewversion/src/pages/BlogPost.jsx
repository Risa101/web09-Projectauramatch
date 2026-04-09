import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { blogApi } from '../api/axios'
import { ArrowLeft, Eye, Calendar, User } from 'lucide-react'
import './BlogPost.css'

export default function BlogPostPage() {
  const { slug } = useParams()
  const [post, setPost] = useState(null)
  const [error, setError] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    blogApi.getPost(slug)
      .then(res => {
        setPost(res.data)
        blogApi.trackView(slug).catch(() => {})
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false))
  }, [slug])

  if (loading) {
    return (
      <div className="blogpost-page">
        <div className="blogpost-container">
          <div className="blogpost-loading">กำลังโหลด...</div>
        </div>
      </div>
    )
  }

  if (error || !post) {
    return (
      <div className="blogpost-page">
        <div className="blogpost-container">
          <div className="blogpost-error">
            <p className="blogpost-error__title">ไม่พบบทความนี้</p>
            <p className="blogpost-error__desc">บทความอาจถูกลบหรือยังไม่ได้เผยแพร่</p>
            <Link to="/blog" className="blogpost-back-link">
              <ArrowLeft size={16} />
              กลับไปบทความทั้งหมด
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="blogpost-page">
      <div className="blogpost-container">

        <Link to="/blog" className="blogpost-back-link">
          <ArrowLeft size={16} />
          กลับไปบทความทั้งหมด
        </Link>

        <article className="blogpost-article">
          {/* Header */}
          <header className="blogpost-article__header">
            {post.category && (
              <span className="blogpost-article__category">{post.category.name}</span>
            )}
            <h1 className="blogpost-article__title">{post.title}</h1>
            <div className="blogpost-article__meta">
              <span className="blogpost-article__meta-item">
                <User size={14} />
                {post.author}
              </span>
              <span className="blogpost-article__meta-item">
                <Calendar size={14} />
                {post.published_at
                  ? new Date(post.published_at).toLocaleDateString('th-TH', { day: 'numeric', month: 'long', year: 'numeric' })
                  : ''}
              </span>
              <span className="blogpost-article__meta-item">
                <Eye size={14} />
                {post.views} views
              </span>
            </div>
          </header>

          {/* Thumbnail */}
          {post.thumbnail_url && (
            <img src={post.thumbnail_url} alt={post.title} className="blogpost-article__thumb" />
          )}

          {/* Content */}
          <div className="blogpost-article__content">
            {post.content}
          </div>
        </article>
      </div>
    </div>
  )
}
