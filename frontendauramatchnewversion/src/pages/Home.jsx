import { Link } from 'react-router-dom'
import { useRef, useState, useEffect, useCallback } from 'react'
import { Cpu, Eye, Layers, Star, ArrowRight, Sparkles, Camera, ShoppingBag } from 'lucide-react'
import './Home.css'

/* ── DATA ── */
const BOXES = [
  { label: 'Face Shape', sub: 'Oval',     top: '15%', left: '48%', w: '20%', h: '14%' },
  { label: 'Skin Tone',  sub: 'Analysis', top: '42%', left: '52%', w: '22%', h: '16%' },
  { label: 'Personal',   sub: 'Color',    top: '64%', left: '32%', w: '20%', h: '14%' },
]

const SEASONS = [
  { name: 'Spring', th: 'สปริง',   bg: '#FFF8F0', desc: 'สีสดใส อบอุ่น มีชีวิตชีวา', colors: ['#FF6B6B','#FFA07A','#FFD700','#98FB98','#FF69B4'], text: '#c2793a' },
  { name: 'Summer', th: 'ซัมเมอร์', bg: '#F0F4FF', desc: 'สีนุ่มนวล เย็น พาสเทล',    colors: ['#B0C4DE','#DDA0DD','#F08080','#87CEEB','#E6E6FA'], text: '#5a6fa8' },
  { name: 'Autumn', th: 'ออทัมน์',  bg: '#FFF4E6', desc: 'สีอบอุ่น เข้ม ดิน',         colors: ['#8B4513','#D2691E','#CD853F','#B8860B','#A0522D'], text: '#8B4513' },
  { name: 'Winter', th: 'วินเทอร์', bg: '#F0F0F8', desc: 'สีเข้ม คม ตัดกัน',          colors: ['#191970','#8B0000','#006400','#4B0082','#2F4F4F'], text: '#2d2d5e' },
]

const REVIEWS = [
  { name: 'ณิชา ว.', avatar: '#f9a8d4', rating: 5, text: 'ระบบวิเคราะห์โครงหน้าแม่นมากเลย รู้ว่าตัวเองเป็น Autumn ทำให้เลือกลิปสีถูกต้องขึ้นมาก!' },
  { name: 'ปิ่น ส.', avatar: '#c4b5fd', rating: 5, text: 'ฟีเจอร์แต่งรูปสวยมาก ใช้งานง่าย แนะนำสินค้าได้ตรงกับโทนสีผิวเลยค่ะ' },
  { name: 'มิน ก.', avatar: '#6ee7b7', rating: 5, text: 'ลองใช้ Gemini AI แต่งรูปแล้วประทับใจมาก ได้ภาพสวยกว่าที่คิดไว้เยอะเลย' },
]

const PRODUCTS = [
  { name: 'Lip Velvet Matte',  brand: 'MAC',         price: '฿850',   color: '#c8434f' },
  { name: 'Liquid Foundation', brand: 'Fenty Beauty', price: '฿1,290', color: '#d4a47a' },
  { name: 'Blush Palette',     brand: 'NARS',         price: '฿1,100', color: '#e8a09a' },
  { name: 'Eyeshadow Quad',    brand: 'Urban Decay',  price: '฿1,650', color: '#8b6c7a' },
]

const STEPS = [
  { icon: Camera,      num: '01', title: 'อัปโหลดรูปภาพ',    desc: 'ถ่ายหรืออัปโหลดรูปใบหน้า รองรับทุกสัญชาติและเพศ' },
  { icon: Sparkles,    num: '02', title: 'AI วิเคราะห์ใบหน้า', desc: 'ตรวจจับโครงหน้า โทนสีผิว และ personal color ' },
  { icon: ShoppingBag, num: '03', title: 'รับคำแนะนำสินค้า',  desc: 'ลิสต์สินค้าพร้อมลิงก์ Shopee, TikTok, Lazada' },
]

/* ── SCROLL REVEAL HOOK ── */
function useScrollReveal() {
  const ref = useRef(null)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const obs = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) { el.classList.add('revealed'); obs.unobserve(el) } },
      { threshold: 0.12, rootMargin: '0px 0px -30px 0px' }
    )
    obs.observe(el)
    return () => obs.disconnect()
  }, [])
  return ref
}

function Reveal({ children, className = '', delay = 0 }) {
  const ref = useScrollReveal()
  return (
    <div ref={ref} className={`sr ${className}`} style={{ transitionDelay: `${delay}ms` }}>
      {children}
    </div>
  )
}

/* ── 3D TILT CARD ── */
function TiltCard({ children, className = '', intensity = 8 }) {
  const cardRef = useRef(null)
  const handleMove = useCallback((e) => {
    const card = cardRef.current
    if (!card) return
    const rect = card.getBoundingClientRect()
    const x = (e.clientX - rect.left) / rect.width - 0.5
    const y = (e.clientY - rect.top) / rect.height - 0.5
    card.style.transform = `perspective(800px) rotateY(${x * intensity}deg) rotateX(${-y * intensity}deg) scale3d(1.02, 1.02, 1.02)`
  }, [intensity])
  const handleLeave = useCallback(() => {
    if (cardRef.current) cardRef.current.style.transform = ''
  }, [])
  return (
    <div ref={cardRef} className={`tilt-card ${className}`}
      onMouseMove={handleMove} onMouseLeave={handleLeave}>
      {children}
    </div>
  )
}

/* ── MOUSE PARALLAX HOOK ── */
function useMouseParallax(ref, intensity = 0.015) {
  const [offset, setOffset] = useState({ x: 0, y: 0 })
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const handle = (e) => {
      const rect = el.getBoundingClientRect()
      const cx = rect.left + rect.width / 2
      const cy = rect.top + rect.height / 2
      setOffset({ x: (e.clientX - cx) * intensity, y: (e.clientY - cy) * intensity })
    }
    window.addEventListener('mousemove', handle)
    return () => window.removeEventListener('mousemove', handle)
  }, [ref, intensity])
  return offset
}

/* ════════════════════════════════════════
   MAIN COMPONENT
   ════════════════════════════════════════ */
export default function Home() {
  const heroRef = useRef(null)
  const mouse = useMouseParallax(heroRef, 0.012)

  return (
    <div className="home">

      {/* ── NAVBAR ── */}
      <header className="home-navbar">
        <div className="home-navbar-logo">
          <span className="logo-dot" />
          AuraMatch
        </div>
        <nav className="home-navbar-links">
          {['Explore','Your Skin','Analysis','AI Guidance','Philosophy'].map(n => (
            <a key={n} href="#">{n}</a>
          ))}
        </nav>
        <div className="home-navbar-cta">
          <Link to="/login" className="btn-outline">Contact Us</Link>
          <Link to="/register" className="btn-dark">Get Started</Link>
        </div>
      </header>

      {/* ── HERO ── */}
      <section className="hero-section" ref={heroRef}>

        {/* Trust Badge */}
        <div className="hero-trust">
          <div className="trust-badge">
            <div className="trust-avatars">
              {['#f9a8d4','#c4b5fd','#93c5fd','#6ee7b7'].map((c,i) => (
                <div key={i} className="trust-avatar" style={{ backgroundColor: c, zIndex: 4-i }}>
                  {['A','B','C','D'][i]}
                </div>
              ))}
            </div>
            <span className="trust-text">Trusted by <strong>10,000+</strong> users</span>
          </div>
        </div>

        {/* Left Text */}
        <div className="hero-left">
          <h1 className="hero-title">Discover<br />Your True<br /><span>Colors</span></h1>
          <p className="hero-desc">AI-powered facial analysis reveals your personal<br />color season and perfect cosmetic matches.</p>
          <div className="hero-btns">
            <Link to="/analyze" className="btn-analyze">
              <span>Analyze Skin</span>
              <ArrowRight size={16} />
            </Link>
            <Link to="/products" className="btn-outline-hero">Explore Products</Link>
          </div>
        </div>

        {/* Center Face with 3D parallax */}
        <div className="hero-face-wrap" style={{ transform: `translate(${mouse.x * 0.8}px, ${mouse.y * 0.8}px)` }}>
          <div className="hero-face-inner">
            <img src="/face-hero.webp" alt="AuraMatch" className="hero-face-img"
              onError={e => { e.target.style.display='none'; e.target.nextSibling.style.display='flex' }} />
            <div className="hero-face-fallback">วางรูปที่ public/face-hero.webp</div>

            {BOXES.map((box,i) => (
              <div key={i} className="det-box" style={{ top:box.top, left:box.left, width:box.w, height:box.h, animationDelay: `${1 + i * 0.2}s` }}>
                <span className="det-box-corner tl" /><span className="det-box-corner tr" />
                <span className="det-box-corner bl" /><span className="det-box-corner br" />
                <span className="det-box-dot" />
                <div className="det-box-label"><span>{box.label}</span><span>{box.sub}</span></div>
              </div>
            ))}

            <div className="hero-fade-bottom" />
            <div className="hero-fade-left" />
            <div className="hero-fade-right" />
          </div>
        </div>

        {/* Right Stats */}
        <div className="hero-stats">
          {[
            { icon: Cpu,    value: '95%', label: 'accurate skin\nanalysis' },
            { icon: Eye,    value: '30+', label: 'skin concerns\nanalyzed' },
            { icon: Layers, value: '4',   label: 'personal color\nseasons' },
          ].map((s,i) => (
            <div key={i} className="stat-item">
              <div className="stat-icon"><s.icon size={18} strokeWidth={1} color="#d1d5db" /></div>
              <div>
                <p className="stat-value">{s.value}</p>
                <p className="stat-label">{s.label.split('\n').map((l,j) => <span key={j}>{l}<br/></span>)}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── HOW IT WORKS ── */}
      <section className="how-section">
        <div className="how-left">
          <img src="/face2.webp" alt="AI Analysis"
            onError={e => { e.target.style.backgroundColor = '#f3f0ee' }} />
          <div className="how-overlay" />
          {[
            { label: 'FACE SHAPE',     top: '28%', left: '42%' },
            { label: 'SKIN TONE',      top: '52%', left: '30%' },
            { label: 'PERSONAL COLOR', top: '70%', left: '50%' },
          ].map((dot,i) => (
            <div key={i} className="how-dot" style={{ top: dot.top, left: dot.left }}>
              <div className="how-dot-circle" />
              <span className="how-dot-label">{dot.label}</span>
            </div>
          ))}
        </div>

        <div className="how-right">
          <Reveal>
            <h2 className="how-title">AI Analysis</h2>
            <p className="how-desc">
              AI doesn't promise perfection — it observes, learns, and adapts.
              Every scan interprets your unique facial structure and color,
              highlighting your best features.
            </p>
          </Reveal>
          <div className="how-arrow">
            <div className="how-arrow-line" />
            <svg width="12" height="8" viewBox="0 0 12 8" fill="none">
              <path d="M6 8L0 0H12L6 8Z" fill="#d1d5db" />
            </svg>
          </div>
          <div className="how-steps">
            {STEPS.map((s,i) => (
              <Reveal key={i} delay={i * 100}>
                <div className="how-step">
                  <div className="how-step-icon"><s.icon size={16} strokeWidth={1.5} /></div>
                  <span className="how-step-num">{s.num}</span>
                  <div>
                    <p className="how-step-title">{s.title}</p>
                    <p className="how-step-desc">{s.desc}</p>
                  </div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ── COLOR SEASONS ── */}
      <section className="seasons-section">
        <Reveal>
          <p className="section-label">PERSONAL COLOR</p>
          <h2 className="section-title">ค้นพบ Season ของคุณ</h2>
          <p className="section-sub">สีที่เหมาะกับคุณ ขึ้นอยู่กับโทนสีผิวและ undertone</p>
        </Reveal>
        <div className="seasons-grid">
          {SEASONS.map((s,i) => (
            <Reveal key={s.name} delay={i * 80}>
              <TiltCard className="season-card" intensity={6}>
                <div className="season-card-inner" style={{ backgroundColor: s.bg }}>
                  <p className="season-name" style={{ color: s.text }}>{s.name.toUpperCase()}</p>
                  <p className="season-th" style={{ color: s.text }}>{s.th}</p>
                  <div className="season-colors">
                    {s.colors.map((c,j) => (
                      <div key={j} className="season-color-dot" style={{ backgroundColor: c }} />
                    ))}
                  </div>
                  <p className="season-desc" style={{ color: s.text }}>{s.desc}</p>
                </div>
              </TiltCard>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ── PRODUCTS ── */}
      <section className="products-section">
        <div className="products-header">
          <Reveal>
            <div>
              <p className="section-label" style={{ textAlign:'left', marginBottom:'8px' }}>PRODUCTS</p>
              <h2 className="section-title" style={{ textAlign:'left', marginBottom:0 }}>สินค้าแนะนำ</h2>
            </div>
          </Reveal>
          <Reveal>
            <Link to="/products" className="products-header-link">
              ดูทั้งหมด <ArrowRight size={14} />
            </Link>
          </Reveal>
        </div>
        <div className="products-grid">
          {PRODUCTS.map((p,i) => (
            <Reveal key={i} delay={i * 80}>
              <TiltCard className="product-card" intensity={7}>
                <div className="product-img" style={{ backgroundColor: p.color + '15' }}>
                  <div className="product-orb-lg" style={{ backgroundColor: p.color + '40' }} />
                  <div className="product-orb-sm" style={{ backgroundColor: p.color + '25' }} />
                </div>
                <div className="product-info">
                  <p className="product-brand">{p.brand}</p>
                  <p className="product-name">{p.name}</p>
                  <p className="product-price">{p.price}</p>
                  <div className="product-platforms">
                    {['shopee','tiktok','lazada'].map(pl => (
                      <span key={pl} className="platform-tag">{pl}</span>
                    ))}
                  </div>
                </div>
              </TiltCard>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ── REVIEWS ── */}
      <section className="reviews-section">
        <Reveal>
          <p className="section-label">REVIEWS</p>
          <h2 className="section-title">ผู้ใช้พูดถึงเรา</h2>
        </Reveal>
        <div className="reviews-grid">
          {REVIEWS.map((r,i) => (
            <Reveal key={i} delay={i * 100}>
              <TiltCard className="review-card" intensity={5}>
                <div className="review-stars">
                  {[...Array(r.rating)].map((_,j) => (
                    <Star key={j} size={12} fill="#facc15" stroke="none" />
                  ))}
                </div>
                <p className="review-text">"{r.text}"</p>
                <div className="review-author">
                  <div className="review-avatar" style={{ backgroundColor: r.avatar }}>{r.name[0]}</div>
                  <p className="review-name">{r.name}</p>
                </div>
              </TiltCard>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ── CTA ── */}
      <section className="cta-section">
        <div className="cta-glow cta-glow-1" />
        <div className="cta-glow cta-glow-2" />
        <Reveal>
          <h2 className="cta-title">พร้อมค้นพบ<br />ตัวตนของคุณ?</h2>
          <p className="cta-desc">วิเคราะห์โครงหน้าและโทนสีผิวของคุณฟรี<br />ด้วย AI ที่รองรับทุกสัญชาติ</p>
          <Link to="/analyze" className="btn-white">เริ่มวิเคราะห์ตอนนี้</Link>
        </Reveal>
      </section>

      {/* ── FOOTER ── */}
      <footer className="home-footer">
        <div className="footer-grid">
          <div>
            <div className="footer-logo">
              <span className="logo-dot" />
              <span className="footer-logo-text">AuraMatch</span>
            </div>
            <p className="footer-desc">AI-powered facial analysis for personalized cosmetic recommendations.</p>
          </div>
          <div className="footer-col">
            <p className="footer-col-title">PRODUCT</p>
            {['วิเคราะห์ใบหน้า','สินค้าแนะนำ','Photo Editor','Gemini AI'].map(l => (
              <a key={l} href="#">{l}</a>
            ))}
          </div>
          <div className="footer-col">
            <p className="footer-col-title">COMPANY</p>
            {['เกี่ยวกับเรา','บล็อก','ติดต่อ','Privacy Policy'].map(l => (
              <a key={l} href="#">{l}</a>
            ))}
          </div>
          <div className="footer-col">
            <p className="footer-col-title">SOCIAL</p>
            <div className="footer-social">
              {['Instagram','TikTok','YouTube'].map(s => (
                <a key={s} href="#">{s}</a>
              ))}
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2026 AuraMatch. All rights reserved.</p>
        </div>
      </footer>

    </div>
  )
}
