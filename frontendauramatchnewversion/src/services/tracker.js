/**
 * User Behavior Tracker
 * เก็บข้อมูลพฤติกรรมผู้ใช้ส่งไป backend
 */
import api from '../api/axios'

// สร้าง session ID ถ้ายังไม่มี
function getSessionId() {
  let sid = sessionStorage.getItem('aura_session_id')
  if (!sid) {
    sid = 'sess_' + Date.now() + '_' + Math.random().toString(36).slice(2, 8)
    sessionStorage.setItem('aura_session_id', sid)
  }
  return sid
}

// Queue สำหรับ batch send
let eventQueue = []
let flushTimer = null

function queueEvent(event) {
  eventQueue.push({ ...event, session_id: getSessionId() })

  // Flush ทุก 3 วินาที หรือเมื่อมี 10 events
  if (eventQueue.length >= 10) {
    flushEvents()
  } else if (!flushTimer) {
    flushTimer = setTimeout(flushEvents, 3000)
  }
}

async function flushEvents() {
  if (flushTimer) {
    clearTimeout(flushTimer)
    flushTimer = null
  }
  if (eventQueue.length === 0) return

  const events = [...eventQueue]
  eventQueue = []

  try {
    await api.post('/behavior/track-batch', events)
  } catch {
    // silent fail — ไม่ให้ tracking error กระทบ UX
  }
}

// Flush เมื่อปิดหน้า
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', flushEvents)
}

// ═══════════════════════════════════════
// Public Tracking Functions
// ═══════════════════════════════════════

/** ดูสินค้า */
export function trackProductView(product) {
  queueEvent({
    event_type: 'product_view',
    page: 'products',
    event_data: {
      product_id: product.product_id,
      product_name: product.name,
      brand: product.brand_name,
      category: product.category_name,
      price: product.price,
      personal_color: product.personal_color,
    },
  })
}

/** ค้นหาสินค้า */
export function trackSearch(query) {
  if (!query || query.length < 2) return
  queueEvent({
    event_type: 'search',
    page: 'products',
    event_data: { query },
  })
}

/** ใช้ตัวกรอง */
export function trackFilter(filterType, filterValue) {
  queueEvent({
    event_type: 'filter',
    page: 'products',
    event_data: { filter_type: filterType, filter_value: String(filterValue) },
  })
}

/** กดลิงก์ซื้อ */
export function trackClick(product, platform, url) {
  queueEvent({
    event_type: 'click',
    page: 'products',
    event_data: {
      product_id: product.product_id,
      product_name: product.name,
      platform,
      url,
    },
  })
}

/** ดูสินค้าคล้ายกัน */
export function trackSimilarView(product) {
  queueEvent({
    event_type: 'similar_view',
    page: 'products',
    event_data: {
      product_id: product.product_id,
      product_name: product.name,
    },
  })
}

/** เลือกสีแต่งหน้า */
export function trackMakeupSelect(part, color) {
  queueEvent({
    event_type: 'makeup_select',
    page: 'editor',
    event_data: { part, color },
  })
}

/** ใช้ preset แต่งหน้า */
export function trackPresetApply(presetName) {
  queueEvent({
    event_type: 'preset_apply',
    page: 'editor',
    event_data: { preset_name: presetName },
  })
}

/** วิเคราะห์ใบหน้า */
export function trackAnalysis(result) {
  queueEvent({
    event_type: 'face_analysis',
    page: 'analyze',
    event_data: {
      face_shape: result.face_shape,
      skin_tone: result.skin_tone,
      personal_color: result.personal_color,
    },
  })
}

/** ดาวน์โหลดรูปแต่ง */
export function trackDownload() {
  queueEvent({
    event_type: 'photo_download',
    page: 'editor',
    event_data: {},
  })
}
