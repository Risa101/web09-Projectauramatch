import { useState, useEffect } from 'react'
import api from '../api/axios'
import { ShoppingBag, ExternalLink, Search, SlidersHorizontal, ChevronDown, X, Loader2, Sparkles, ArrowLeft, Scale, Check } from 'lucide-react'
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

  // Similar products (TF-IDF)
  const [selectedProduct, setSelectedProduct] = useState(null)
  const [similarProducts, setSimilarProducts] = useState([])
  const [loadingSimilar, setLoadingSimilar] = useState(false)

  const COSMETIC_CATEGORY_IDS = [1, 2, 3, 4, 5, 6, 7]

  useEffect(() => {
    api.get('/products/categories').then(res => {
      setCategories(res.data.filter(c => COSMETIC_CATEGORY_IDS.includes(c.category_id)))
    }).catch(() => {})
    api.get('/products/brands').then(res => setBrands(res.data)).catch(() => {})
  }, [])

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

  const clearFilters = () => {
    setSearch('')
    setSelectedCategory(null)
    setSelectedBrand(null)
    setSelectedColor(null)
    setSort('newest')
  }

  const hasFilters = search || selectedCategory || selectedBrand || selectedColor || sort !== 'newest'

  const PERSONAL_COLORS = [
    { id: 'spring', label: 'สปริง (โทนอุ่นสว่าง)', emoji: '🌸', color: '#fbbf24' },
    { id: 'summer', label: 'ซัมเมอร์ (โทนเย็นนุ่ม)', emoji: '🌊', color: '#60a5fa' },
    { id: 'autumn', label: 'ออทั่ม (โทนอุ่นเข้ม)', emoji: '🍂', color: '#f97316' },
    { id: 'winter', label: 'วินเทอร์ (โทนเย็นสด)', emoji: '❄️', color: '#8b5cf6' },
  ]

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
              <div key={product.product_id} className="pd-card" onMouseEnter={() => trackProductView(product)}>
                <div className="pd-card-img-wrap">
                  {product.image_url ? (
                    <img src={product.image_url} alt={product.name} className="pd-card-img" />
                  ) : (
                    <div className="pd-card-placeholder"><ShoppingBag size={36} /></div>
                  )}
                  {product.price > 0 && <span className="pd-card-price">฿{product.price.toLocaleString()}</span>}
                  {product.category_name && <span className="pd-card-cat">{product.category_name}</span>}
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
                  <div className="pd-card-actions">
                    {product.links?.length > 0 && (
                      <div className="pd-card-links">
                        {product.links.map(link => (
                          <button key={link.link_id} onClick={() => handleClickLink(product, link.link_id, link.platform, link.url)}
                            className={`pd-link pd-link--${link.platform}`}>
                            <ExternalLink size={11} /> {link.platform.charAt(0).toUpperCase() + link.platform.slice(1)}
                          </button>
                        ))}
                      </div>
                    )}
                    <div className="pd-card-btns">
                      <button className="pd-similar-btn" onClick={() => handleViewSimilar(product)}>
                        <Sparkles size={12} /> สินค้าคล้ายกัน
                      </button>
                      <button className={`pd-compare-btn ${isInCompare(product.product_id) ? 'pd-compare-btn--active' : ''}`}
                        onClick={() => toggleCompare(product)}>
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
