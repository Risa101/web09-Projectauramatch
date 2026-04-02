import { useState, useRef } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../api/axios'
import { Upload, Loader2, ShoppingBag, ExternalLink, Sparkles, Camera, X } from 'lucide-react'
import { trackAnalysis } from '../services/tracker'
import './Analyze.css'

const FACE_SHAPE_TH = { oval: 'รูปไข่', round: 'กลม', square: 'เหลี่ยม', heart: 'หัวใจ', oblong: 'ยาว', diamond: 'เพชร', triangle: 'สามเหลี่ยม' }
const SKIN_TONE_TH = { fair: 'ขาวมาก', light: 'ขาว', medium: 'กลาง', tan: 'แทน', dark: 'คล้ำ', deep: 'เข้ม' }
const PERSONAL_COLOR_TH = { spring: 'Spring', summer: 'Summer', autumn: 'Autumn', winter: 'Winter' }

const SEASON_CSS = {
  spring: 'season-spring',
  summer: 'season-summer',
  autumn: 'season-autumn',
  winter: 'season-winter',
}

const SEASON_DOT_CSS = {
  spring: 'dot-spring',
  summer: 'dot-summer',
  autumn: 'dot-autumn',
  winter: 'dot-winter',
}

const PLATFORM_CSS = {
  shopee: 'platform-btn--shopee',
  tiktok: 'platform-btn--tiktok',
  lazada: 'platform-btn--lazada',
}

export default function Analyze() {
  const { user } = useAuth()
  const [image, setImage] = useState(null)
  const [preview, setPreview] = useState(null)
  const [gender, setGender] = useState('female')
  const [result, setResult] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(false)
  const [loadingRecs, setLoadingRecs] = useState(false)
  const fileRef = useRef(null)

  const handleFile = (e) => {
    const file = e.target.files[0]
    if (!file) return
    setImage(file)
    setPreview(URL.createObjectURL(file))
    setResult(null)
    setRecommendations([])
  }

  const handleAnalyze = async () => {
    if (!image) return
    setLoading(true)
    setRecommendations([])
    try {
      const formData = new FormData()
      formData.append('file', image)
      const res = await api.post(`/analysis/?gender=${gender}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setResult(res.data)
      trackAnalysis(res.data)

      // หลังวิเคราะห์เสร็จ → generate recommendations
      setLoadingRecs(true)
      const analysisId = res.data.analysis_id
      await api.post(`/recommendations/generate/${analysisId}`)
      const recsRes = await api.get(`/recommendations/${analysisId}`)
      setRecommendations(recsRes.data)
    } catch (err) {
      alert('เกิดข้อผิดพลาดในการวิเคราะห์')
    } finally {
      setLoading(false)
      setLoadingRecs(false)
    }
  }

  const handleClickLink = async (linkId, url) => {
    try {
      await api.post(`/commission/click/${linkId}`)
    } catch { /* ignore */ }
    window.open(url, '_blank')
  }

  const clearImage = () => {
    setImage(null)
    setPreview(null)
    setResult(null)
    setRecommendations([])
  }

  return (
    <div className="analyze-page">

      {/* ── Hero Header ── */}
      <div className="hero-wrapper">
        <div className="hero-bg-layer">
          <div className="hero-glow-purple" />
          <div className="hero-glow-pink" />
        </div>

        <div className="hero-content">
          <div className="hero-text-center">
            <div className="hero-badge">
              <Sparkles size={14} className="hero-badge-icon" />
              AI-Powered Analysis
            </div>
            <h1 className="hero-title">
              AI Face Analysis
            </h1>
            <p className="hero-subtitle">
              อัปโหลดรูปใบหน้าเพื่อวิเคราะห์โครงหน้า โทนสีผิว และค้นหา Personal Color ของคุณ
            </p>
          </div>
        </div>
      </div>

      {/* ── Main Content ── */}
      <div className="main-content">
        <div className="content-grid">

          {/* ── Left: Upload Area ── */}
          <div className="upload-column">

            {/* Drop Zone Card */}
            <div className="card">
              <div className="dropzone-wrapper">
                <div
                  onClick={() => fileRef.current.click()}
                  className={`dropzone ${preview ? 'dropzone--has-image' : 'dropzone--empty'}`}
                >
                  {preview ? (
                    <div className="preview-container">
                      <img src={preview} alt="preview" className="preview-image" />
                      <button
                        onClick={(e) => { e.stopPropagation(); clearImage() }}
                        className="clear-btn"
                      >
                        <X size={16} />
                      </button>
                    </div>
                  ) : (
                    <div className="dropzone-placeholder">
                      <div className="upload-icon-box">
                        <Upload size={32} />
                      </div>
                      <p className="dropzone-text-primary">
                        คลิกเพื่ออัปโหลดรูปภาพ
                      </p>
                      <p className="dropzone-text-secondary">
                        รองรับ JPG, PNG, WEBP
                      </p>
                      <div className="dropzone-hint">
                        <div className="dropzone-hint-item">
                          <Camera size={14} />
                          <span>ถ่ายหรืออัปโหลด</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                <input ref={fileRef} type="file" accept="image/*" className="file-input-hidden" onChange={handleFile} />
              </div>

              {/* Gender Selection */}
              <div className="gender-section">
                <label className="gender-label">
                  เพศ
                </label>
                <div className="gender-buttons">
                  {['female', 'male'].map(g => (
                    <button
                      key={g}
                      onClick={() => setGender(g)}
                      className={`gender-btn ${gender === g ? 'gender-btn--active' : 'gender-btn--inactive'}`}
                    >
                      {g === 'female' ? 'หญิง' : 'ชาย'}
                    </button>
                  ))}
                </div>
              </div>

              {/* Analyze Button */}
              <button
                onClick={handleAnalyze}
                disabled={!image || loading}
                className="analyze-btn"
              >
                {loading ? (
                  <>
                    <Loader2 size={18} className="icon-spin" />
                    <span>กำลังวิเคราะห์...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={18} />
                    <span>วิเคราะห์ใบหน้า</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* ── Right: Results ── */}
          <div>
            {result ? (
              <div className="card card--results">
                {/* Result Header */}
                <div className="result-header">
                  <div className="result-header-inner">
                    <div className="result-icon-box">
                      <Sparkles size={18} />
                    </div>
                    <div>
                      <h2 className="result-title">
                        ผลการวิเคราะห์
                      </h2>
                      <p className="result-subtitle">
                        Analysis Result
                      </p>
                    </div>
                  </div>
                </div>

                <div className="result-body">
                  {/* Personal Color - Featured */}
                  {result.personal_color && (
                    <div className="personal-color-box">
                      <p className="personal-color-label">
                        Personal Color
                      </p>
                      <span className={`personal-color-badge ${SEASON_CSS[result.personal_color] || ''}`}>
                        {PERSONAL_COLOR_TH[result.personal_color]}
                      </span>
                      <div className="color-dots">
                        {[0,1,2,3,4].map(i => (
                          <div key={i}
                            className={`color-dot ${SEASON_DOT_CSS[result.personal_color] || 'dot-default'}`}
                            style={{ opacity: 1 - i * 0.15 }}
                          />
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Detail Rows */}
                  <div className="detail-rows">
                    <ResultRow
                      label="โครงหน้า"
                      sublabel="Face Shape"
                      value={FACE_SHAPE_TH[result.face_shape] || result.face_shape}
                    />
                    <ResultRow
                      label="โทนสีผิว"
                      sublabel="Skin Tone"
                      value={SKIN_TONE_TH[result.skin_tone] || result.skin_tone}
                    />
                    <ResultRow
                      label="Undertone"
                      sublabel="อันเดอร์โทน"
                      value={result.skin_undertone}
                    />
                  </div>

                  {/* Confidence Score */}
                  {result.confidence_score && (
                    <div className="confidence-section">
                      <div className="confidence-header">
                        <div>
                          <p className="confidence-label">
                            ความแม่นยำ
                          </p>
                          <p className="confidence-sublabel">
                            Confidence Score
                          </p>
                        </div>
                        <span className="confidence-value">
                          {result.confidence_score}%
                        </span>
                      </div>
                      <div className="confidence-track">
                        <div
                          className="confidence-fill"
                          style={{ width: `${result.confidence_score}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              /* Empty State */
              <div className="card card--results">
                <div className="empty-state">
                  <div className="empty-icon-box">
                    <Sparkles size={32} />
                  </div>
                  <p className="empty-text">
                    ผลการวิเคราะห์จะแสดงที่นี่
                  </p>
                  <p className="empty-subtext">
                    อัปโหลดรูปภาพและกดวิเคราะห์เพื่อเริ่มต้น
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* ── Loading Recommendations ── */}
        {loadingRecs && (
          <div className="loading-recs">
            <div className="loading-recs-icon">
              <Loader2 size={22} className="icon-spin" />
            </div>
            <p className="loading-recs-text">
              กำลังค้นหาสินค้าที่เหมาะกับคุณ...
            </p>
          </div>
        )}

        {/* ── Product Recommendations ── */}
        {recommendations.length > 0 && (
          <div className="recs-section">
            <div className="recs-header">
              <div className="recs-header-left">
                <div className="recs-icon-box">
                  <ShoppingBag size={18} />
                </div>
                <div>
                  <h2 className="recs-title">
                    สินค้าแนะนำสำหรับคุณ
                  </h2>
                  <p className="recs-subtitle">
                    Personalized Recommendations
                  </p>
                </div>
              </div>
              <span className="recs-count">
                {recommendations.length} รายการ
              </span>
            </div>

            <div className="product-grid">
              {recommendations.map((rec) => (
                <div
                  key={rec.recommendation_id}
                  className="product-card"
                >
                  {/* Product Image */}
                  {rec.product.image_url ? (
                    <div className="product-image-wrapper">
                      <img
                        src={rec.product.image_url}
                        alt={rec.product.name}
                        className="product-image"
                      />
                      <div className="product-image-overlay" />
                    </div>
                  ) : (
                    <div className="product-placeholder">
                      <ShoppingBag size={40} />
                    </div>
                  )}

                  {/* Product Info */}
                  <div className="product-info">
                    {rec.product.brand && (
                      <p className="product-brand">
                        {rec.product.brand}
                      </p>
                    )}
                    <h3 className="product-name">
                      {rec.product.name}
                    </h3>
                    {rec.product.price && (
                      <p className="product-price">
                        ฿{rec.product.price.toLocaleString()}
                      </p>
                    )}

                    {/* Platform Links */}
                    {rec.product.links?.length > 0 && (
                      <div className="platform-links">
                        {rec.product.links.map((link) => (
                          <button
                            key={link.link_id}
                            onClick={() => handleClickLink(link.link_id, link.url)}
                            className={`platform-btn ${PLATFORM_CSS[link.platform] || 'platform-btn--default'}`}
                          >
                            {link.platform}
                            <ExternalLink size={10} />
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function ResultRow({ label, sublabel, value }) {
  return (
    <div className="result-row">
      <div>
        <span className="result-row-label">
          {label}
        </span>
        {sublabel && (
          <span className="result-row-sublabel">
            {sublabel}
          </span>
        )}
      </div>
      <span className="result-row-value">
        {value}
      </span>
    </div>
  )
}
