import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { blogApi } from '../api/axios'
import { BookOpen, Eye, ChevronLeft, ChevronRight } from 'lucide-react'
import './Blog.css'

export default function Blog() {
  const [posts, setPosts] = useState([])
  const [categories, setCategories] = useState([])
  const [activeCategory, setActiveCategory] = useState(null)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    blogApi.getCategories().then(res => setCategories(res.data)).catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    const params = { page, limit: 12 }
    if (activeCategory) params.category_id = activeCategory
    blogApi.getPosts(params)
      .then(res => {
        setPosts(res.data.posts)
        setTotalPages(res.data.pages)
      })
      .catch(() => setPosts([]))
      .finally(() => setLoading(false))
  }, [activeCategory, page])

  const handleCategoryChange = (catId) => {
    setActiveCategory(catId)
    setPage(1)
  }

  return (
    <div className="blog-page">
      <div className="blog-container">

        {/* Header */}
        <div className="blog-header">
          <div className="blog-header__row">
            <div className="blog-header__accent" />
            <h1 className="blog-header__title">บทความ</h1>
          </div>
          <p className="blog-header__subtitle">
            เคล็ดลับความงามและการดูแลตัวเอง
          </p>
        </div>

        {/* Category filter */}
        {categories.length > 0 && (
          <div className="blog-filters">
            <button
              className={`blog-filter-pill ${!activeCategory ? 'blog-filter-pill--active' : ''}`}
              onClick={() => handleCategoryChange(null)}
            >
              ทั้งหมด
            </button>
            {categories.map(cat => (
              <button
                key={cat.category_id}
                className={`blog-filter-pill ${activeCategory === cat.category_id ? 'blog-filter-pill--active' : ''}`}
                onClick={() => handleCategoryChange(cat.category_id)}
              >
                {cat.name}
              </button>
            ))}
          </div>
        )}

        {/* Post grid */}
        {loading ? (
          <div className="blog-loading">กำลังโหลด...</div>
        ) : posts.length === 0 ? (
          <div className="blog-empty">
            <BookOpen size={48} className="blog-empty__icon" />
            <p className="blog-empty__title">ยังไม่มีบทความ</p>
            <p className="blog-empty__desc">บทความจะปรากฏที่นี่เมื่อมีการเผยแพร่</p>
          </div>
        ) : (
          <>
            <div className="blog-grid">
              {posts.map(post => (
                <Link key={post.post_id} to={`/blog/${post.slug}`} className="blog-card">
                  {post.thumbnail_url ? (
                    <img src={post.thumbnail_url} alt={post.title} className="blog-card__thumb" />
                  ) : (
                    <div className="blog-card__thumb-placeholder" />
                  )}
                  <div className="blog-card__body">
                    {post.category && (
                      <span className="blog-card__category">{post.category.name}</span>
                    )}
                    <h3 className="blog-card__title">{post.title}</h3>
                    <p className="blog-card__excerpt">{post.excerpt}</p>
                    <div className="blog-card__footer">
                      <span className="blog-card__author">{post.author}</span>
                      <span className="blog-card__dot">·</span>
                      <span className="blog-card__date">
                        {post.published_at
                          ? new Date(post.published_at).toLocaleDateString('th-TH', { day: 'numeric', month: 'short', year: 'numeric' })
                          : ''}
                      </span>
                      <span className="blog-card__views">
                        <Eye size={13} />
                        {post.views}
                      </span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="blog-pagination">
                <button
                  className="blog-pagination__btn"
                  disabled={page <= 1}
                  onClick={() => setPage(p => p - 1)}
                >
                  <ChevronLeft size={16} />
                  ก่อนหน้า
                </button>
                <span className="blog-pagination__info">
                  {page} / {totalPages}
                </span>
                <button
                  className="blog-pagination__btn"
                  disabled={page >= totalPages}
                  onClick={() => setPage(p => p + 1)}
                >
                  ถัดไป
                  <ChevronRight size={16} />
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
