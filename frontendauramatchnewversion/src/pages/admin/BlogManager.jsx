import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { blogApi } from '../../api/axios'
import {
  ArrowLeft, Plus, Pencil, Trash2, Eye, FileText, FolderOpen,
} from 'lucide-react'
import './BlogManager.css'

export default function BlogManager() {
  const [tab, setTab] = useState('posts')

  // Posts state
  const [posts, setPosts] = useState([])
  const [editingPost, setEditingPost] = useState(null) // null = list view, {} = create, {post_id} = edit
  const [postForm, setPostForm] = useState({ title: '', category_id: '', content: '', thumbnail_url: '', is_published: 0 })

  // Categories state
  const [categories, setCategories] = useState([])
  const [editingCategory, setEditingCategory] = useState(null)
  const [catForm, setCatForm] = useState({ name: '', description: '' })

  const [loading, setLoading] = useState(false)

  const loadPosts = useCallback(() => {
    setLoading(true)
    blogApi.adminGetPosts({ limit: 50 })
      .then(res => setPosts(res.data.posts))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const loadCategories = useCallback(() => {
    blogApi.getCategories()
      .then(res => setCategories(res.data))
      .catch(() => {})
  }, [])

  useEffect(() => {
    loadPosts()
    loadCategories()
  }, [loadPosts, loadCategories])

  // ── Post handlers ──

  const openCreatePost = () => {
    setPostForm({ title: '', category_id: '', content: '', thumbnail_url: '', is_published: 0 })
    setEditingPost({})
  }

  const openEditPost = (post) => {
    setPostForm({
      title: post.title,
      category_id: post.category?.category_id || '',
      content: post.content || '',
      thumbnail_url: post.thumbnail_url || '',
      is_published: post.is_published,
    })
    setEditingPost(post)
  }

  const savePost = async () => {
    const data = {
      ...postForm,
      category_id: postForm.category_id || null,
      is_published: postForm.is_published ? 1 : 0,
    }
    try {
      if (editingPost.post_id) {
        await blogApi.adminUpdatePost(editingPost.post_id, data)
      } else {
        await blogApi.adminCreatePost(data)
      }
      setEditingPost(null)
      loadPosts()
    } catch {
      alert('เกิดข้อผิดพลาด')
    }
  }

  const deletePost = async (postId) => {
    if (!confirm('ต้องการลบบทความนี้?')) return
    try {
      await blogApi.adminDeletePost(postId)
      loadPosts()
    } catch {
      alert('เกิดข้อผิดพลาด')
    }
  }

  // ── Category handlers ──

  const openCreateCategory = () => {
    setCatForm({ name: '', description: '' })
    setEditingCategory({})
  }

  const openEditCategory = (cat) => {
    setCatForm({ name: cat.name, description: cat.description || '' })
    setEditingCategory(cat)
  }

  const saveCategory = async () => {
    try {
      if (editingCategory.category_id) {
        await blogApi.adminUpdateCategory(editingCategory.category_id, catForm)
      } else {
        await blogApi.adminCreateCategory(catForm)
      }
      setEditingCategory(null)
      loadCategories()
    } catch {
      alert('เกิดข้อผิดพลาด')
    }
  }

  const deleteCategory = async (catId) => {
    if (!confirm('ต้องการลบหมวดหมู่นี้? บทความในหมวดหมู่นี้จะไม่ถูกลบ')) return
    try {
      await blogApi.adminDeleteCategory(catId)
      loadCategories()
    } catch {
      alert('เกิดข้อผิดพลาด')
    }
  }

  return (
    <div className="blogmgr-page">
      <div className="blogmgr-container">

        {/* Header */}
        <div className="blogmgr-header">
          <Link to="/admin" className="blogmgr-back">
            <ArrowLeft size={16} />
            กลับ Dashboard
          </Link>
          <div className="blogmgr-header__row">
            <div className="blogmgr-header__accent" />
            <h1 className="blogmgr-header__title">จัดการบทความ</h1>
          </div>
        </div>

        {/* Tabs */}
        <div className="blogmgr-tabs">
          <button
            className={`blogmgr-tab ${tab === 'posts' ? 'blogmgr-tab--active' : ''}`}
            onClick={() => { setTab('posts'); setEditingPost(null) }}
          >
            <FileText size={16} />
            บทความ
          </button>
          <button
            className={`blogmgr-tab ${tab === 'categories' ? 'blogmgr-tab--active' : ''}`}
            onClick={() => { setTab('categories'); setEditingCategory(null) }}
          >
            <FolderOpen size={16} />
            หมวดหมู่
          </button>
        </div>

        {/* Posts Tab */}
        {tab === 'posts' && (
          editingPost !== null ? (
            <div className="blogmgr-form-card">
              <h2 className="blogmgr-form-card__title">
                {editingPost.post_id ? 'แก้ไขบทความ' : 'สร้างบทความใหม่'}
              </h2>

              <label className="blogmgr-label">
                หัวข้อ
                <input
                  className="blogmgr-input"
                  value={postForm.title}
                  onChange={e => setPostForm(f => ({ ...f, title: e.target.value }))}
                  placeholder="หัวข้อบทความ"
                />
              </label>

              <label className="blogmgr-label">
                หมวดหมู่
                <select
                  className="blogmgr-input"
                  value={postForm.category_id}
                  onChange={e => setPostForm(f => ({ ...f, category_id: e.target.value ? Number(e.target.value) : '' }))}
                >
                  <option value="">-- ไม่ระบุ --</option>
                  {categories.map(c => (
                    <option key={c.category_id} value={c.category_id}>{c.name}</option>
                  ))}
                </select>
              </label>

              <label className="blogmgr-label">
                เนื้อหา
                <textarea
                  className="blogmgr-input blogmgr-textarea"
                  rows={12}
                  value={postForm.content}
                  onChange={e => setPostForm(f => ({ ...f, content: e.target.value }))}
                  placeholder="เขียนเนื้อหาบทความ..."
                />
              </label>

              <label className="blogmgr-label">
                URL รูปภาพปก
                <input
                  className="blogmgr-input"
                  value={postForm.thumbnail_url}
                  onChange={e => setPostForm(f => ({ ...f, thumbnail_url: e.target.value }))}
                  placeholder="https://..."
                />
              </label>

              <label className="blogmgr-checkbox-label">
                <input
                  type="checkbox"
                  checked={!!postForm.is_published}
                  onChange={e => setPostForm(f => ({ ...f, is_published: e.target.checked ? 1 : 0 }))}
                />
                เผยแพร่ทันที
              </label>

              <div className="blogmgr-form-actions">
                <button className="blogmgr-btn blogmgr-btn--primary" onClick={savePost}>
                  บันทึก
                </button>
                <button className="blogmgr-btn blogmgr-btn--ghost" onClick={() => setEditingPost(null)}>
                  ยกเลิก
                </button>
              </div>
            </div>
          ) : (
            <>
              <button className="blogmgr-btn blogmgr-btn--primary blogmgr-btn--create" onClick={openCreatePost}>
                <Plus size={16} />
                สร้างบทความใหม่
              </button>

              {loading ? (
                <p className="blogmgr-loading">กำลังโหลด...</p>
              ) : posts.length === 0 ? (
                <p className="blogmgr-empty">ยังไม่มีบทความ</p>
              ) : (
                <div className="blogmgr-table-wrapper">
                  <table className="blogmgr-table">
                    <thead>
                      <tr>
                        <th>หัวข้อ</th>
                        <th>หมวดหมู่</th>
                        <th>สถานะ</th>
                        <th>เข้าชม</th>
                        <th>วันที่</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>
                      {posts.map(post => (
                        <tr key={post.post_id}>
                          <td className="blogmgr-table__title-cell">{post.title}</td>
                          <td>{post.category?.name || '-'}</td>
                          <td>
                            <span className={`blogmgr-status ${post.is_published ? 'blogmgr-status--pub' : 'blogmgr-status--draft'}`}>
                              {post.is_published ? 'เผยแพร่' : 'ฉบับร่าง'}
                            </span>
                          </td>
                          <td>
                            <span className="blogmgr-views-cell"><Eye size={13} /> {post.views}</span>
                          </td>
                          <td className="blogmgr-date-cell">
                            {post.created_at ? new Date(post.created_at).toLocaleDateString('th-TH', { day: 'numeric', month: 'short' }) : ''}
                          </td>
                          <td>
                            <div className="blogmgr-actions">
                              <button className="blogmgr-icon-btn" title="แก้ไข" onClick={() => openEditPost(post)}>
                                <Pencil size={15} />
                              </button>
                              <button className="blogmgr-icon-btn blogmgr-icon-btn--danger" title="ลบ" onClick={() => deletePost(post.post_id)}>
                                <Trash2 size={15} />
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
          )
        )}

        {/* Categories Tab */}
        {tab === 'categories' && (
          <>
            {editingCategory !== null ? (
              <div className="blogmgr-form-card">
                <h2 className="blogmgr-form-card__title">
                  {editingCategory.category_id ? 'แก้ไขหมวดหมู่' : 'เพิ่มหมวดหมู่ใหม่'}
                </h2>
                <label className="blogmgr-label">
                  ชื่อ
                  <input
                    className="blogmgr-input"
                    value={catForm.name}
                    onChange={e => setCatForm(f => ({ ...f, name: e.target.value }))}
                    placeholder="ชื่อหมวดหมู่"
                  />
                </label>
                <label className="blogmgr-label">
                  คำอธิบาย
                  <input
                    className="blogmgr-input"
                    value={catForm.description}
                    onChange={e => setCatForm(f => ({ ...f, description: e.target.value }))}
                    placeholder="คำอธิบายสั้นๆ (ไม่จำเป็น)"
                  />
                </label>
                <div className="blogmgr-form-actions">
                  <button className="blogmgr-btn blogmgr-btn--primary" onClick={saveCategory}>บันทึก</button>
                  <button className="blogmgr-btn blogmgr-btn--ghost" onClick={() => setEditingCategory(null)}>ยกเลิก</button>
                </div>
              </div>
            ) : (
              <>
                <button className="blogmgr-btn blogmgr-btn--primary blogmgr-btn--create" onClick={openCreateCategory}>
                  <Plus size={16} />
                  เพิ่มหมวดหมู่
                </button>

                {categories.length === 0 ? (
                  <p className="blogmgr-empty">ยังไม่มีหมวดหมู่</p>
                ) : (
                  <div className="blogmgr-table-wrapper">
                    <table className="blogmgr-table">
                      <thead>
                        <tr>
                          <th>ชื่อ</th>
                          <th>คำอธิบาย</th>
                          <th></th>
                        </tr>
                      </thead>
                      <tbody>
                        {categories.map(cat => (
                          <tr key={cat.category_id}>
                            <td className="blogmgr-table__title-cell">{cat.name}</td>
                            <td>{cat.description || '-'}</td>
                            <td>
                              <div className="blogmgr-actions">
                                <button className="blogmgr-icon-btn" title="แก้ไข" onClick={() => openEditCategory(cat)}>
                                  <Pencil size={15} />
                                </button>
                                <button className="blogmgr-icon-btn blogmgr-icon-btn--danger" title="ลบ" onClick={() => deleteCategory(cat.category_id)}>
                                  <Trash2 size={15} />
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
          </>
        )}
      </div>
    </div>
  )
}
