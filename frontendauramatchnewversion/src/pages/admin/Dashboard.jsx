import { useState, useEffect } from 'react'
import api from '../../api/axios'
import {
  MousePointer,
  DollarSign,
  ShoppingBag,
  Tag,
  ArrowRight,
  BarChart3,
  TrendingUp,
  Sparkles,
  FileText,
  Activity,
  Image,
} from 'lucide-react'
import './Dashboard.css'

export default function AdminDashboard() {
  const [stats, setStats] = useState(null)

  useEffect(() => {
    api.get('/commission/stats').then(res => setStats(res.data))
  }, [])

  return (
    <div className="dashboard-page">
      <div className="dashboard-container">

        {/* Header */}
        <div className="dashboard-header">
          <div className="dashboard-header-row">
            <div className="dashboard-accent-bar" />
            <h1 className="dashboard-title">
              Admin Dashboard
            </h1>
          </div>
          <p className="dashboard-subtitle">
            Overview of your affiliate performance
          </p>
        </div>

        {/* Top Stat Cards */}
        <div className="stat-cards-grid">
          {/* Total Clicks */}
          <div className="stat-card">
            <div className="stat-card__blob stat-card__blob--purple" />
            <div className="stat-card__body">
              <div>
                <p className="stat-card__label">
                  Total Clicks
                </p>
                <p className="stat-card__value">
                  {stats?.total_clicks?.toLocaleString() ?? '0'}
                </p>
              </div>
              <div className="stat-card__icon stat-card__icon--purple">
                <MousePointer size={20} />
              </div>
            </div>
          </div>

          {/* Total Commission */}
          <div className="stat-card">
            <div className="stat-card__blob stat-card__blob--pink" />
            <div className="stat-card__body">
              <div>
                <p className="stat-card__label">
                  Total Commission
                </p>
                <p className="stat-card__value">
                  ฿{Number(stats?.total_commission || 0).toLocaleString()}
                </p>
              </div>
              <div className="stat-card__icon stat-card__icon--pink">
                <DollarSign size={20} />
              </div>
            </div>
          </div>
        </div>

        {/* Platform Breakdown */}
        <div className="platform-section">
          <div className="section-heading">
            <BarChart3 size={18} className="section-heading__icon" />
            <h2 className="section-heading__text">
              Platform Breakdown
            </h2>
          </div>

          {stats?.by_platform && Object.keys(stats.by_platform).length > 0 ? (
            <div className="platform-table-wrapper">
              <table className="platform-table">
                <thead>
                  <tr>
                    <th>
                      Platform
                    </th>
                    <th>
                      Clicks
                    </th>
                    <th>
                      Commission
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(stats.by_platform).map(([platform, data]) => (
                    <tr key={platform}>
                      <td>
                        <div className="platform-name-cell">
                          <span className="platform-icon-badge">
                            <Sparkles size={14} />
                          </span>
                          <span className="platform-name">
                            {platform}
                          </span>
                        </div>
                      </td>
                      <td className="platform-value">
                        {data.clicks?.toLocaleString() ?? 0}
                      </td>
                      <td className="platform-value">
                        ฿{Number(data.commission || 0).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="platform-empty">
              No platform data available yet.
            </p>
          )}
        </div>

        {/* Quick Actions */}
        <div>
          <div className="quick-actions-heading">
            <TrendingUp size={18} className="section-heading__icon" />
            <h2 className="section-heading__text">
              Quick Actions
            </h2>
          </div>

          <div className="quick-actions-grid">
            <QuickActionCard
              href="/admin/products"
              icon={<ShoppingBag size={20} />}
              title="จัดการสินค้า"
              desc="เพิ่ม แก้ไข ลบสินค้า"
              variant="purple"
            />
            <QuickActionCard
              href="/admin/brands"
              icon={<Tag size={20} />}
              title="จัดการแบรนด์"
              desc="เพิ่ม แก้ไข แบรนด์"
              variant="fuchsia"
            />
            <QuickActionCard
              href="/admin/commission"
              icon={<DollarSign size={20} />}
              title="ค่าคอมมิชชั่น"
              desc="ดูสถิติและยืนยันยอด"
              variant="pink"
            />
            <QuickActionCard
              href="/admin/blog"
              icon={<FileText size={20} />}
              title="จัดการบทความ"
              desc="เขียน แก้ไข เผยแพร่บทความ"
              variant="purple"
            />
            <QuickActionCard
              href="/admin/analytics"
              icon={<Activity size={20} />}
              title="วิเคราะห์พฤติกรรม"
              desc="ดูสถิติการใช้งานของผู้ใช้"
              variant="fuchsia"
            />
            <QuickActionCard
              href="/admin/banners"
              icon={<Image size={20} />}
              title="จัดการแบนเนอร์"
              desc="เพิ่ม แก้ไข แบนเนอร์หน้าแรก"
              variant="pink"
            />
          </div>
        </div>
      </div>
    </div>
  )
}

function QuickActionCard({ href, icon, title, desc, variant }) {
  return (
    <a href={href} className="action-card">
      <div className={`action-card__top-line action-card__top-line--${variant}`} />
      <div className="action-card__body">
        <div>
          <div className={`action-card__icon-box action-card__icon-box--${variant}`}>
            {icon}
          </div>
          <h3 className="action-card__title">
            {title}
          </h3>
          <p className="action-card__desc">
            {desc}
          </p>
        </div>
        <ArrowRight size={16} className="action-card__arrow" />
      </div>
    </a>
  )
}
