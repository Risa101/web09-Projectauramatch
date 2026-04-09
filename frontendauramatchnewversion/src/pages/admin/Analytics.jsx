import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { analyticsApi } from '../../api/axios'
import {
  ArrowLeft, Activity, Users, Monitor, TrendingUp,
  BarChart3, Search, ShoppingBag, Palette, SlidersHorizontal, Sparkles,
} from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import './Analytics.css'

const PERIODS = [
  { label: '7 วัน', value: 7 },
  { label: '30 วัน', value: 30 },
  { label: '90 วัน', value: 90 },
]

const CHART_COLORS = ['#8b5cf6', '#7c3aed', '#6d28d9', '#f472b6', '#ec4899', '#db2777', '#d946ef', '#a78bfa', '#c084fc']
const SEASON_COLORS = { spring: '#FDB813', summer: '#87CEEB', autumn: '#D2691E', winter: '#4169E1' }

const EVENT_LABELS = {
  product_view: 'ดูสินค้า',
  search: 'ค้นหา',
  filter: 'ใช้ตัวกรอง',
  click: 'คลิกซื้อ',
  similar_view: 'ดูสินค้าคล้าย',
  makeup_select: 'เลือกแต่งหน้า',
  preset_apply: 'ใช้ Preset',
  face_analysis: 'วิเคราะห์ใบหน้า',
  photo_download: 'ดาวน์โหลดรูป',
}

const SEASON_LABELS = {
  spring: 'Spring',
  summer: 'Summer',
  autumn: 'Autumn',
  winter: 'Winter',
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background: '#fff', border: '1px solid #e5e7eb', borderRadius: '0.5rem',
      padding: '0.5rem 0.75rem', fontSize: '0.8125rem', fontFamily: 'Prompt, sans-serif',
      boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)',
    }}>
      <p style={{ color: '#374151', fontWeight: 500 }}>{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color }}>
          {p.name || 'จำนวน'}: {p.value?.toLocaleString()}
        </p>
      ))}
    </div>
  )
}

export default function Analytics() {
  const [days, setDays] = useState(30)
  const [loading, setLoading] = useState(true)
  const [summary, setSummary] = useState(null)
  const [topProducts, setTopProducts] = useState([])
  const [topSearches, setTopSearches] = useState([])
  const [filterUsage, setFilterUsage] = useState([])
  const [makeupBehavior, setMakeupBehavior] = useState({ popular_colors: [], popular_presets: [] })
  const [personalColor, setPersonalColor] = useState([])
  const [funnel, setFunnel] = useState(null)

  useEffect(() => {
    setLoading(true)
    Promise.all([
      analyticsApi.getSummary(days),
      analyticsApi.getTopProducts(days),
      analyticsApi.getTopSearches(days),
      analyticsApi.getFilterUsage(days),
      analyticsApi.getMakeupBehavior(days),
      analyticsApi.getPersonalColor(days),
      analyticsApi.getClickFunnel(days),
    ])
      .then(([s, p, q, f, m, c, fn]) => {
        setSummary(s.data)
        setTopProducts(p.data)
        setTopSearches(q.data)
        setFilterUsage(f.data)
        setMakeupBehavior(m.data)
        setPersonalColor(c.data)
        setFunnel(fn.data)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [days])

  if (loading) {
    return (
      <div className="analytics-page">
        <div className="analytics-container">
          <div className="analytics-loading">กำลังโหลดข้อมูล...</div>
        </div>
      </div>
    )
  }

  const eventData = (summary?.event_breakdown || []).map(e => ({
    name: EVENT_LABELS[e.event] || e.event,
    count: e.count,
  }))

  const productData = topProducts.slice(0, 8).map(p => ({
    name: (p.product_name || '').replace(/^"|"$/g, '').slice(0, 25),
    views: p.views,
  }))

  const searchData = topSearches.slice(0, 8).map(s => ({
    name: (s.query || '').replace(/^"|"$/g, ''),
    count: s.count,
  }))

  const seasonData = personalColor.map(c => ({
    name: SEASON_LABELS[c.season?.replace(/^"|"$/g, '')] || c.season,
    value: c.count,
    season: (c.season || '').replace(/^"|"$/g, ''),
  }))

  const presetData = (makeupBehavior.popular_presets || []).slice(0, 8).map(p => ({
    name: (p.preset || '').replace(/^"|"$/g, ''),
    count: p.count,
  }))

  const funnelMax = funnel?.product_views || 1

  return (
    <div className="analytics-page">
      <div className="analytics-container">

        {/* Header */}
        <div className="analytics-header">
          <Link to="/admin" className="analytics-back">
            <ArrowLeft size={16} />
            กลับ Dashboard
          </Link>
          <div className="analytics-header__row">
            <div className="analytics-header__accent" />
            <h1 className="analytics-header__title">วิเคราะห์พฤติกรรมผู้ใช้</h1>
          </div>
          <p className="analytics-header__subtitle">
            สถิติการใช้งานและพฤติกรรมของผู้ใช้ในระบบ
          </p>
        </div>

        {/* Period Selector */}
        <div className="analytics-period">
          {PERIODS.map(p => (
            <button
              key={p.value}
              className={`analytics-period__btn ${days === p.value ? 'analytics-period__btn--active' : ''}`}
              onClick={() => setDays(p.value)}
            >
              {p.label}
            </button>
          ))}
        </div>

        {/* Summary Stat Cards */}
        <div className="analytics-stats">
          <StatCard
            label="อีเว้นท์ทั้งหมด"
            value={summary?.total_events?.toLocaleString() ?? '0'}
            icon={<Activity size={18} />}
            variant="purple"
          />
          <StatCard
            label="ผู้ใช้ที่ไม่ซ้ำ"
            value={summary?.unique_users?.toLocaleString() ?? '0'}
            icon={<Users size={18} />}
            variant="pink"
          />
          <StatCard
            label="เซสชัน"
            value={summary?.unique_sessions?.toLocaleString() ?? '0'}
            icon={<Monitor size={18} />}
            variant="fuchsia"
          />
          <StatCard
            label="อัตราคลิกซื้อ"
            value={`${funnel?.view_to_click_rate ?? 0}%`}
            icon={<TrendingUp size={18} />}
            variant="blue"
          />
        </div>

        {/* Chart Grid */}
        <div className="analytics-grid">

          {/* Event Breakdown */}
          <ChartCard title="ประเภทอีเว้นท์" icon={<BarChart3 size={16} />}>
            {eventData.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={eventData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                  <XAxis dataKey="name" tick={{ fontSize: 11, fontFamily: 'Prompt' }} angle={-35} textAnchor="end" height={70} />
                  <YAxis tick={{ fontSize: 11, fontFamily: 'Prompt' }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="count" name="จำนวน" radius={[4, 4, 0, 0]}>
                    {eventData.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : <p className="analytics-empty">ยังไม่มีข้อมูล</p>}
          </ChartCard>

          {/* Click Funnel */}
          <ChartCard title="Conversion Funnel" icon={<TrendingUp size={16} />}>
            {funnel && funnel.product_views > 0 ? (
              <div className="analytics-funnel">
                <FunnelStep label="ดูสินค้า" count={funnel.product_views} max={funnelMax} variant="views" />
                <FunnelStep label="ดูสินค้าคล้ายกัน" count={funnel.similar_views} max={funnelMax} variant="similar" />
                <FunnelStep label="คลิกซื้อ" count={funnel.purchase_clicks} max={funnelMax} variant="clicks" />
                <div className="analytics-funnel__rate">
                  <TrendingUp size={14} />
                  อัตรา View → Click: {funnel.view_to_click_rate}%
                </div>
              </div>
            ) : <p className="analytics-empty">ยังไม่มีข้อมูล</p>}
          </ChartCard>

          {/* Top Products */}
          <ChartCard title="สินค้ายอดนิยม" icon={<ShoppingBag size={16} />}>
            {productData.length > 0 ? (
              <ResponsiveContainer width="100%" height={Math.max(200, productData.length * 36)}>
                <BarChart data={productData} layout="vertical" margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                  <XAxis type="number" tick={{ fontSize: 11, fontFamily: 'Prompt' }} />
                  <YAxis dataKey="name" type="category" width={140} tick={{ fontSize: 11, fontFamily: 'Prompt' }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="views" name="เข้าชม" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : <p className="analytics-empty">ยังไม่มีข้อมูล</p>}
          </ChartCard>

          {/* Top Searches */}
          <ChartCard title="คำค้นหายอดนิยม" icon={<Search size={16} />}>
            {searchData.length > 0 ? (
              <ResponsiveContainer width="100%" height={Math.max(200, searchData.length * 36)}>
                <BarChart data={searchData} layout="vertical" margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                  <XAxis type="number" tick={{ fontSize: 11, fontFamily: 'Prompt' }} />
                  <YAxis dataKey="name" type="category" width={120} tick={{ fontSize: 11, fontFamily: 'Prompt' }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="count" name="จำนวน" fill="#ec4899" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : <p className="analytics-empty">ยังไม่มีข้อมูล</p>}
          </ChartCard>

          {/* Personal Color Demand */}
          <ChartCard title="Personal Color ยอดนิยม" icon={<Palette size={16} />}>
            {seasonData.length > 0 ? (
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie
                    data={seasonData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={90}
                    paddingAngle={3}
                    dataKey="value"
                    nameKey="name"
                  >
                    {seasonData.map((entry) => (
                      <Cell key={entry.name} fill={SEASON_COLORS[entry.season] || '#8b5cf6'} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                  <Legend
                    verticalAlign="bottom"
                    formatter={(value) => <span style={{ fontSize: '0.8125rem', fontFamily: 'Prompt', color: '#374151' }}>{value}</span>}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : <p className="analytics-empty">ยังไม่มีข้อมูล</p>}
          </ChartCard>

          {/* Filter Usage */}
          <ChartCard title="การใช้ตัวกรอง" icon={<SlidersHorizontal size={16} />}>
            {filterUsage.length > 0 ? (
              <ResponsiveContainer width="100%" height={Math.max(200, Math.min(filterUsage.length, 10) * 36)}>
                <BarChart
                  data={filterUsage.slice(0, 10).map(f => ({
                    name: `${(f.filter_type || '').replace(/^"|"$/g, '')}: ${(f.filter_value || '').replace(/^"|"$/g, '')}`,
                    count: f.count,
                  }))}
                  layout="vertical"
                  margin={{ top: 5, right: 20, left: 10, bottom: 5 }}
                >
                  <XAxis type="number" tick={{ fontSize: 11, fontFamily: 'Prompt' }} />
                  <YAxis dataKey="name" type="category" width={150} tick={{ fontSize: 11, fontFamily: 'Prompt' }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="count" name="จำนวน" fill="#d946ef" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : <p className="analytics-empty">ยังไม่มีข้อมูล</p>}
          </ChartCard>

          {/* Makeup Presets */}
          <ChartCard title="Preset แต่งหน้ายอดนิยม" icon={<Sparkles size={16} />} full>
            {presetData.length > 0 ? (
              <ResponsiveContainer width="100%" height={Math.max(180, presetData.length * 36)}>
                <BarChart data={presetData} layout="vertical" margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                  <XAxis type="number" tick={{ fontSize: 11, fontFamily: 'Prompt' }} />
                  <YAxis dataKey="name" type="category" width={140} tick={{ fontSize: 11, fontFamily: 'Prompt' }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="count" name="จำนวน" fill="#a78bfa" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : <p className="analytics-empty">ยังไม่มีข้อมูล</p>}
          </ChartCard>

        </div>
      </div>
    </div>
  )
}

function StatCard({ label, value, icon, variant }) {
  return (
    <div className="analytics-stat">
      <div className={`analytics-stat__blob analytics-stat__blob--${variant}`} />
      <div className="analytics-stat__body">
        <div>
          <p className="analytics-stat__label">{label}</p>
          <p className="analytics-stat__value">{value}</p>
        </div>
        <div className={`analytics-stat__icon analytics-stat__icon--${variant}`}>
          {icon}
        </div>
      </div>
    </div>
  )
}

function ChartCard({ title, icon, children, full }) {
  return (
    <div className={`analytics-chart-card ${full ? 'analytics-chart-card--full' : ''}`}>
      <div className="analytics-chart-card__heading">
        <span className="analytics-chart-card__icon">{icon}</span>
        <h2 className="analytics-chart-card__title">{title}</h2>
      </div>
      {children}
    </div>
  )
}

function FunnelStep({ label, count, max, variant }) {
  const pct = max > 0 ? Math.max((count / max) * 100, 8) : 8
  return (
    <div className="analytics-funnel__step">
      <span className="analytics-funnel__label">{label}</span>
      <div className="analytics-funnel__bar-wrapper">
        <div
          className={`analytics-funnel__bar analytics-funnel__bar--${variant}`}
          style={{ width: `${pct}%` }}
        >
          <span className="analytics-funnel__bar-text">{count.toLocaleString()}</span>
        </div>
      </div>
    </div>
  )
}
