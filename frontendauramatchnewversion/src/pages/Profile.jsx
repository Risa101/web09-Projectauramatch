import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import api from '../api/axios'
import { User, Mail, Calendar, Save, Loader2, History, Pen, X, Sparkles } from 'lucide-react'
import './Profile.css'

const FACE_SHAPE_TH = { oval: 'รูปไข่', round: 'กลม', square: 'เหลี่ยม', heart: 'หัวใจ', oblong: 'ยาว', diamond: 'เพชร', triangle: 'สามเหลี่ยม' }
const SKIN_TONE_TH = { fair: 'ขาวมาก', light: 'ขาว', medium: 'กลาง', tan: 'แทน', dark: 'คล้ำ', deep: 'เข้ม' }

const SEASON_BAR_CLASS = {
  spring: 'analysis-card__bar--spring',
  summer: 'analysis-card__bar--summer',
  autumn: 'analysis-card__bar--autumn',
  winter: 'analysis-card__bar--winter',
}

const SEASON_BADGE_CLASS = {
  spring: 'analysis-card__season-badge--spring',
  summer: 'analysis-card__season-badge--summer',
  autumn: 'analysis-card__season-badge--autumn',
  winter: 'analysis-card__season-badge--winter',
}

export default function Profile() {
  const { user } = useAuth()
  const [profile, setProfile] = useState(null)
  const [analyses, setAnalyses] = useState([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    display_name: '',
    bio: '',
    gender: '',
    nationality: '',
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [profileRes, analysesRes] = await Promise.all([
        api.get('/profile/'),
        api.get('/profile/analyses'),
      ])
      setProfile(profileRes.data)
      setAnalyses(analysesRes.data)
      if (profileRes.data.profile) {
        const p = profileRes.data.profile
        setForm({
          first_name: p.first_name || '',
          last_name: p.last_name || '',
          display_name: p.display_name || '',
          bio: p.bio || '',
          gender: p.gender || '',
          nationality: p.nationality || '',
        })
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      const params = new URLSearchParams()
      Object.entries(form).forEach(([k, v]) => {
        if (v) params.append(k, v)
      })
      await api.put(`/profile/?${params.toString()}`)
      alert('บันทึกโปรไฟล์สำเร็จ')
      setEditing(false)
    } catch {
      alert('เกิดข้อผิดพลาด')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="profile-loading">
        <div className="profile-loading__inner">
          <div className="profile-loading__orb-wrapper">
            <div className="profile-loading__orb" />
            <Loader2 size={28} className="profile-loading__spinner" />
          </div>
          <p className="profile-loading__text">
            กำลังโหลดโปรไฟล์...
          </p>
        </div>
      </div>
    )
  }

  const initial = profile?.username?.charAt(0)?.toUpperCase() || '?'

  return (
    <div className="profile-page">
      {/* Hero Header */}
      <div className="profile-hero">
        <div className="profile-hero__gradient" />
        <div className="profile-hero__decorations">
          <div className="profile-hero__blob--top" />
          <div className="profile-hero__blob--bottom" />
        </div>
        <div className="profile-hero__content">
          <h1 className="profile-hero__title">My Profile</h1>
          <p className="profile-hero__subtitle">
            จัดการข้อมูลส่วนตัวและดูประวัติการวิเคราะห์
          </p>
        </div>
      </div>

      <div className="profile-main">
        {/* Profile Card */}
        <div className="profile-card">
          <div className="profile-card__layout">
            {/* Avatar */}
            <div className="profile-avatar">
              <div className="profile-avatar__circle">
                <span className="profile-avatar__initial">{initial}</span>
              </div>
              <div className="profile-avatar__status" />
            </div>

            {/* Info */}
            <div className="profile-info">
              <h2 className="profile-info__name">{profile?.username}</h2>
              <div className="profile-info__meta">
                <div className="profile-info__meta-item">
                  <Mail size={14} className="profile-info__meta-icon" />
                  <span>{profile?.email}</span>
                </div>
                <span className="profile-info__meta-divider">|</span>
                <div className="profile-info__meta-item">
                  <Calendar size={14} className="profile-info__meta-icon" />
                  <span>สมัครเมื่อ {profile?.created_at?.split(' ')[0]}</span>
                </div>
              </div>
              <div className="profile-info__role-wrapper">
                <span
                  className={`profile-role-badge ${
                    profile?.role === 'admin'
                      ? 'profile-role-badge--admin'
                      : 'profile-role-badge--user'
                  }`}
                >
                  {profile?.role}
                </span>
              </div>
            </div>

            {/* Edit toggle button */}
            {!editing && (
              <button onClick={() => setEditing(true)} className="profile-edit-btn">
                <Pen size={14} />
                แก้ไขโปรไฟล์
              </button>
            )}
          </div>
        </div>

        {/* Edit Form Card */}
        {editing && (
          <div className="profile-card profile-form-card">
            <div className="profile-form__header">
              <div className="profile-form__header-left">
                <div className="profile-form__icon-box">
                  <Pen size={14} className="profile-form__icon-box-icon" />
                </div>
                <h2 className="profile-form__title">แก้ไขข้อมูล</h2>
              </div>
              <button onClick={() => setEditing(false)} className="profile-form__close-btn">
                <X size={18} />
              </button>
            </div>

            <div className="profile-form__grid">
              <InputField label="ชื่อ" value={form.first_name} onChange={v => setForm({ ...form, first_name: v })} />
              <InputField label="นามสกุล" value={form.last_name} onChange={v => setForm({ ...form, last_name: v })} />
              <InputField label="ชื่อที่แสดง" value={form.display_name} onChange={v => setForm({ ...form, display_name: v })} />
              <InputField label="สัญชาติ" value={form.nationality} onChange={v => setForm({ ...form, nationality: v })} />
              <div>
                <label className="profile-field__label">เพศ</label>
                <select
                  value={form.gender}
                  onChange={e => setForm({ ...form, gender: e.target.value })}
                  className="profile-field__select"
                >
                  <option value="">-- เลือก --</option>
                  <option value="female">หญิง</option>
                  <option value="male">ชาย</option>
                  <option value="non_binary">Non-binary</option>
                  <option value="prefer_not_to_say">ไม่ระบุ</option>
                </select>
              </div>
              <div className="profile-form__col-span-2">
                <label className="profile-field__label">เกี่ยวกับตัวคุณ</label>
                <textarea
                  value={form.bio}
                  onChange={e => setForm({ ...form, bio: e.target.value })}
                  rows={3}
                  placeholder="เล่าเรื่องราวของคุณให้เราฟังหน่อย..."
                  className="profile-field__textarea"
                />
              </div>
            </div>

            <div className="profile-form__actions">
              <button onClick={handleSave} disabled={saving} className="profile-save-btn">
                {saving ? <Loader2 size={16} className="profile-save-btn__spinner" /> : <Save size={16} />}
                บันทึก
              </button>
              <button onClick={() => setEditing(false)} className="profile-cancel-btn">
                ยกเลิก
              </button>
            </div>
          </div>
        )}

        {/* Analysis History Section */}
        <div className="profile-history">
          <div className="profile-history__header">
            <div className="profile-history__icon-box">
              <Sparkles size={18} className="profile-history__icon-box-icon" />
            </div>
            <div>
              <h2 className="profile-history__title">ประวัติการวิเคราะห์</h2>
              <p className="profile-history__count">
                {analyses.length > 0
                  ? `ทั้งหมด ${analyses.length} รายการ`
                  : 'ยังไม่มีข้อมูล'}
              </p>
            </div>
          </div>

          {analyses.length === 0 ? (
            <div className="profile-history__empty">
              <div className="profile-history__empty-icon">
                <History size={28} className="profile-history__empty-icon-svg" />
              </div>
              <p className="profile-history__empty-text">ยังไม่มีประวัติการวิเคราะห์</p>
              <p className="profile-history__empty-subtext">เริ่มวิเคราะห์สีประจำตัวของคุณได้เลย</p>
            </div>
          ) : (
            <div className="profile-history__grid">
              {analyses.map((a) => (
                <div key={a.analysis_id} className="analysis-card">
                  {/* Color bar top */}
                  <div className={`analysis-card__bar ${SEASON_BAR_CLASS[a.personal_color] || 'analysis-card__bar--default'}`} />

                  <div className="analysis-card__body">
                    <div className="analysis-card__header">
                      <span className="analysis-card__date">
                        {a.created_at?.split(' ')[0]}
                      </span>
                      <span className={`analysis-card__season-badge ${SEASON_BADGE_CLASS[a.personal_color] || 'analysis-card__season-badge--default'}`}>
                        {a.personal_color}
                      </span>
                    </div>

                    <div className="analysis-card__rows">
                      <AnalysisRow label="โครงหน้า" value={FACE_SHAPE_TH[a.face_shape] || a.face_shape} />
                      <AnalysisRow label="สีผิว" value={SKIN_TONE_TH[a.skin_tone] || a.skin_tone} />
                      <AnalysisRow label="Undertone" value={a.skin_undertone} />
                    </div>

                    {/* Confidence Bar */}
                    {a.confidence_score != null && (
                      <div className="analysis-card__confidence">
                        <div className="analysis-card__confidence-header">
                          <span className="analysis-card__confidence-label">ความมั่นใจ</span>
                          <span className="analysis-card__confidence-value">
                            {Math.round(a.confidence_score * 100)}%
                          </span>
                        </div>
                        <div className="analysis-card__confidence-track">
                          <div
                            className="analysis-card__confidence-fill"
                            style={{ width: `${Math.round(a.confidence_score * 100)}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function AnalysisRow({ label, value }) {
  return (
    <div className="analysis-row">
      <span className="analysis-row__label">{label}</span>
      <span className="analysis-row__value">{value}</span>
    </div>
  )
}

function InputField({ label, value, onChange }) {
  return (
    <div>
      <label className="profile-field__label">{label}</label>
      <input
        type="text"
        value={value}
        onChange={e => onChange(e.target.value)}
        className="profile-field__input"
      />
    </div>
  )
}
