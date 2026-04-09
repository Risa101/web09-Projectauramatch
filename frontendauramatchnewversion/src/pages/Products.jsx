import { useState, useEffect } from 'react'
import api, { favoritesApi, skinConcernsApi, reviewsApi } from '../api/axios'
import { useAuth } from '../context/AuthContext'
import { ShoppingBag, ExternalLink, Search, SlidersHorizontal, ChevronDown, X, Loader2, Sparkles, ArrowLeft, Scale, Check, Heart, ShieldCheck, Star, MessageSquare, Trash2 } from 'lucide-react'
import { trackProductView, trackSearch, trackFilter, trackClick, trackSimilarView } from '../services/tracker'
import './Products.css'

export default function Products() {
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [brands, setBrands] = useState([])
  const [loading, setLoading] = useState(true)

  // Filters
  const [search, setSearch] = useState('')
  const [selectedCategory, setSelectedCategory] = useState(null)
  const [selectedBrand, setSelectedBrand] = useState(null)
  const [selectedColor, setSelectedColor] = useState(null)
  const [sort, setSort] = useState('newest')
  const [showFilters, setShowFilters] = useState(false)

  // Compare
  const [compareList, setCompareList] = useState([])
  const [showCompare, setShowCompare] = useState(false)
  const [latestAnalysisId, setLatestAnalysisId] = useState(null)
  const [compareScores, setCompareScores] = useState({})
  const [compareFaceShape, setCompareFaceShape] = useState(null)
  const [loadingCompare, setLoadingCompare] = useState(false)

  // Similar products (TF-IDF)
  const [selectedProduct, setSelectedProduct] = useState(null)
  const [similarProducts, setSimilarProducts] = useState([])
  const [loadingSimilar, setLoadingSimilar] = useState(false)

  // Favorites
  const { user } = useAuth()
  const [favoriteIds, setFavoriteIds] = useState(new Set())

  // User skin concerns
  const [userConcernIds, setUserConcernIds] = useState(new Set())

  // Product detail + reviews
  const [detailProduct, setDetailProduct] = useState(null)
  const [reviews, setReviews] = useState([])
  const [reviewSummary, setReviewSummary] = useState(null)
  const [loadingReviews, setLoadingReviews] = useState(false)
  const [reviewForm, setReviewForm] = useState({ rating: 0, comment: '' })
  const [submittingReview, setSubmittingReview] = useState(false)

  const COSMETIC_CATEGORY_IDS = [1, 2, 3, 4, 5, 6, 7]

  useEffect(() => {
    api.get('/products/categories').then(res => {
      setCategories(res.data.filter(c => COSMETIC_CATEGORY_IDS.includes(c.category_id)))
    }).catch(() => {})
    api.get('/products/brands').then(res => setBrands(res.data)).catch(() => {})
  }, [])

  // Load favorite IDs and user concerns when logged in
  useEffect(() => {
    if (!user) { setFavoriteIds(new Set()); setUserConcernIds(new Set()); return }
    favoritesApi.getIds()
      .then(res => setFavoriteIds(new Set(res.data)))
      .catch(() => {})
    skinConcernsApi.getMine()
      .then(res => setUserConcernIds(new Set(res.data.map(c => c.concern_id))))
      .catch(() => {})
  }, [user])

  useEffect(() => {
    setLoading(true)
    const params = new URLSearchParams()
    if (selectedCategory) params.append('category_id', selectedCategory)
    if (selectedBrand) params.append('brand_id', selectedBrand)
    if (selectedColor) params.append('personal_color', selectedColor)
    if (search.trim()) params.append('search', search.trim())
    if (sort) params.append('sort', sort)
    params.append('limit', '50')

    api.get(`/products/?${params.toString()}`)
      .then(res => setProducts(res.data))
      .catch(() => setProducts([]))
      .finally(() => setLoading(false))
    // Track search
    if (search.trim()) trackSearch(search.trim())
  }, [selectedCategory, selectedBrand, selectedColor, sort, search])

  // Track filters
  useEffect(() => {
    if (selectedCategory) trackFilter('category', selectedCategory)
  }, [selectedCategory])
  useEffect(() => {
    if (selectedBrand) trackFilter('brand', selectedBrand)
  }, [selectedBrand])
  useEffect(() => {
    if (selectedColor) trackFilter('personal_color', selectedColor)
  }, [selectedColor])

  // Fetch latest analysis for compare scoring
  useEffect(() => {
    api.get('/profile/analyses')
      .then(res => {
        if (res.data?.length > 0) setLatestAnalysisId(res.data[0].analysis_id)
      })
      .catch(() => {})
  }, [])

  // Fetch S2/S4 compare scores when modal opens
  useEffect(() => {
    if (!showCompare || !latestAnalysisId || compareList.length < 2) return
    setLoadingCompare(true)
    api.post('/recommendations/compare', {
      analysis_id: latestAnalysisId,
      product_ids: compareList.map(p => p.product_id)
    })
      .then(res => {
        setCompareScores(res.data.products || {})
        setCompareFaceShape(res.data.face_shape || null)
      })
      .catch(() => { setCompareScores({}); setCompareFaceShape(null) })
      .finally(() => setLoadingCompare(false))
  }, [showCompare, latestAnalysisId, compareList])

  const handleClickLink = async (product, linkId, platform, url) => {
    trackClick(product, platform, url)
    try { await api.post(`/commission/click/${linkId}`) } catch {}
    window.open(url, '_blank')
  }

  const handleViewSimilar = async (product) => {
    trackSimilarView(product)
    setSelectedProduct(product)
    setLoadingSimilar(true)
    try {
      const res = await api.get(`/products/similar/${product.product_id}?limit=6`)
      setSimilarProducts(res.data.similar || [])
    } catch {
      setSimilarProducts([])
    } finally {
      setLoadingSimilar(false)
    }
  }

  const closeSimilar = () => {
    setSelectedProduct(null)
    setSimilarProducts([])
  }

  const toggleCompare = (product) => {
    setCompareList(prev => {
      const exists = prev.find(p => p.product_id === product.product_id)
      if (exists) return prev.filter(p => p.product_id !== product.product_id)
      if (prev.length >= 3) return prev // สูงสุด 3 ตัว
      return [...prev, product]
    })
  }

  const isInCompare = (productId) => compareList.some(p => p.product_id === productId)

  const toggleFavorite = async (productId) => {
    if (!user) return
    const isFav = favoriteIds.has(productId)
    // Optimistic update
    setFavoriteIds(prev => {
      const next = new Set(prev)
      if (isFav) next.delete(productId)
      else next.add(productId)
      return next
    })
    try {
      if (isFav) await favoritesApi.remove(productId)
      else await favoritesApi.add(productId)
    } catch {
      // Revert on error
      setFavoriteIds(prev => {
        const next = new Set(prev)
        if (isFav) next.add(productId)
        else next.delete(productId)
        return next
      })
    }
  }

  const clearFilters = () => {
    setSearch('')
    setSelectedCategory(null)
    setSelectedBrand(null)
    setSelectedColor(null)
    setSort('newest')
  }

  const openDetail = async (product) => {
    setDetailProduct(product)
    setLoadingReviews(true)
    setReviewForm({ rating: 0, comment: '' })
    try {
      const [revRes, sumRes] = await Promise.all([
        reviewsApi.getForProduct(product.product_id),
        reviewsApi.getSummary(product.product_id),
      ])
      setReviews(revRes.data)
      setReviewSummary(sumRes.data)
    } catch {
      setReviews([])
      setReviewSummary(null)
    } finally {
      setLoadingReviews(false)
    }
  }

  const closeDetail = () => {
    setDetailProduct(null)
    setReviews([])
    setReviewSummary(null)
  }

  const refreshReviews = async (productId) => {
    const [revRes, sumRes] = await Promise.all([
      reviewsApi.getForProduct(productId),
      reviewsApi.getSummary(productId),
    ])
    setReviews(revRes.data)
    setReviewSummary(sumRes.data)
  }

  const submitReview = async () => {
    if (!user || reviewForm.rating === 0) return
    setSubmittingReview(true)
    try {
      await reviewsApi.submit(detailProduct.product_id, {
        rating: reviewForm.rating,
        comment: reviewForm.comment || null,
      })
      await refreshReviews(detailProduct.product_id)
      setReviewForm({ rating: 0, comment: '' })
    } catch { }
    finally { setSubmittingReview(false) }
  }

  const deleteReview = async () => {
    if (!user) return
    try {
      await reviewsApi.remove(detailProduct.product_id)
      await refreshReviews(detailProduct.product_id)
    } catch { }
  }

  const hasFilters = search || selectedCategory || selectedBrand || selectedColor || sort !== 'newest'

  const PERSONAL_COLORS = [
    { id: 'spring', label: 'สปริง (โทนอุ่นสว่าง)', emoji: '🌸', color: '#fbbf24' },
    { id: 'summer', label: 'ซัมเมอร์ (โทนเย็นนุ่ม)', emoji: '🌊', color: '#60a5fa' },
    { id: 'autumn', label: 'ออทั่ม (โทนอุ่นเข้ม)', emoji: '🍂', color: '#f97316' },
    { id: 'winter', label: 'วินเทอร์ (โทนเย็นสด)', emoji: '❄️', color: '#8b5cf6' },
  ]

  const FACE_SHAPE_TIPS_TH = {
    oval:     { contour: 'คอนทัวร์เบาๆ บริเวณโหนกแก้ม', styles: 'เหมาะกับทุกทรง' },
    round:    { contour: 'คอนทัวร์แนวกราม และขมับ', styles: 'กรอบเหลี่ยม, หน้าม้าปัดข้าง' },
    square:   { contour: 'ทำมุมกรามให้นุ่มลง', styles: 'ผมเลเยอร์, แสกข้าง' },
    heart:    { contour: 'คอนทัวร์ข้างหน้าผาก', styles: 'หน้าม้าปัดข้าง, เลเยอร์ระดับคาง' },
    oblong:   { contour: 'เพิ่มความกว้างที่โหนกแก้ม', styles: 'หน้าม้าปัดข้าง, ผมเลเยอร์' },
    diamond:  { contour: 'ลดความเด่นของโหนกแก้ม', styles: 'หน้าม้าปัดข้าง, ทรงระดับคาง' },
    triangle: { contour: 'เพิ่มความกว้างที่ขมับ', styles: 'เพิ่มวอลุ่มด้านบน, หน้าม้าปัดข้าง' },
  }

  const FACE_SHAPE_NAMES_TH = {
    oval: 'รูปไข่', round: 'กลม', square: 'เหลี่ยม', heart: 'หัวใจ',
    oblong: 'ยาว', diamond: 'เพชร', triangle: 'สามเหลี่ยม',
  }

  return (
    <div className="pd">
      {/* Header */}
      <div className="pd-header">
        <h1 className="pd-title">สินค้าเครื่องสำอาง</h1>
        <p className="pd-subtitle">คัดสรรเครื่องสำอางคุณภาพดีจากแบรนด์ชั้นนำ พร้อมลิงก์ซื้อได้ทันที</p>
      </div>

      {/* Similar Products Modal */}
      {selectedProduct && (
        <div className="pd-similar-overlay" onClick={closeSimilar}>
          <div className="pd-similar-modal" onClick={e => e.stopPropagation()}>
            <div className="pd-similar-header">
              <button className="pd-similar-back" onClick={closeSimilar}><ArrowLeft size={18} /></button>
              <div>
                <h2 className="pd-similar-title">
                  <Sparkles size={16} /> สินค้าที่คล้ายกัน
                </h2>
                <p className="pd-similar-subtitle">แนะนำโดยอัลกอริทึมวิเคราะห์ความคล้ายคลึง</p>
              </div>
            </div>

            {/* Target Product */}
            <div className="pd-similar-target">
              <span className="pd-similar-label">สินค้าที่เลือก</span>
              <div className="pd-similar-target-card">
                {selectedProduct.image_url && <img src={selectedProduct.image_url} alt="" className="pd-similar-target-img" />}
                <div>
                  {selectedProduct.brand_name && <span className="pd-card-brand">{selectedProduct.brand_name}</span>}
                  <h4 className="pd-similar-target-name">{selectedProduct.name}</h4>
                  {selectedProduct.price > 0 && <span className="pd-similar-target-price">฿{selectedProduct.price.toLocaleString()}</span>}
                </div>
              </div>
            </div>

            {/* Similar Results */}
            {loadingSimilar ? (
              <div className="pd-similar-loading"><Loader2 size={20} className="pd-spin" /> กำลังวิเคราะห์...</div>
            ) : similarProducts.length === 0 ? (
              <p className="pd-similar-empty">ไม่พบสินค้าที่คล้ายกัน</p>
            ) : (
              <div className="pd-similar-grid">
                {similarProducts.map(p => (
                  <div key={p.product_id} className="pd-card pd-card--similar">
                    <div className="pd-card-img-wrap">
                      {p.image_url ? (
                        <img src={p.image_url} alt={p.name} className="pd-card-img" />
                      ) : (
                        <div className="pd-card-placeholder"><ShoppingBag size={28} /></div>
                      )}
                      {p.price > 0 && <span className="pd-card-price">฿{p.price.toLocaleString()}</span>}
                      <span className="pd-card-score">{Math.round(p.similarity_score * 100)}% คล้าย</span>
                    </div>
                    <div className="pd-card-body">
                      {p.brand_name && <span className="pd-card-brand">{p.brand_name}</span>}
                      <h3 className="pd-card-name">{p.name}</h3>
                      {p.links?.length > 0 && (
                        <div className="pd-card-links">
                          {p.links.map(link => (
                            <button key={link.link_id} onClick={() => handleClickLink(product, link.link_id, link.platform, link.url)}
                              className={`pd-link pd-link--${link.platform}`}>
                              <ExternalLink size={10} /> {link.platform}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Product Detail + Review Modal */}
      {detailProduct && (
        <div className="pd-similar-overlay" onClick={closeDetail}>
          <div className="pd-detail-modal" onClick={e => e.stopPropagation()}>
            <div className="pd-similar-header">
              <button className="pd-similar-back" onClick={closeDetail}><ArrowLeft size={18} /></button>
              <h2 className="pd-similar-title"><MessageSquare size={16} /> รายละเอียดและรีวิว</h2>
            </div>

            {/* Product Info */}
            <div className="pd-detail-header">
              {detailProduct.image_url && <img src={detailProduct.image_url} alt="" className="pd-detail-img" />}
              <div className="pd-detail-info">
                {detailProduct.brand_name && <span className="pd-card-brand">{detailProduct.brand_name}</span>}
                <h3 className="pd-detail-name">{detailProduct.name}</h3>
                {detailProduct.price > 0 && <span className="pd-detail-price">฿{detailProduct.price.toLocaleString()}</span>}
                {detailProduct.personal_color && (
                  <div className="pd-card-seasons">
                    {detailProduct.personal_color.split(',').map(s => {
                      const pc = PERSONAL_COLORS.find(c => c.id === s.trim())
                      return pc ? <span key={pc.id} className={`pd-season-dot pd-season-dot--${pc.id}`} title={pc.label}>{pc.emoji}</span> : null
                    })}
                  </div>
                )}
                {detailProduct.links?.length > 0 && (
                  <div className="pd-card-links">
                    {detailProduct.links.map(link => (
                      <button key={link.link_id}
                        onClick={() => handleClickLink(detailProduct, link.link_id, link.platform, link.url)}
                        className={`pd-link pd-link--${link.platform}`}>
                        <ExternalLink size={11} /> {link.platform.charAt(0).toUpperCase() + link.platform.slice(1)}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Review Summary */}
            {loadingReviews ? (
              <div className="pd-review-loading"><Loader2 size={20} className="pd-spin" /> กำลังโหลดรีวิว...</div>
            ) : reviewSummary && (
              <div className="pd-review-summary">
                <div className="pd-review-avg-section">
                  <span className="pd-review-avg">{reviewSummary.average_rating > 0 ? reviewSummary.average_rating.toFixed(1) : '-'}</span>
                  <div className="pd-review-avg-detail">
                    <div className="pd-review-stars">
                      {[1, 2, 3, 4, 5].map(i => (
                        <Star key={i} size={14} className={i <= Math.round(reviewSummary.average_rating) ? 'pd-review-star--filled' : 'pd-review-star--empty'} fill={i <= Math.round(reviewSummary.average_rating) ? 'currentColor' : 'none'} />
                      ))}
                    </div>
                    <span className="pd-review-total">{reviewSummary.total_count} รีวิว</span>
                  </div>
                </div>
                {reviewSummary.total_count > 0 && (
                  <div className="pd-review-dist">
                    {[5, 4, 3, 2, 1].map(star => (
                      <div key={star} className="pd-review-dist-row">
                        <span className="pd-review-dist-label">{star}</span>
                        <div className="pd-review-dist-bar">
                          <div className="pd-review-dist-fill" style={{ width: `${reviewSummary.total_count > 0 ? (reviewSummary.distribution[star] / reviewSummary.total_count) * 100 : 0}%` }} />
                        </div>
                        <span className="pd-review-dist-count">{reviewSummary.distribution[star]}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Review Form (auth only) */}
            {user && !loadingReviews && (
              <div className="pd-review-form">
                <h4 className="pd-review-form-title">เขียนรีวิว</h4>
                <div className="pd-review-form-stars">
                  {[1, 2, 3, 4, 5].map(i => (
                    <button key={i} className="pd-review-star-btn" onClick={() => setReviewForm(f => ({ ...f, rating: i }))}>
                      <Star size={22} className={i <= reviewForm.rating ? 'pd-review-star--filled' : 'pd-review-star--empty'} fill={i <= reviewForm.rating ? 'currentColor' : 'none'} />
                    </button>
                  ))}
                </div>
                <textarea className="pd-review-textarea" rows={3} placeholder="แชร์ประสบการณ์ของคุณ..." value={reviewForm.comment} onChange={e => setReviewForm(f => ({ ...f, comment: e.target.value }))} />
                <button className="pd-review-submit" onClick={submitReview} disabled={submittingReview || reviewForm.rating === 0}>
                  {submittingReview ? <Loader2 size={14} className="pd-spin" /> : <Star size={14} />}
                  ส่งรีวิว
                </button>
              </div>
            )}

            {/* Review List */}
            {!loadingReviews && (
              <div className="pd-review-list">
                {reviews.length === 0 ? (
                  <div className="pd-review-empty">
                    <MessageSquare size={24} />
                    <p>ยังไม่มีรีวิว</p>
                  </div>
                ) : reviews.map(r => (
                  <div key={r.review_id} className="pd-review-item">
                    <div className="pd-review-item-header">
                      <div className="pd-review-author">
                        <span className="pd-review-author-name">{r.username}</span>
                        {r.is_verified === 1 && <ShieldCheck size={12} className="pd-review-verified" />}
                      </div>
                      <span className="pd-review-date">{r.created_at?.split(' ')[0]}</span>
                    </div>
                    <div className="pd-review-stars">
                      {[1, 2, 3, 4, 5].map(i => (
                        <Star key={i} size={12} className={i <= r.rating ? 'pd-review-star--filled' : 'pd-review-star--empty'} fill={i <= r.rating ? 'currentColor' : 'none'} />
                      ))}
                    </div>
                    {r.comment && <p className="pd-review-comment">{r.comment}</p>}
                    {user && r.user_id === user.user_id && (
                      <button className="pd-review-delete" onClick={deleteReview}><Trash2 size={12} /> ลบรีวิว</button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Search & Filter Bar */}
      <div className="pd-toolbar">
        <div className="pd-search">
          <Search size={16} className="pd-search-icon" />
          <input type="text" placeholder="ค้นหาสินค้า..." value={search}
            onChange={(e) => setSearch(e.target.value)} className="pd-search-input" />
          {search && <button className="pd-search-clear" onClick={() => setSearch('')}><X size={14} /></button>}
        </div>
        <button className="pd-filter-toggle" onClick={() => setShowFilters(!showFilters)}>
          <SlidersHorizontal size={15} /> <span>กรอง</span>
          <ChevronDown size={14} style={{ transform: showFilters ? 'rotate(180deg)' : 'none', transition: '.2s' }} />
        </button>
      </div>

      {/* Filter Panel */}
      {showFilters && (
        <div className="pd-filters">
          <div className="pd-filter-group">
            <span className="pd-filter-label">หมวดหมู่</span>
            <div className="pd-filter-chips">
              <button className={`pd-chip ${!selectedCategory ? 'pd-chip--active' : ''}`}
                onClick={() => setSelectedCategory(null)}>ทั้งหมด</button>
              {categories.map(cat => (
                <button key={cat.category_id}
                  className={`pd-chip ${selectedCategory === cat.category_id ? 'pd-chip--active' : ''}`}
                  onClick={() => setSelectedCategory(cat.category_id)}>{cat.name}</button>
              ))}
            </div>
          </div>

          <div className="pd-filter-group">
            <span className="pd-filter-label">แบรนด์</span>
            <div className="pd-filter-chips">
              <button className={`pd-chip ${!selectedBrand ? 'pd-chip--active' : ''}`}
                onClick={() => setSelectedBrand(null)}>ทั้งหมด</button>
              {brands.map(b => (
                <button key={b.brand_id}
                  className={`pd-chip ${selectedBrand === b.brand_id ? 'pd-chip--active' : ''}`}
                  onClick={() => setSelectedBrand(b.brand_id)}>{b.name}</button>
              ))}
            </div>
          </div>

          <div className="pd-filter-group">
            <span className="pd-filter-label">Personal Color</span>
            <div className="pd-filter-chips">
              <button className={`pd-chip ${!selectedColor ? 'pd-chip--active' : ''}`}
                onClick={() => setSelectedColor(null)}>ทั้งหมด</button>
              {PERSONAL_COLORS.map(pc => (
                <button key={pc.id}
                  className={`pd-chip pd-chip--color ${selectedColor === pc.id ? 'pd-chip--active' : ''}`}
                  onClick={() => setSelectedColor(pc.id)}>
                  {pc.emoji} {pc.label}
                </button>
              ))}
            </div>
          </div>

          <div className="pd-filter-group">
            <span className="pd-filter-label">เรียงตาม</span>
            <div className="pd-filter-chips">
              {[
                { id: 'newest', label: 'ใหม่สุด' },
                { id: 'price_asc', label: 'ราคาต่ำ → สูง' },
                { id: 'price_desc', label: 'ราคาสูง → ต่ำ' },
              ].map(s => (
                <button key={s.id} className={`pd-chip ${sort === s.id ? 'pd-chip--active' : ''}`}
                  onClick={() => setSort(s.id)}>{s.label}</button>
              ))}
            </div>
          </div>

          {hasFilters && <button className="pd-clear-btn" onClick={clearFilters}>ล้างตัวกรองทั้งหมด</button>}
        </div>
      )}

      {/* Result count */}
      <div className="pd-result-bar">
        <span className="pd-result-count">{loading ? 'กำลังโหลด...' : `พบ ${products.length} สินค้า`}</span>
      </div>

      {/* Product Grid */}
      <div className="pd-content">
        {loading ? (
          <div className="pd-grid">{[...Array(8)].map((_, i) => <SkeletonCard key={i} />)}</div>
        ) : products.length === 0 ? (
          <div className="pd-empty">
            <div className="pd-empty-icon"><ShoppingBag size={36} /></div>
            <p className="pd-empty-text">ไม่พบสินค้า</p>
            <p className="pd-empty-sub">ลองเปลี่ยนคำค้นหาหรือตัวกรอง</p>
            {hasFilters && <button className="pd-empty-btn" onClick={clearFilters}>ล้างตัวกรอง</button>}
          </div>
        ) : (
          <div className="pd-grid">
            {products.map(product => (
              <div key={product.product_id} className="pd-card" onClick={() => openDetail(product)} onMouseEnter={() => trackProductView(product)} style={{ cursor: 'pointer' }}>
                <div className="pd-card-img-wrap">
                  {product.image_url ? (
                    <img src={product.image_url} alt={product.name} className="pd-card-img" />
                  ) : (
                    <div className="pd-card-placeholder"><ShoppingBag size={36} /></div>
                  )}
                  {product.price > 0 && <span className="pd-card-price">฿{product.price.toLocaleString()}</span>}
                  {product.category_name && <span className="pd-card-cat">{product.category_name}</span>}
                  {user && (
                    <button
                      className={`pd-fav-btn ${favoriteIds.has(product.product_id) ? 'pd-fav-btn--active' : ''}`}
                      onClick={(e) => { e.stopPropagation(); toggleFavorite(product.product_id) }}
                      aria-label={favoriteIds.has(product.product_id) ? 'นำออกจากรายการโปรด' : 'เพิ่มในรายการโปรด'}
                    >
                      <Heart size={18} fill={favoriteIds.has(product.product_id) ? 'currentColor' : 'none'} />
                    </button>
                  )}
                </div>
                <div className="pd-card-body">
                  {product.brand_name && <span className="pd-card-brand">{product.brand_name}</span>}
                  <h3 className="pd-card-name">{product.name}</h3>
                  {product.description && <p className="pd-card-desc">{product.description}</p>}
                  {product.personal_color && (
                    <div className="pd-card-seasons">
                      {product.personal_color.split(',').map(s => {
                        const pc = PERSONAL_COLORS.find(c => c.id === s.trim())
                        return pc ? <span key={pc.id} className={`pd-season-dot pd-season-dot--${pc.id}`} title={pc.label}>{pc.emoji}</span> : null
                      })}
                    </div>
                  )}
                  {product.concerns?.length > 0 && (
                    <div className="pd-card-concerns">
                      {product.concerns.map(c => {
                        const isMatch = userConcernIds.has(c.concern_id)
                        return (
                          <span key={c.concern_id} className={`pd-concern-badge ${isMatch ? 'pd-concern-badge--match' : ''}`}>
                            {isMatch && <ShieldCheck size={10} />}
                            {c.name}
                          </span>
                        )
                      })}
                    </div>
                  )}
                  <div className="pd-card-actions">
                    {product.links?.length > 0 && (
                      <div className="pd-card-links">
                        {product.links.map(link => (
                          <button key={link.link_id} onClick={(e) => { e.stopPropagation(); handleClickLink(product, link.link_id, link.platform, link.url) }}
                            className={`pd-link pd-link--${link.platform}`}>
                            <ExternalLink size={11} /> {link.platform.charAt(0).toUpperCase() + link.platform.slice(1)}
                          </button>
                        ))}
                      </div>
                    )}
                    <div className="pd-card-btns">
                      <button className="pd-similar-btn" onClick={(e) => { e.stopPropagation(); handleViewSimilar(product) }}>
                        <Sparkles size={12} /> สินค้าคล้ายกัน
                      </button>
                      <button className={`pd-compare-btn ${isInCompare(product.product_id) ? 'pd-compare-btn--active' : ''}`}
                        onClick={(e) => { e.stopPropagation(); toggleCompare(product) }}>
                        {isInCompare(product.product_id) ? <><Check size={12} /> เลือกแล้ว</> : <><Scale size={12} /> เปรียบเทียบ</>}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Floating Compare Bar */}
      {compareList.length > 0 && !showCompare && (
        <div className="pd-compare-bar">
          <span className="pd-compare-bar-text">เลือกแล้ว {compareList.length}/3 ชิ้น</span>
          <button className="pd-compare-bar-btn" onClick={() => setShowCompare(true)} disabled={compareList.length < 2}>
            <Scale size={14} /> เปรียบเทียบ
          </button>
          <button className="pd-compare-bar-clear" onClick={() => setCompareList([])}>
            <X size={14} />
          </button>
        </div>
      )}

      {/* Compare Table Modal */}
      {showCompare && (
        <div className="pd-similar-overlay" onClick={() => setShowCompare(false)}>
          <div className="pd-compare-modal" onClick={e => e.stopPropagation()}>
            <div className="pd-similar-header">
              <button className="pd-similar-back" onClick={() => setShowCompare(false)}><ArrowLeft size={18} /></button>
              <h2 className="pd-similar-title"><Scale size={16} /> เปรียบเทียบสินค้า</h2>
            </div>

            <div className="pd-compare-table-wrap">
              <table className="pd-compare-table">
                <thead>
                  <tr>
                    <th className="pd-compare-label-col"></th>
                    {compareList.map(p => (
                      <th key={p.product_id} className="pd-compare-product-col">
                        {p.image_url && <img src={p.image_url} alt="" className="pd-compare-img" />}
                        <button className="pd-compare-remove" onClick={() => { toggleCompare(p); if (compareList.length <= 2) setShowCompare(false); }}>
                          <X size={12} />
                        </button>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className="pd-compare-label">ชื่อสินค้า</td>
                    {compareList.map(p => <td key={p.product_id} className="pd-compare-val pd-compare-val--name">{p.name}</td>)}
                  </tr>
                  <tr>
                    <td className="pd-compare-label">แบรนด์</td>
                    {compareList.map(p => <td key={p.product_id} className="pd-compare-val">{p.brand_name || '-'}</td>)}
                  </tr>
                  <tr>
                    <td className="pd-compare-label">ราคา</td>
                    {compareList.map(p => <td key={p.product_id} className="pd-compare-val pd-compare-val--price">฿{p.price?.toLocaleString() || '-'}</td>)}
                  </tr>
                  <tr>
                    <td className="pd-compare-label">หมวดหมู่</td>
                    {compareList.map(p => <td key={p.product_id} className="pd-compare-val">{p.category_name || '-'}</td>)}
                  </tr>
                  <tr>
                    <td className="pd-compare-label">เหมาะกับ</td>
                    {compareList.map(p => (
                      <td key={p.product_id} className="pd-compare-val">
                        {p.personal_color ? p.personal_color.split(',').map(s => {
                          const pc = PERSONAL_COLORS.find(c => c.id === s.trim())
                          return pc ? <span key={pc.id} className="pd-compare-season">{pc.emoji} {pc.label.split(' ')[0]}</span> : null
                        }) : '-'}
                      </td>
                    ))}
                  </tr>
                  {latestAnalysisId && (
                    <tr>
                      <td className="pd-compare-label">ความเข้ากันของสี</td>
                      {compareList.map(p => {
                        const score = compareScores[p.product_id]
                        const pct = score ? Math.round(score.match_pct) : null
                        return (
                          <td key={p.product_id} className="pd-compare-val">
                            {loadingCompare ? (
                              <span className="pd-compare-loading-text">กำลังคำนวณ...</span>
                            ) : pct !== null ? (
                              <div className="pd-compare-match">
                                <div className="pd-compare-match-bar">
                                  <div className="pd-compare-match-fill"
                                    style={{ width: `${pct}%`, background: pct >= 70 ? 'var(--pd-gold)' : pct >= 40 ? 'var(--pd-warm-gray)' : 'var(--pd-rose)' }} />
                                </div>
                                <span className="pd-compare-match-pct">{pct}%</span>
                              </div>
                            ) : (
                              <span className="pd-compare-no-data">ยังไม่ได้วิเคราะห์</span>
                            )}
                          </td>
                        )
                      })}
                    </tr>
                  )}
                  {compareFaceShape && FACE_SHAPE_TIPS_TH[compareFaceShape] && (
                    <tr>
                      <td className="pd-compare-label">เคล็ดลับตามรูปหน้า</td>
                      {compareList.map(p => {
                        const tips = FACE_SHAPE_TIPS_TH[compareFaceShape]
                        return (
                          <td key={p.product_id} className="pd-compare-val pd-compare-val--tips">
                            <div className="pd-compare-tips">
                              <span className="pd-compare-tips-shape">{FACE_SHAPE_NAMES_TH[compareFaceShape] || compareFaceShape}</span>
                              <span className="pd-compare-tips-contour">{tips.contour}</span>
                              <span className="pd-compare-tips-styles">{tips.styles}</span>
                            </div>
                          </td>
                        )
                      })}
                    </tr>
                  )}
                  <tr>
                    <td className="pd-compare-label">คำอธิบาย</td>
                    {compareList.map(p => <td key={p.product_id} className="pd-compare-val pd-compare-val--desc">{p.description || '-'}</td>)}
                  </tr>
                  <tr>
                    <td className="pd-compare-label">ซื้อได้ที่</td>
                    {compareList.map(p => (
                      <td key={p.product_id} className="pd-compare-val">
                        {p.links?.length > 0 ? (
                          <div className="pd-card-links">
                            {p.links.map(link => (
                              <button key={link.link_id} onClick={() => handleClickLink(p, link.link_id, link.platform, link.url)}
                                className={`pd-link pd-link--${link.platform}`}>
                                {link.platform}
                              </button>
                            ))}
                          </div>
                        ) : '-'}
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function SkeletonCard() {
  return (
    <div className="pd-card pd-card--skeleton">
      <div className="pd-skel-img" />
      <div className="pd-skel-body">
        <div className="pd-skel-line pd-skel-line--sm" />
        <div className="pd-skel-line pd-skel-line--lg" />
        <div className="pd-skel-line pd-skel-line--md" />
      </div>
    </div>
  )
}
