import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { bannerApi } from '../../api/axios'
import {
  ArrowLeft, Image, Plus, Pencil, Trash2, ToggleLeft, ToggleRight,
} from 'lucide-react'
import './BannerManager.css'

const POSITIONS = [
  { value: 'home_top', label: 'Home (บน)' },
  { value: 'home_middle', label: 'Home (กลาง)' },
  { value: 'sidebar', label: 'Sidebar' },
]

const EMPTY_FORM = { title: '', link_url: '', position: 'home_top', starts_at: '', ends_at: '', is_active: 1 }

function formatDate(iso) {
  if (!iso) return '-'
  return new Date(iso).toLocaleDateString('th-TH', { day: 'numeric', month: 'short', year: 'numeric' })
}

function toLocalInput(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const offset = d.getTimezoneOffset()
  const local = new Date(d.getTime() - offset * 60000)
  return local.toISOString().slice(0, 16)
}

export default function BannerManager() {
  const [banners, setBanners] = useState([])
  const [loading, setLoading] = useState(false)
  const [editingBanner, setEditingBanner] = useState(null) // null=list, {}=create, {banner_id}=edit
  const [bannerForm, setBannerForm] = useState(EMPTY_FORM)
  const [imageFile, setImageFile] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)

  const loadBanners = useCallback(() => {
    setLoading(true)
    bannerApi.adminGetList({ page: 1, limit: 100 })
      .then(res => setBanners(res.data.banners || []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => { loadBanners() }, [loadBanners])

  // ── Handlers ──

  const openCreate = () => {
    setEditingBanner({})
    setBannerForm(EMPTY_FORM)
    setImageFile(null)
    setImagePreview(null)
  }

  const openEdit = (b) => {
    setEditingBanner(b)
    setBannerForm({
      title: b.title || '',
      link_url: b.link_url || '',
      position: b.position || 'home_top',
      starts_at: toLocalInput(b.starts_at),
      ends_at: toLocalInput(b.ends_at),
      is_active: b.is_active,
    })
    setImageFile(null)
    setImagePreview(b.image_url || null)
  }

  const handleFileChange = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setImageFile(file)
    setImagePreview(URL.createObjectURL(file))
  }

  const saveBanner = async () => {
    if (!editingBanner.banner_id && !imageFile) {
      alert('กรุณาเลือกรูปภาพ')
      return
    }
    const fd = new FormData()
    if (imageFile) fd.append('file', imageFile)
    fd.append('title', bannerForm.title)
    fd.append('link_url', bannerForm.link_url)
    fd.append('position', bannerForm.position)
    fd.append('is_active', bannerForm.is_active)
    if (bannerForm.starts_at) fd.append('starts_at', new Date(bannerForm.starts_at).toISOString())
    if (bannerForm.ends_at) fd.append('ends_at', new Date(bannerForm.ends_at).toISOString())

    try {
      if (editingBanner.banner_id) {
        await bannerApi.adminUpdate(editingBanner.banner_id, fd)
      } else {
        await bannerApi.adminCreate(fd)
      }
      setEditingBanner(null)
      loadBanners()
    } catch {
      alert('เกิดข้อผิดพลาด กรุณาลองใหม่')
    }
  }

  const deleteBanner = async (id) => {
    if (!confirm('ต้องการลบแบนเนอร์นี้?')) return
    try {
      await bannerApi.adminDelete(id)
      loadBanners()
    } catch {
      alert('ลบไม่สำเร็จ')
    }
  }

  const toggleBanner = async (id) => {
    try {
      await bannerApi.adminToggle(id)
      loadBanners()
    } catch {
      alert('เปลี่ยนสถานะไม่สำเร็จ')
    }
  }

  // ── Render ──

  return (
    <div className="bnrmgr-page">
      <div className="bnrmgr-container">

        {/* Header */}
        <div className="bnrmgr-header">
          <Link to="/admin" className="bnrmgr-back">
            <ArrowLeft size={14} />
            กลับ Dashboard
          </Link>
          <div className="bnrmgr-header__row">
            <div className="bnrmgr-header__accent" />
            <h1 className="bnrmgr-header__title">จัดการแบนเนอร์</h1>
          </div>
        </div>

        {editingBanner !== null ? (
          /* ── Form View ── */
          <div className="bnrmgr-form-card">
            <h2 className="bnrmgr-form-card__title">
              {editingBanner.banner_id ? 'แก้ไขแบนเนอร์' : 'เพิ่มแบนเนอร์ใหม่'}
            </h2>

            <label className="bnrmgr-label">
              รูปภาพแบนเนอร์ {!editingBanner.banner_id && <span className="bnrmgr-required">*</span>}
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp,image/gif"
                className="bnrmgr-file-input"
                onChange={handleFileChange}
              />
            </label>
            {imagePreview && (
              <img src={imagePreview} alt="Preview" className="bnrmgr-preview" />
            )}

            <label className="bnrmgr-label">
              ชื่อแบนเนอร์
              <input
                className="bnrmgr-input"
                value={bannerForm.title}
                onChange={e => setBannerForm(f => ({ ...f, title: e.target.value }))}
                placeholder="ชื่อแบนเนอร์ (ไม่บังคับ)"
              />
            </label>

            <label className="bnrmgr-label">
              ลิงก์ URL
              <input
                className="bnrmgr-input"
                value={bannerForm.link_url}
                onChange={e => setBannerForm(f => ({ ...f, link_url: e.target.value }))}
                placeholder="https://..."
              />
            </label>

            <label className="bnrmgr-label">
              ตำแหน่ง
              <select
                className="bnrmgr-input bnrmgr-select"
                value={bannerForm.position}
                onChange={e => setBannerForm(f => ({ ...f, position: e.target.value }))}
              >
                {POSITIONS.map(p => (
                  <option key={p.value} value={p.value}>{p.label}</option>
                ))}
              </select>
            </label>

            <div className="bnrmgr-row">
              <label className="bnrmgr-label">
                เริ่มแสดง
                <input
                  type="datetime-local"
                  className="bnrmgr-input"
                  value={bannerForm.starts_at}
                  onChange={e => setBannerForm(f => ({ ...f, starts_at: e.target.value }))}
                />
              </label>
              <label className="bnrmgr-label">
                สิ้นสุดแสดง
                <input
                  type="datetime-local"
                  className="bnrmgr-input"
                  value={bannerForm.ends_at}
                  onChange={e => setBannerForm(f => ({ ...f, ends_at: e.target.value }))}
                />
              </label>
            </div>

            <label className="bnrmgr-checkbox-label">
              <input
                type="checkbox"
                checked={bannerForm.is_active === 1}
                onChange={e => setBannerForm(f => ({ ...f, is_active: e.target.checked ? 1 : 0 }))}
              />
              เปิดใช้งาน
            </label>

            <div className="bnrmgr-form-actions">
              <button className="bnrmgr-btn bnrmgr-btn--primary" onClick={saveBanner}>
                บันทึก
              </button>
              <button className="bnrmgr-btn bnrmgr-btn--ghost" onClick={() => setEditingBanner(null)}>
                ยกเลิก
              </button>
            </div>
          </div>
        ) : (
          /* ── List View ── */
          <>
            <button className="bnrmgr-btn bnrmgr-btn--primary bnrmgr-btn--create" onClick={openCreate}>
              <Plus size={15} /> เพิ่มแบนเนอร์
            </button>

            {loading ? (
              <p className="bnrmgr-loading">กำลังโหลด...</p>
            ) : banners.length === 0 ? (
              <p className="bnrmgr-empty">ยังไม่มีแบนเนอร์</p>
            ) : (
              <div className="bnrmgr-table-wrapper">
                <table className="bnrmgr-table">
                  <thead>
                    <tr>
                      <th>รูปภาพ</th>
                      <th>ชื่อ</th>
                      <th>ตำแหน่ง</th>
                      <th>สถานะ</th>
                      <th>ช่วงเวลา</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {banners.map(b => (
                      <tr key={b.banner_id}>
                        <td>
                          <img src={b.image_url} alt="" className="bnrmgr-thumb" />
                        </td>
                        <td className="bnrmgr-table__title-cell">
                          {b.title || <span style={{ color: '#9ca3af' }}>-</span>}
                        </td>
                        <td>
                          <span className="bnrmgr-position">
                            {POSITIONS.find(p => p.value === b.position)?.label || b.position}
                          </span>
                        </td>
                        <td>
                          <span className={`bnrmgr-status ${b.is_active ? 'bnrmgr-status--active' : 'bnrmgr-status--inactive'}`}>
                            {b.is_active ? 'เปิด' : 'ปิด'}
                          </span>
                        </td>
                        <td className="bnrmgr-date-cell">
                          {formatDate(b.starts_at)} ~ {formatDate(b.ends_at)}
                        </td>
                        <td>
                          <div className="bnrmgr-actions">
                            <button className="bnrmgr-icon-btn" title="แก้ไข" onClick={() => openEdit(b)}>
                              <Pencil size={14} />
                            </button>
                            <button
                              className="bnrmgr-icon-btn bnrmgr-icon-btn--toggle"
                              title={b.is_active ? 'ปิดใช้งาน' : 'เปิดใช้งาน'}
                              onClick={() => toggleBanner(b.banner_id)}
                            >
                              {b.is_active ? <ToggleRight size={16} /> : <ToggleLeft size={16} />}
                            </button>
                            <button className="bnrmgr-icon-btn bnrmgr-icon-btn--danger" title="ลบ" onClick={() => deleteBanner(b.banner_id)}>
                              <Trash2 size={14} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
