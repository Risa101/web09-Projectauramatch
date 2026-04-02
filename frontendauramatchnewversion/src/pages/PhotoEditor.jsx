import { useState, useRef, useEffect, useCallback } from 'react'
import { Upload, Download, Wand2, SlidersHorizontal, Sparkles, ImagePlus, RotateCcw, Loader2, ShoppingBag, ExternalLink, X, Heart, Trash2 } from 'lucide-react'
import api from '../api/axios'
import { trackMakeupSelect, trackPresetApply, trackDownload } from '../services/tracker'
import './PhotoEditor.css'

const FILTERS = [
  { name: 'ปกติ', values: { brightness: 100, contrast: 100, saturate: 100 }, style: '' },
  { name: 'สว่าง', values: { brightness: 130, contrast: 100, saturate: 100 }, style: 'brightness(1.3)' },
  { name: 'นุ่ม', values: { brightness: 110, contrast: 90, saturate: 90 }, style: 'brightness(1.1) contrast(0.9) saturate(0.9)' },
  { name: 'วินเทจ', values: { brightness: 90, contrast: 100, saturate: 100 }, style: 'sepia(0.4) brightness(0.9)' },
  { name: 'คมชัด', values: { brightness: 100, contrast: 130, saturate: 120 }, style: 'contrast(1.3) saturate(1.2)' },
  { name: 'ขาวดำ', values: { brightness: 100, contrast: 100, saturate: 0 }, style: 'grayscale(1)' },
  { name: 'สดใส', values: { brightness: 110, contrast: 100, saturate: 150 }, style: 'saturate(1.5) brightness(1.1)' },
  { name: 'โรสโทน', values: { brightness: 100, contrast: 100, saturate: 130 }, style: 'sepia(0.2) saturate(1.3) hue-rotate(330deg)' },
]

const FILTER_ICONS = ['☀️', '✨', '🌸', '📜', '🔍', '🖤', '🌈', '🌹']

// ── Makeup Config ──
const MAKEUP_PARTS = [
  { id: 'lips', label: 'ลิปสติก', icon: '💋' },
  { id: 'eyes', label: 'อายแชโดว์', icon: '👁' },
  { id: 'eyeliner', label: 'อายไลเนอร์', icon: '✏️' },
  { id: 'eyebrows', label: 'คิ้ว', icon: '🖌️' },
  { id: 'lashes', label: 'ขนตา', icon: '👀' },
  { id: 'nose', label: 'คอนทัวร์', icon: '👃' },
  { id: 'blush', label: 'บลัช', icon: '🌸' },
  { id: 'highlight', label: 'ไฮไลท์', icon: '✨' },
  { id: 'foundation', label: 'รองพื้น', icon: '🧴' },
]

const MAKEUP_COLORS = {
  lips: [
    { name: 'แดงสด', color: '#dc2626' },
    { name: 'แดงเข้ม', color: '#991b1b' },
    { name: 'ชมพูสด', color: '#ec4899' },
    { name: 'ชมพูอ่อน', color: '#f9a8d4' },
    { name: 'ส้ม', color: '#f97316' },
    { name: 'ส้มอิฐ', color: '#c2410c' },
    { name: 'Nude', color: '#d4a574' },
    { name: 'Nude ชมพู', color: '#e8a0b4' },
    { name: 'Berry', color: '#9333ea' },
    { name: 'Plum', color: '#7e22ce' },
    { name: 'Rose', color: '#e11d48' },
    { name: 'Mauve', color: '#a8516e' },
  ],
  eyes: [
    { name: 'น้ำตาลเข้ม', color: '#78350f' },
    { name: 'น้ำตาลอ่อน', color: '#92400e' },
    { name: 'ชมพู', color: '#f9a8d4' },
    { name: 'ม่วง', color: '#a78bfa' },
    { name: 'ม่วงเข้ม', color: '#6d28d9' },
    { name: 'ทอง', color: '#d4a017' },
    { name: 'ทองแชมเปญ', color: '#e8d5a3' },
    { name: 'เขียว', color: '#4ade80' },
    { name: 'เขียวมรกต', color: '#047857' },
    { name: 'น้ำเงิน', color: '#3b82f6' },
    { name: 'Navy', color: '#1e3a5f' },
    { name: 'เทาเงิน', color: '#9ca3af' },
  ],
  eyeliner: [
    { name: 'ดำ', color: '#0a0a0a' },
    { name: 'น้ำตาลเข้ม', color: '#3b1f0b' },
    { name: 'น้ำตาล', color: '#78350f' },
    { name: 'เทาเข้ม', color: '#374151' },
    { name: 'น้ำเงินกรม', color: '#1e3a5f' },
    { name: 'เขียวเข้ม', color: '#14532d' },
    { name: 'ม่วงเข้ม', color: '#4c1d95' },
    { name: 'บอร์โดซ์', color: '#7f1d1d' },
  ],
  eyebrows: [
    { name: 'ดำ', color: '#1a1a1a' },
    { name: 'ดำอ่อน', color: '#374151' },
    { name: 'น้ำตาลเข้ม', color: '#4a3728' },
    { name: 'น้ำตาล', color: '#78350f' },
    { name: 'น้ำตาลอ่อน', color: '#8b6f47' },
    { name: 'น้ำตาลแดง', color: '#6b3a2a' },
    { name: 'เทา', color: '#6b7280' },
    { name: 'เทาอ่อน', color: '#9ca3af' },
  ],
  lashes: [
    { name: 'ดำ', color: '#0a0a0a' },
    { name: 'ดำธรรมชาติ', color: '#1f2937' },
    { name: 'น้ำตาลเข้ม', color: '#3b1f0b' },
    { name: 'น้ำตาล', color: '#78350f' },
  ],
  nose: [
    { name: 'เฉดดิ้งอ่อน', color: '#a68b6b' },
    { name: 'เฉดดิ้งกลาง', color: '#8b6f47' },
    { name: 'เฉดดิ้งเข้ม', color: '#6b4f2f' },
    { name: 'เฉดดิ้งเทา', color: '#78716c' },
  ],
  blush: [
    { name: 'ชมพูอ่อน', color: '#fbb6ce' },
    { name: 'ชมพูสด', color: '#f9a8d4' },
    { name: 'ชมพูเข้ม', color: '#ec4899' },
    { name: 'พีช', color: '#fdba74' },
    { name: 'Coral', color: '#fb7185' },
    { name: 'Coral เข้ม', color: '#e11d48' },
    { name: 'ม่วงอ่อน', color: '#c4b5fd' },
    { name: 'แดงอิฐ', color: '#dc6b5a' },
    { name: 'ส้มอ่อน', color: '#fed7aa' },
    { name: 'Rose', color: '#e8a0b4' },
  ],
  highlight: [
    { name: 'ขาวมุก', color: '#ffffff' },
    { name: 'แชมเปญ', color: '#f5e6c8' },
    { name: 'ทองอ่อน', color: '#fde68a' },
    { name: 'ทองชมพู', color: '#fecdd3' },
    { name: 'ชมพูมุก', color: '#fce7f3' },
    { name: 'ม่วงมุก', color: '#e9d5ff' },
  ],
  foundation: [
    { name: 'Porcelain', color: '#fde8d0' },
    { name: 'Ivory', color: '#f5deb3' },
    { name: 'Sand', color: '#e8c99b' },
    { name: 'Beige', color: '#d4a574' },
    { name: 'Honey', color: '#c49a6c' },
    { name: 'Caramel', color: '#a0785a' },
    { name: 'Tan', color: '#8b6f47' },
    { name: 'Mocha', color: '#6b4f2f' },
  ],
}

// dlib 68 landmark index ranges
const LANDMARK_GROUPS = {
  lips: { outer: [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59], inner: [60, 61, 62, 63, 64, 65, 66, 67] },
  eyes: { left: [36, 37, 38, 39, 40, 41], right: [42, 43, 44, 45, 46, 47] },
  eyeliner: { left: [36, 37, 38, 39, 40, 41], right: [42, 43, 44, 45, 46, 47] },
  eyebrows: { left: [17, 18, 19, 20, 21], right: [22, 23, 24, 25, 26] },
  lashes: { left: [36, 37, 38, 39, 40, 41], right: [42, 43, 44, 45, 46, 47] },
  nose: { bridge: [27, 28, 29, 30], bottom: [31, 32, 33, 34, 35] },
  blush: { left: [1, 2, 3, 4], right: [12, 13, 14, 15] },
  highlight: { bridge: [27, 28, 29, 30], cheekLeft: [1, 2], cheekRight: [14, 15] },
  foundation: { jaw: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16] },
}

const DEFAULT_MAKEUP = {
  lips: { color: null, intensity: 50 },
  eyes: { color: null, intensity: 40 },
  eyeliner: { color: null, intensity: 50 },
  eyebrows: { color: null, intensity: 30 },
  lashes: { color: null, intensity: 40 },
  nose: { color: null, intensity: 25 },
  blush: { color: null, intensity: 35 },
  highlight: { color: null, intensity: 30 },
  foundation: { color: null, intensity: 20 },
}

// ── Makeup Presets (ลุคสำเร็จรูป) ──
const MAKEUP_PRESETS = [
  {
    name: 'Korean Natural', icon: '🇰🇷', desc: 'ลุคเกาหลีธรรมชาติ ผิวฉ่ำ ปากชมพูใส',
    makeup: {
      lips: { color: '#f9a8d4', intensity: 40 }, eyes: { color: '#e8d5a3', intensity: 30 },
      eyeliner: { color: '#3b1f0b', intensity: 30 }, eyebrows: { color: '#4a3728', intensity: 25 },
      lashes: { color: '#1f2937', intensity: 30 }, nose: { color: null, intensity: 25 },
      blush: { color: '#fbb6ce', intensity: 30 }, highlight: { color: '#fce7f3', intensity: 25 },
      foundation: { color: '#fde8d0', intensity: 12 },
    }
  },
  {
    name: 'Glam Night', icon: '🌙', desc: 'ลุคปาร์ตี้กลางคืน ตาสโมกกี้ ปากแดง',
    makeup: {
      lips: { color: '#dc2626', intensity: 60 }, eyes: { color: '#1e3a5f', intensity: 50 },
      eyeliner: { color: '#0a0a0a', intensity: 60 }, eyebrows: { color: '#1a1a1a', intensity: 35 },
      lashes: { color: '#0a0a0a', intensity: 50 }, nose: { color: '#8b6f47', intensity: 20 },
      blush: { color: '#fb7185', intensity: 30 }, highlight: { color: '#f5e6c8', intensity: 35 },
      foundation: { color: '#f5deb3', intensity: 15 },
    }
  },
  {
    name: 'Soft Girl', icon: '🧸', desc: 'ลุคหวานละมุน แก้มชมพู ตาวิ้ง',
    makeup: {
      lips: { color: '#ec4899', intensity: 40 }, eyes: { color: '#f9a8d4', intensity: 35 },
      eyeliner: { color: null, intensity: 50 }, eyebrows: { color: '#8b6f47', intensity: 20 },
      lashes: { color: '#3b1f0b', intensity: 30 }, nose: { color: null, intensity: 25 },
      blush: { color: '#ec4899', intensity: 40 }, highlight: { color: '#ffffff', intensity: 30 },
      foundation: { color: null, intensity: 20 },
    }
  },
  {
    name: 'Office Day', icon: '💼', desc: 'ลุคทำงานสุภาพ เรียบร้อย ดูโปร',
    makeup: {
      lips: { color: '#d4a574', intensity: 45 }, eyes: { color: '#92400e', intensity: 30 },
      eyeliner: { color: '#374151', intensity: 35 }, eyebrows: { color: '#4a3728', intensity: 28 },
      lashes: { color: '#1f2937', intensity: 25 }, nose: { color: '#a68b6b', intensity: 15 },
      blush: { color: '#fdba74', intensity: 25 }, highlight: { color: '#f5e6c8', intensity: 20 },
      foundation: { color: '#e8c99b', intensity: 12 },
    }
  },
  {
    name: 'Sunset Glow', icon: '🌅', desc: 'ลุคส้มทอง อบอุ่น เหมือนแสงอาทิตย์ยามเย็น',
    makeup: {
      lips: { color: '#f97316', intensity: 50 }, eyes: { color: '#d4a017', intensity: 40 },
      eyeliner: { color: '#78350f', intensity: 35 }, eyebrows: { color: '#6b3a2a', intensity: 25 },
      lashes: { color: '#3b1f0b', intensity: 30 }, nose: { color: null, intensity: 25 },
      blush: { color: '#fed7aa', intensity: 35 }, highlight: { color: '#fde68a', intensity: 30 },
      foundation: { color: null, intensity: 20 },
    }
  },
  {
    name: 'Berry Queen', icon: '🫐', desc: 'ลุคม่วงเบอร์รี่ เท่ลึกลับ มีเสน่ห์',
    makeup: {
      lips: { color: '#7e22ce', intensity: 55 }, eyes: { color: '#6d28d9', intensity: 45 },
      eyeliner: { color: '#4c1d95', intensity: 50 }, eyebrows: { color: '#374151', intensity: 30 },
      lashes: { color: '#0a0a0a', intensity: 40 }, nose: { color: '#78716c', intensity: 18 },
      blush: { color: '#c4b5fd', intensity: 30 }, highlight: { color: '#e9d5ff', intensity: 28 },
      foundation: { color: null, intensity: 20 },
    }
  },
  {
    name: 'Fresh No-Makeup', icon: '🌿', desc: 'ลุคหน้าสดไม่แต่ง แต่สวยกว่าเดิม',
    makeup: {
      lips: { color: '#e8a0b4', intensity: 30 }, eyes: { color: null, intensity: 40 },
      eyeliner: { color: null, intensity: 50 }, eyebrows: { color: '#8b6f47', intensity: 18 },
      lashes: { color: '#78350f', intensity: 20 }, nose: { color: null, intensity: 25 },
      blush: { color: '#fbb6ce', intensity: 20 }, highlight: { color: '#ffffff', intensity: 18 },
      foundation: { color: '#fde8d0', intensity: 10 },
    }
  },
  {
    name: 'Red Carpet', icon: '🌹', desc: 'ลุคพรมแดง หรูหรา ดูแพงทุกมุม',
    makeup: {
      lips: { color: '#991b1b', intensity: 65 }, eyes: { color: '#78350f', intensity: 40 },
      eyeliner: { color: '#0a0a0a', intensity: 55 }, eyebrows: { color: '#1a1a1a', intensity: 35 },
      lashes: { color: '#0a0a0a', intensity: 50 }, nose: { color: '#6b4f2f', intensity: 22 },
      blush: { color: '#e11d48', intensity: 25 }, highlight: { color: '#f5e6c8', intensity: 35 },
      foundation: { color: '#f5deb3', intensity: 15 },
    }
  },
]

// ── Makeup Tips ──
const MAKEUP_TIPS = {
  lips: [
    '💡 ทาลิปไลเนอร์ก่อนจะช่วยให้ลิปติดทนขึ้น',
    '💡 ใช้คอนซีลเลอร์ลบขอบปากก่อนทา จะได้ขอบคมชัด',
    '💡 ซับทิชชู่แล้วทาซ้ำอีกชั้น จะติดทนทั้งวัน',
    '💡 สีแดงเข้ม เหมาะกับลุคปาร์ตี้ สี Nude เหมาะกับทุกวัน',
  ],
  eyes: [
    '💡 ทาสีอ่อนทั้งเปลือกตา แล้วเน้นสีเข้มที่หัวตาและหางตา',
    '💡 ใช้ไพรเมอร์ตาก่อน จะช่วยให้สีชัดและติดทนขึ้น',
    '💡 เบลนด์ขอบให้กลมกลืน อย่าปล่อยให้เห็นเส้นแบ่งสี',
    '💡 สีทองและแชมเปญ เหมาะกับทุกสีผิว',
  ],
  eyeliner: [
    '💡 เริ่มลากเส้นจากกลางตาไปหางตา แล้วค่อยต่อจากหัวตา',
    '💡 ดึงหางตาขึ้นเล็กน้อยเวลาลาก จะได้เส้นตรง',
    '💡 อายไลเนอร์สีน้ำตาล ดูเป็นธรรมชาติกว่าสีดำ',
    '💡 ลองลากเส้นติดขนตา จะได้ตาโตขึ้นแบบธรรมชาติ',
  ],
  eyebrows: [
    '💡 แปรงขนคิ้วให้เป็นทรงก่อน แล้วค่อยเติมสี',
    '💡 ใช้สีอ่อนกว่าสีผมเล็กน้อย จะได้คิ้วดูธรรมชาติ',
    '💡 เน้นเติมที่ส่วนหาง อย่าเติมหนักที่หัวคิ้ว',
    '💡 ใช้ Spoolie แปรงคิ้วหลังเติม จะได้สีกลมกลืน',
  ],
  lashes: [
    '💡 ดัดขนตาก่อนปัดมาสคาร่า จะงอนสวยขึ้น',
    '💡 ปัดซิกแซ็กจากโคนถึงปลาย จะไม่เป็นก้อน',
    '💡 ขนตาล่าง ใช้แปรงเล็กปัดเบาๆ ตาจะดูโตขึ้น',
    '💡 เคลือบเบบี้พาวเดอร์ระหว่างชั้น จะหนาขึ้น',
  ],
  nose: [
    '💡 ลากเฉดดิ้ง 2 เส้นข้างจมูก แล้วเบลนด์ให้กลมกลืน',
    '💡 ใช้สีเข้มกว่าสีผิว 2 โทน จะดูเป็นธรรมชาติ',
    '💡 อย่าลากเส้นยาวเกินไป หยุดที่ปลายจมูก',
    '💡 เบลนด์ด้วยฟองน้ำชื้น จะได้เนียนที่สุด',
  ],
  blush: [
    '💡 ยิ้มแล้วปัดบลัชตรงแก้มที่นูนขึ้นมา',
    '💡 ปัดบลัชขึ้นเฉียงไปทางขมับ จะดูหน้าเรียว',
    '💡 สีพีชเหมาะกับผิวอุ่น สีชมพูเหมาะกับผิวเย็น',
    '💡 ใช้แปรงขนาดใหญ่ แตะเบาๆ จะได้สีไม่จัดเกินไป',
  ],
  highlight: [
    '💡 ทาไฮไลท์ที่สันจมูก โหนกแก้ม ใต้คิ้ว และคิวปิดโบว์',
    '💡 ผิวมัน ใช้ไฮไลท์เนื้อฝุ่น ผิวแห้ง ใช้เนื้อครีม',
    '💡 อย่าทามากเกินไป เดี๋ยวจะดูมันแทนที่จะดูฉ่ำ',
    '💡 สีแชมเปญเหมาะกับทุกสีผิว',
  ],
  foundation: [
    '💡 เลือกสีรองพื้นที่ตรงกับสีคอ ไม่ใช่สีหน้า',
    '💡 ใช้ฟองน้ำชุบน้ำบิดหมาด แล้วแตะรองพื้น จะได้ผิวเนียนบาง',
    '💡 ทาบางๆ หลายชั้นดีกว่าทาหนาชั้นเดียว',
    '💡 บำรุงผิวและทาไพรเมอร์ก่อน รองพื้นจะติดทนขึ้น',
  ],
}

export default function PhotoEditor() {
  const [image, setImage] = useState(null)
  const [imageFile, setImageFile] = useState(null)
  const [filter, setFilter] = useState('')
  const [activeFilter, setActiveFilter] = useState('ปกติ')
  const [brightness, setBrightness] = useState(100)
  const [contrast, setContrast] = useState(100)
  const [saturation, setSaturation] = useState(100)

  // Makeup state
  const [landmarks, setLandmarks] = useState(null)
  const [loadingLandmarks, setLoadingLandmarks] = useState(false)
  const [activeMakeupPart, setActiveMakeupPart] = useState('lips')
  const [makeup, setMakeup] = useState({ ...DEFAULT_MAKEUP })

  // Product recommendations
  const [recommendations, setRecommendations] = useState({})
  const [loadingRecs, setLoadingRecs] = useState(false)

  // Saved looks
  const [savedLooks, setSavedLooks] = useState([])
  const [lookName, setLookName] = useState('')
  const [lookCategory, setLookCategory] = useState('อื่นๆ')
  const [savingLook, setSavingLook] = useState(false)

  // Tab state
  const [activeTab, setActiveTab] = useState('makeup')
  const [showBefore, setShowBefore] = useState(false)

  const fileRef = useRef(null)
  const canvasRef = useRef(null)
  const imgRef = useRef(null)
  const makeupCanvasRef = useRef(null)

  const handleFile = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setImage(URL.createObjectURL(file))
    setImageFile(file)
    setLandmarks(null)
    setMakeup({ ...DEFAULT_MAKEUP })
    setRecommendations({})

    // เรียก API detect landmarks
    setLoadingLandmarks(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await api.post('/landmarks/detect', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setLandmarks(res.data.landmarks)
    } catch (err) {
      console.warn('Landmark detection failed:', err)
      setLandmarks(null)
    } finally {
      setLoadingLandmarks(false)
    }
  }

  const getFilterStyle = () => {
    if (filter) return filter
    return `brightness(${brightness}%) contrast(${contrast}%) saturate(${saturation}%)`
  }

  const handleFilterSelect = (f) => {
    setFilter(f.style)
    setActiveFilter(f.name)
    setBrightness(100)
    setContrast(100)
    setSaturation(100)
  }

  const handleSliderChange = (setter, value) => {
    setter(value)
    setFilter('')
    setActiveFilter(null)
  }

  const handleReset = () => {
    setFilter('')
    setActiveFilter('ปกติ')
    setBrightness(100)
    setContrast(100)
    setSaturation(100)
    setMakeup({ ...DEFAULT_MAKEUP })
    setRecommendations({})
  }

  // Fetch saved looks
  useEffect(() => {
    api.get('/looks/').then(res => setSavedLooks(res.data)).catch(() => {})
  }, [])

  const saveLook = async () => {
    if (!lookName.trim()) return
    setSavingLook(true)
    try {
      await api.post('/looks/', {
        name: lookName,
        category: lookCategory,
        makeup_data: makeup,
        filter_data: { filter, brightness, contrast, saturation, activeFilter },
      })
      setLookName('')
      const res = await api.get('/looks/')
      setSavedLooks(res.data)
    } catch {}
    setSavingLook(false)
  }

  const loadLook = (look) => {
    setMakeup(look.makeup_data)
    if (look.filter_data) {
      setFilter(look.filter_data.filter || '')
      setBrightness(look.filter_data.brightness || 100)
      setContrast(look.filter_data.contrast || 100)
      setSaturation(look.filter_data.saturation || 100)
      setActiveFilter(look.filter_data.activeFilter || 'ปกติ')
    }
  }

  const deleteLook = async (lookId) => {
    try {
      await api.delete(`/looks/${lookId}`)
      setSavedLooks(prev => prev.filter(l => l.look_id !== lookId))
    } catch {}
  }

  const applyPreset = (preset) => {
    setMakeup({ ...preset.makeup })
    trackPresetApply(preset.name)
  }

  const fetchRecommendations = async () => {
    const usedParts = Object.entries(makeup)
      .filter(([_, v]) => v.color)
      .map(([k]) => k)
    if (usedParts.length === 0) return
    setLoadingRecs(true)
    try {
      const res = await api.get(`/products/makeup-recommendations?parts=${usedParts.join(',')}`)
      setRecommendations(res.data)
    } catch (err) {
      console.warn('Failed to fetch recommendations:', err)
    } finally {
      setLoadingRecs(false)
    }
  }

  const updateMakeup = (part, key, value) => {
    setMakeup(prev => ({
      ...prev,
      [part]: { ...prev[part], [key]: value }
    }))
    if (key === 'color' && value) trackMakeupSelect(part, value)
  }

  // ── Draw makeup on canvas ──
  const drawMakeup = useCallback(() => {
    const canvas = makeupCanvasRef.current
    const img = imgRef.current
    if (!canvas || !img || !landmarks) return

    const rect = img.getBoundingClientRect()
    canvas.width = rect.width
    canvas.height = rect.height
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    const w = canvas.width
    const h = canvas.height

    const getPoint = (idx) => ({
      x: landmarks[idx].x * w,
      y: landmarks[idx].y * h
    })

    // วาดปาก (Lips)
    if (makeup.lips.color) {
      const alpha = makeup.lips.intensity / 100
      ctx.save()
      ctx.globalAlpha = alpha
      ctx.fillStyle = makeup.lips.color

      // Outer lips
      ctx.beginPath()
      const outerPts = LANDMARK_GROUPS.lips.outer.map(i => getPoint(i))
      ctx.moveTo(outerPts[0].x, outerPts[0].y)
      for (let i = 1; i < outerPts.length; i++) {
        ctx.lineTo(outerPts[i].x, outerPts[i].y)
      }
      ctx.closePath()
      ctx.fill()

      // Inner lips (fill too for full coverage)
      ctx.beginPath()
      const innerPts = LANDMARK_GROUPS.lips.inner.map(i => getPoint(i))
      ctx.moveTo(innerPts[0].x, innerPts[0].y)
      for (let i = 1; i < innerPts.length; i++) {
        ctx.lineTo(innerPts[i].x, innerPts[i].y)
      }
      ctx.closePath()
      ctx.fill()
      ctx.restore()
    }

    // วาดอายแชโดว์ (Eyes)
    if (makeup.eyes.color) {
      const alpha = makeup.eyes.intensity / 100
      ctx.save()
      ctx.globalAlpha = alpha
      ctx.fillStyle = makeup.eyes.color

      ;['left', 'right'].forEach(side => {
        const pts = LANDMARK_GROUPS.eyes[side].map(i => getPoint(i))
        // วาดอายแชโดว์เหนือตา
        ctx.beginPath()
        const topPts = side === 'left' ? pts.slice(0, 3) : pts.slice(0, 3)
        const eyeWidth = Math.abs(pts[3].x - pts[0].x)
        const eyeHeight = eyeWidth * 0.3

        ctx.moveTo(pts[0].x, pts[0].y)
        ctx.quadraticCurveTo(
          (pts[0].x + pts[3].x) / 2,
          pts[1].y - eyeHeight,
          pts[3].x,
          pts[3].y
        )
        ctx.quadraticCurveTo(
          (pts[0].x + pts[3].x) / 2,
          pts[1].y,
          pts[0].x,
          pts[0].y
        )
        ctx.closePath()
        ctx.fill()
      })
      ctx.restore()
    }

    // วาดคิ้ว (Eyebrows)
    if (makeup.eyebrows.color) {
      const alpha = makeup.eyebrows.intensity / 100
      ctx.save()
      ctx.globalAlpha = alpha
      ctx.strokeStyle = makeup.eyebrows.color
      ctx.lineWidth = Math.max(2, w * 0.006)
      ctx.lineCap = 'round'
      ctx.lineJoin = 'round'

      ;['left', 'right'].forEach(side => {
        const pts = LANDMARK_GROUPS.eyebrows[side].map(i => getPoint(i))
        // วาดคิ้วหนาขึ้น
        for (let offset = -1; offset <= 1; offset++) {
          ctx.beginPath()
          ctx.moveTo(pts[0].x, pts[0].y + offset)
          for (let i = 1; i < pts.length; i++) {
            const prev = pts[i - 1]
            const curr = pts[i]
            const cpx = (prev.x + curr.x) / 2
            const cpy = (prev.y + curr.y) / 2 + offset
            ctx.quadraticCurveTo(prev.x, prev.y + offset, cpx, cpy)
          }
          ctx.stroke()
        }
      })
      ctx.restore()
    }

    // วาด contour จมูก (Nose)
    if (makeup.nose.color) {
      const alpha = makeup.nose.intensity / 100
      ctx.save()
      ctx.globalAlpha = alpha

      const bridgePts = LANDMARK_GROUPS.nose.bridge.map(i => getPoint(i))
      const bottomPts = LANDMARK_GROUPS.nose.bottom.map(i => getPoint(i))

      if (makeup.nose.color === '#ffffff') {
        // ไฮไลท์ — เส้นสว่างตรงสันจมูก
        ctx.strokeStyle = 'rgba(255,255,255,0.6)'
        ctx.lineWidth = Math.max(3, w * 0.008)
        ctx.lineCap = 'round'
        ctx.beginPath()
        ctx.moveTo(bridgePts[0].x, bridgePts[0].y)
        for (let i = 1; i < bridgePts.length; i++) {
          ctx.lineTo(bridgePts[i].x, bridgePts[i].y)
        }
        ctx.stroke()
      } else {
        // เฉดดิ้ง — เงาด้านข้างจมูก
        ctx.strokeStyle = makeup.nose.color
        ctx.lineWidth = Math.max(2, w * 0.004)
        ctx.lineCap = 'round'

        // เส้นซ้าย
        ctx.beginPath()
        ctx.moveTo(bridgePts[0].x - w * 0.015, bridgePts[0].y)
        ctx.lineTo(bottomPts[0].x, bottomPts[0].y)
        ctx.stroke()

        // เส้นขวา
        ctx.beginPath()
        ctx.moveTo(bridgePts[0].x + w * 0.015, bridgePts[0].y)
        ctx.lineTo(bottomPts[4].x, bottomPts[4].y)
        ctx.stroke()
      }
      ctx.restore()
    }

    // วาดบลัช (Blush)
    if (makeup.blush.color) {
      const alpha = makeup.blush.intensity / 100
      ctx.save()
      ctx.globalAlpha = alpha

      ;['left', 'right'].forEach(side => {
        const pts = LANDMARK_GROUPS.blush[side].map(i => getPoint(i))
        const cx = pts.reduce((s, p) => s + p.x, 0) / pts.length
        const cy = pts.reduce((s, p) => s + p.y, 0) / pts.length
        const radius = w * 0.06

        const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius)
        gradient.addColorStop(0, makeup.blush.color)
        gradient.addColorStop(1, 'transparent')

        ctx.fillStyle = gradient
        ctx.beginPath()
        ctx.arc(cx, cy, radius, 0, Math.PI * 2)
        ctx.fill()
      })
      ctx.restore()
    }

    // วาดอายไลเนอร์ (Eyeliner)
    if (makeup.eyeliner.color) {
      const alpha = makeup.eyeliner.intensity / 100
      ctx.save()
      ctx.globalAlpha = alpha
      ctx.strokeStyle = makeup.eyeliner.color
      ctx.lineWidth = Math.max(1.5, w * 0.003)
      ctx.lineCap = 'round'

      ;['left', 'right'].forEach(side => {
        const pts = LANDMARK_GROUPS.eyeliner[side].map(i => getPoint(i))
        // เส้นบนตา
        ctx.beginPath()
        ctx.moveTo(pts[0].x, pts[0].y)
        ctx.quadraticCurveTo((pts[1].x + pts[2].x) / 2, Math.min(pts[1].y, pts[2].y), pts[3].x, pts[3].y)
        ctx.stroke()
        // เส้นล่างตา (บางกว่า)
        ctx.lineWidth = Math.max(1, w * 0.002)
        ctx.beginPath()
        ctx.moveTo(pts[0].x, pts[0].y)
        ctx.quadraticCurveTo((pts[4].x + pts[5].x) / 2, Math.max(pts[4].y, pts[5].y), pts[3].x, pts[3].y)
        ctx.stroke()
      })
      ctx.restore()
    }

    // วาดขนตา (Lashes)
    if (makeup.lashes.color) {
      const alpha = makeup.lashes.intensity / 100
      ctx.save()
      ctx.globalAlpha = alpha
      ctx.strokeStyle = makeup.lashes.color
      ctx.lineWidth = Math.max(1, w * 0.002)
      ctx.lineCap = 'round'

      ;['left', 'right'].forEach(side => {
        const pts = LANDMARK_GROUPS.lashes[side].map(i => getPoint(i))
        const topPts = [pts[0], pts[1], pts[2], pts[3]]
        // วาดขนตาหลายเส้นจากขอบบนตาขึ้นไป
        for (let j = 0; j < topPts.length; j++) {
          const p = topPts[j]
          const lashLen = w * 0.012
          for (let k = -1; k <= 1; k++) {
            ctx.beginPath()
            ctx.moveTo(p.x + k * w * 0.003, p.y)
            ctx.lineTo(p.x + k * w * 0.004, p.y - lashLen)
            ctx.stroke()
          }
        }
      })
      ctx.restore()
    }

    // วาดไฮไลท์ (Highlight)
    if (makeup.highlight.color) {
      const alpha = makeup.highlight.intensity / 100
      ctx.save()
      ctx.globalAlpha = alpha

      // ไฮไลท์สันจมูก
      const bridgePts = LANDMARK_GROUPS.highlight.bridge.map(i => getPoint(i))
      ctx.strokeStyle = makeup.highlight.color === '#ffffff' ? 'rgba(255,255,255,0.7)' : makeup.highlight.color
      ctx.lineWidth = Math.max(3, w * 0.008)
      ctx.lineCap = 'round'
      ctx.beginPath()
      ctx.moveTo(bridgePts[0].x, bridgePts[0].y)
      bridgePts.slice(1).forEach(p => ctx.lineTo(p.x, p.y))
      ctx.stroke()

      // ไฮไลท์โหนกแก้ม
      ;['cheekLeft', 'cheekRight'].forEach(side => {
        const pts = LANDMARK_GROUPS.highlight[side].map(i => getPoint(i))
        const cx = pts.reduce((s, p) => s + p.x, 0) / pts.length
        const cy = pts.reduce((s, p) => s + p.y, 0) / pts.length - h * 0.02
        const radius = w * 0.035
        const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius)
        gradient.addColorStop(0, makeup.highlight.color === '#ffffff' ? 'rgba(255,255,255,0.5)' : makeup.highlight.color)
        gradient.addColorStop(1, 'transparent')
        ctx.fillStyle = gradient
        ctx.beginPath()
        ctx.arc(cx, cy, radius, 0, Math.PI * 2)
        ctx.fill()
      })
      ctx.restore()
    }

    // วาดรองพื้น (Foundation)
    if (makeup.foundation.color) {
      const alpha = makeup.foundation.intensity / 100
      ctx.save()
      ctx.globalAlpha = alpha
      ctx.fillStyle = makeup.foundation.color

      // วาดทับทั้งใบหน้าตาม jaw line
      const jawPts = LANDMARK_GROUPS.foundation.jaw.map(i => getPoint(i))
      const foreheadY = getPoint(19).y - h * 0.05
      ctx.beginPath()
      ctx.moveTo(jawPts[0].x, jawPts[0].y)
      jawPts.forEach(p => ctx.lineTo(p.x, p.y))
      // เส้นบนกลับขึ้นไปหน้าผาก
      ctx.lineTo(jawPts[jawPts.length - 1].x, foreheadY)
      ctx.quadraticCurveTo((jawPts[0].x + jawPts[jawPts.length - 1].x) / 2, foreheadY - h * 0.02, jawPts[0].x, foreheadY)
      ctx.closePath()
      ctx.fill()
      ctx.restore()
    }
  }, [landmarks, makeup])

  useEffect(() => {
    drawMakeup()
  }, [drawMakeup])

  // Redraw on window resize
  useEffect(() => {
    const handleResize = () => drawMakeup()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [drawMakeup])

  const handleDownload = () => {
    const img = imgRef.current
    if (!img) return

    const canvas = document.createElement('canvas')
    canvas.width = img.naturalWidth
    canvas.height = img.naturalHeight
    const ctx = canvas.getContext('2d')

    // วาดรูปพร้อม filter
    ctx.filter = getFilterStyle()
    ctx.drawImage(img, 0, 0)
    ctx.filter = 'none'

    // วาด makeup ทับ (scale จาก display size → natural size)
    if (landmarks) {
      const w = img.naturalWidth
      const h = img.naturalHeight
      const getPoint = (idx) => ({
        x: landmarks[idx].x * w,
        y: landmarks[idx].y * h
      })

      // Lips
      if (makeup.lips.color) {
        ctx.save()
        ctx.globalAlpha = makeup.lips.intensity / 100
        ctx.fillStyle = makeup.lips.color
        ctx.beginPath()
        const outerPts = LANDMARK_GROUPS.lips.outer.map(i => getPoint(i))
        ctx.moveTo(outerPts[0].x, outerPts[0].y)
        outerPts.slice(1).forEach(p => ctx.lineTo(p.x, p.y))
        ctx.closePath()
        ctx.fill()
        ctx.beginPath()
        const innerPts = LANDMARK_GROUPS.lips.inner.map(i => getPoint(i))
        ctx.moveTo(innerPts[0].x, innerPts[0].y)
        innerPts.slice(1).forEach(p => ctx.lineTo(p.x, p.y))
        ctx.closePath()
        ctx.fill()
        ctx.restore()
      }

      // Eyes
      if (makeup.eyes.color) {
        ctx.save()
        ctx.globalAlpha = makeup.eyes.intensity / 100
        ctx.fillStyle = makeup.eyes.color
        ;['left', 'right'].forEach(side => {
          const pts = LANDMARK_GROUPS.eyes[side].map(i => getPoint(i))
          const eyeWidth = Math.abs(pts[3].x - pts[0].x)
          const eyeHeight = eyeWidth * 0.3
          ctx.beginPath()
          ctx.moveTo(pts[0].x, pts[0].y)
          ctx.quadraticCurveTo((pts[0].x + pts[3].x) / 2, pts[1].y - eyeHeight, pts[3].x, pts[3].y)
          ctx.quadraticCurveTo((pts[0].x + pts[3].x) / 2, pts[1].y, pts[0].x, pts[0].y)
          ctx.closePath()
          ctx.fill()
        })
        ctx.restore()
      }

      // Eyebrows
      if (makeup.eyebrows.color) {
        ctx.save()
        ctx.globalAlpha = makeup.eyebrows.intensity / 100
        ctx.strokeStyle = makeup.eyebrows.color
        ctx.lineWidth = Math.max(2, w * 0.006)
        ctx.lineCap = 'round'
        ctx.lineJoin = 'round'
        ;['left', 'right'].forEach(side => {
          const pts = LANDMARK_GROUPS.eyebrows[side].map(i => getPoint(i))
          for (let offset = -1; offset <= 1; offset++) {
            ctx.beginPath()
            ctx.moveTo(pts[0].x, pts[0].y + offset)
            for (let i = 1; i < pts.length; i++) {
              const prev = pts[i - 1]
              const curr = pts[i]
              ctx.quadraticCurveTo(prev.x, prev.y + offset, (prev.x + curr.x) / 2, (prev.y + curr.y) / 2 + offset)
            }
            ctx.stroke()
          }
        })
        ctx.restore()
      }

      // Nose
      if (makeup.nose.color) {
        ctx.save()
        ctx.globalAlpha = makeup.nose.intensity / 100
        const bridgePts = LANDMARK_GROUPS.nose.bridge.map(i => getPoint(i))
        const bottomPts = LANDMARK_GROUPS.nose.bottom.map(i => getPoint(i))
        if (makeup.nose.color === '#ffffff') {
          ctx.strokeStyle = 'rgba(255,255,255,0.6)'
          ctx.lineWidth = Math.max(3, w * 0.008)
          ctx.lineCap = 'round'
          ctx.beginPath()
          ctx.moveTo(bridgePts[0].x, bridgePts[0].y)
          bridgePts.slice(1).forEach(p => ctx.lineTo(p.x, p.y))
          ctx.stroke()
        } else {
          ctx.strokeStyle = makeup.nose.color
          ctx.lineWidth = Math.max(2, w * 0.004)
          ctx.lineCap = 'round'
          ctx.beginPath()
          ctx.moveTo(bridgePts[0].x - w * 0.015, bridgePts[0].y)
          ctx.lineTo(bottomPts[0].x, bottomPts[0].y)
          ctx.stroke()
          ctx.beginPath()
          ctx.moveTo(bridgePts[0].x + w * 0.015, bridgePts[0].y)
          ctx.lineTo(bottomPts[4].x, bottomPts[4].y)
          ctx.stroke()
        }
        ctx.restore()
      }

      // Blush
      if (makeup.blush.color) {
        ctx.save()
        ctx.globalAlpha = makeup.blush.intensity / 100
        ;['left', 'right'].forEach(side => {
          const pts = LANDMARK_GROUPS.blush[side].map(i => getPoint(i))
          const cx = pts.reduce((s, p) => s + p.x, 0) / pts.length
          const cy = pts.reduce((s, p) => s + p.y, 0) / pts.length
          const radius = w * 0.06
          const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius)
          gradient.addColorStop(0, makeup.blush.color)
          gradient.addColorStop(1, 'transparent')
          ctx.fillStyle = gradient
          ctx.beginPath()
          ctx.arc(cx, cy, radius, 0, Math.PI * 2)
          ctx.fill()
        })
        ctx.restore()
      }
    }

    const link = document.createElement('a')
    link.download = 'auramatch_edited.png'
    link.href = canvas.toDataURL()
    link.click()
    trackDownload()
  }

  const TABS = [
    { id: 'presets', label: 'ลุคสำเร็จรูป', icon: '🎨' },
    { id: 'makeup', label: 'แต่งหน้า', icon: '💄' },
    { id: 'filter', label: 'ฟิลเตอร์', icon: '✨' },
    { id: 'adjust', label: 'ปรับแต่ง', icon: '⚙️' },
    { id: 'tips', label: 'เคล็ดลับ', icon: '💡' },
    { id: 'recommend', label: 'แนะนำ', icon: '🛍️' },
    { id: 'mylooks', label: 'ลุคของฉัน', icon: '❤️' },
  ]

  const hasAnyMakeup = Object.entries(makeup).some(([_, v]) => v.color)

  return (
    <div className="pe">
      {!image ? (
        /* ── Upload ── */
        <div className="pe-upload-wrap">
          <div className="pe-upload" onClick={() => fileRef.current.click()}>
            <div className="pe-upload-icon"><ImagePlus size={40} /></div>
            <h2 className="pe-upload-title">เริ่มแต่งรูป</h2>
            <p className="pe-upload-desc">อัปโหลดรูปภาพเพื่อเริ่มแต่งหน้าและใส่ฟิลเตอร์</p>
            <span className="pe-upload-btn">เลือกรูปภาพ</span>
          </div>
        </div>
      ) : (
        <div className="pe-editor">
          {/* ── Top Bar ── */}
          <div className="pe-topbar">
            <button className="pe-topbar-btn" onClick={() => { setImage(null); setImageFile(null); setLandmarks(null); setMakeup({...DEFAULT_MAKEUP}); setRecommendations({}); }}>
              <X size={18} /> <span>ปิด</span>
            </button>
            <div className="pe-topbar-actions">
              <button className="pe-topbar-btn" onClick={() => fileRef.current.click()}><Upload size={16} /> <span>เปลี่ยนรูป</span></button>
              <button className="pe-topbar-btn" onClick={handleReset}><RotateCcw size={16} /> <span>รีเซ็ต</span></button>
              <button className="pe-topbar-btn pe-topbar-btn--save" onClick={handleDownload}><Download size={16} /> <span>บันทึก</span></button>
            </div>
          </div>

          {/* ── Image Preview ── */}
          <div className="pe-preview">
            <div className="pe-preview-inner">
              <img ref={imgRef} src={image} alt="edit" className="pe-img"
                style={{ filter: getFilterStyle(), opacity: showBefore ? 0 : 1 }} onLoad={drawMakeup} />
              {showBefore && <img src={image} alt="before" className="pe-img pe-img-before" />}
              <canvas ref={makeupCanvasRef} className="pe-makeup-overlay" style={{ opacity: showBefore ? 0 : 1 }} />
            </div>
            {loadingLandmarks && (
              <div className="pe-loading"><Loader2 size={18} className="spin" /> กำลังตรวจจับใบหน้า...</div>
            )}
            {/* Before/After Button */}
            {hasAnyMakeup && (
              <button className="pe-before-btn"
                onMouseDown={() => setShowBefore(true)} onMouseUp={() => setShowBefore(false)}
                onMouseLeave={() => setShowBefore(false)}
                onTouchStart={() => setShowBefore(true)} onTouchEnd={() => setShowBefore(false)}>
                {showBefore ? '👁 ก่อนแต่ง' : '👁 กดค้างดูก่อนแต่ง'}
              </button>
            )}
          </div>

          {/* ── Bottom Panel ── */}
          <div className="pe-bottom">
            {/* Tab Bar */}
            <div className="pe-tabs">
              {TABS.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`pe-tab ${activeTab === tab.id ? 'pe-tab--active' : ''}`}
                >
                  <span className="pe-tab-icon">{tab.icon}</span>
                  <span className="pe-tab-label">{tab.label}</span>
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="pe-tab-content">
              {/* ── ลุคสำเร็จรูป ── */}
              {activeTab === 'presets' && (
                <div className="pe-panel">
                  {!landmarks ? (
                    <p className="pe-panel-msg">อัปโหลดรูปก่อน แล้วเลือกลุคที่ชอบได้เลย</p>
                  ) : (
                    <div className="pe-presets-grid">
                      {MAKEUP_PRESETS.map((preset, i) => (
                        <button key={i} className="pe-preset-card" onClick={() => applyPreset(preset)}>
                          <span className="pe-preset-icon">{preset.icon}</span>
                          <span className="pe-preset-name">{preset.name}</span>
                          <span className="pe-preset-desc">{preset.desc}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* ── แต่งหน้า ── */}
              {activeTab === 'makeup' && (
                <div className="pe-panel">
                  {!landmarks ? (
                    <p className="pe-panel-msg">กำลังโหลด... กรุณารอสักครู่</p>
                  ) : (
                    <>
                      <div className="pe-part-bar">
                        {MAKEUP_PARTS.map(part => (
                          <button key={part.id} onClick={() => setActiveMakeupPart(part.id)}
                            className={`pe-part ${activeMakeupPart === part.id ? 'pe-part--active' : ''}`}>
                            <span className="pe-part-icon">{part.icon}</span>
                            <span className="pe-part-label">{part.label}</span>
                          </button>
                        ))}
                      </div>
                      <div className="pe-colors">
                        <button onClick={() => updateMakeup(activeMakeupPart, 'color', null)}
                          className={`pe-swatch pe-swatch--none ${!makeup[activeMakeupPart].color ? 'pe-swatch--active' : ''}`}>✕</button>
                        {MAKEUP_COLORS[activeMakeupPart].map(c => (
                          <button key={c.color} onClick={() => updateMakeup(activeMakeupPart, 'color', c.color)}
                            className={`pe-swatch ${makeup[activeMakeupPart].color === c.color ? 'pe-swatch--active' : ''}`}
                            style={{ backgroundColor: c.color }} title={c.name} />
                        ))}
                      </div>
                      {makeup[activeMakeupPart].color && (
                        <div className="pe-slider-row">
                          <span className="pe-slider-label">ความเข้ม</span>
                          <input type="range" min={5} max={100} value={makeup[activeMakeupPart].intensity}
                            onChange={(e) => updateMakeup(activeMakeupPart, 'intensity', Number(e.target.value))}
                            className="pe-range"
                            style={{ background: `linear-gradient(to right,#ec4899 ${makeup[activeMakeupPart].intensity}%,#e5e7eb ${makeup[activeMakeupPart].intensity}%)` }} />
                          <span className="pe-slider-val">{makeup[activeMakeupPart].intensity}%</span>
                        </div>
                      )}
                    </>
                  )}
                </div>
              )}

              {/* ── ฟิลเตอร์ ── */}
              {activeTab === 'filter' && (
                <div className="pe-panel">
                  <div className="pe-filter-scroll">
                    {FILTERS.map((f, i) => (
                      <button key={f.name} onClick={() => handleFilterSelect(f)}
                        className={`pe-filter ${activeFilter === f.name ? 'pe-filter--active' : ''}`}>
                        <span className="pe-filter-icon">{FILTER_ICONS[i]}</span>
                        <span className="pe-filter-name">{f.name}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* ── ปรับแต่ง ── */}
              {activeTab === 'adjust' && (
                <div className="pe-panel pe-adjust-panel">
                  <div className="pe-slider-row">
                    <span className="pe-slider-label">☀️ สว่าง</span>
                    <input type="range" min={50} max={150} value={brightness}
                      onChange={(e) => handleSliderChange(setBrightness, Number(e.target.value))}
                      className="pe-range" style={{ background: `linear-gradient(to right,#a855f7 ${(brightness-50)}%,#e5e7eb ${(brightness-50)}%)` }} />
                    <span className="pe-slider-val">{brightness}%</span>
                  </div>
                  <div className="pe-slider-row">
                    <span className="pe-slider-label">◐ คอนทราสต์</span>
                    <input type="range" min={50} max={150} value={contrast}
                      onChange={(e) => handleSliderChange(setContrast, Number(e.target.value))}
                      className="pe-range" style={{ background: `linear-gradient(to right,#8b5cf6 ${(contrast-50)}%,#e5e7eb ${(contrast-50)}%)` }} />
                    <span className="pe-slider-val">{contrast}%</span>
                  </div>
                  <div className="pe-slider-row">
                    <span className="pe-slider-label">🎨 อิ่มตัว</span>
                    <input type="range" min={50} max={200} value={saturation}
                      onChange={(e) => handleSliderChange(setSaturation, Number(e.target.value))}
                      className="pe-range" style={{ background: `linear-gradient(to right,#ec4899 ${((saturation-50)/1.5)}%,#e5e7eb ${((saturation-50)/1.5)}%)` }} />
                    <span className="pe-slider-val">{saturation}%</span>
                  </div>
                </div>
              )}

              {/* ── เคล็ดลับ ── */}
              {activeTab === 'tips' && (
                <div className="pe-panel">
                  <div className="pe-tips-list">
                    {(MAKEUP_TIPS[activeMakeupPart] || MAKEUP_TIPS.lips).map((tip, i) => (
                      <div key={i} className="pe-tip-card">{tip}</div>
                    ))}
                  </div>
                  <p className="pe-tips-hint">เปลี่ยนหมวดที่แท็บ "แต่งหน้า" เพื่อดูเคล็ดลับส่วนอื่น</p>
                </div>
              )}

              {/* ── แนะนำสินค้า ── */}
              {activeTab === 'recommend' && (
                <div className="pe-panel">
                  {!hasAnyMakeup ? (
                    <p className="pe-panel-msg">เลือกแต่งหน้าอย่างน้อย 1 ส่วนก่อน แล้วกลับมาดูสินค้าแนะนำ</p>
                  ) : (
                    <>
                      <button onClick={fetchRecommendations} disabled={loadingRecs} className="pe-rec-btn">
                        {loadingRecs ? <><Loader2 size={14} className="spin" /> กำลังค้นหา...</> : <><ShoppingBag size={14} /> ดูสินค้าแนะนำ</>}
                      </button>
                      {Object.keys(recommendations).length > 0 && (
                        <div className="pe-rec-sections">
                          {Object.entries(recommendations).map(([part, products]) => {
                            if (!products || products.length === 0) return null
                            const partInfo = MAKEUP_PARTS.find(p => p.id === part)
                            return (
                              <div key={part} className="pe-rec-section">
                                <div className="pe-rec-section-title">{partInfo?.icon} {partInfo?.label}</div>
                                <div className="pe-rec-grid">
                                  {products.map(product => (
                                    <div key={product.product_id} className="pe-rec-card">
                                      {product.image_url && <div className="pe-rec-img"><img src={product.image_url} alt={product.name} /></div>}
                                      <div className="pe-rec-info">
                                        {product.brand_name && <span className="pe-rec-brand">{product.brand_name}</span>}
                                        <span className="pe-rec-name">{product.name}</span>
                                        <span className="pe-rec-price">฿{product.price.toLocaleString()}</span>
                                        {product.links?.length > 0 && (
                                          <div className="pe-rec-links">
                                            {product.links.map((link, i) => (
                                              <a key={i} href={link.url} target="_blank" rel="noopener noreferrer"
                                                className={`pe-rec-link pe-rec-link--${link.platform}`}>
                                                {link.platform} <ExternalLink size={9} />
                                              </a>
                                            ))}
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )
                          })}
                        </div>
                      )}
                    </>
                  )}
                </div>
              )}

              {/* ── ลุคของฉัน ── */}
              {activeTab === 'mylooks' && (
                <div className="pe-panel">
                  {/* บันทึกลุคใหม่ */}
                  {hasAnyMakeup && (
                    <div className="pe-save-look">
                      <div className="pe-save-look-title"><Heart size={14} /> บันทึกลุคปัจจุบัน</div>
                      <input type="text" placeholder="ตั้งชื่อลุค เช่น ลุคไปทำงาน" value={lookName}
                        onChange={e => setLookName(e.target.value)} className="pe-save-look-input" />
                      <div className="pe-save-look-row">
                        <select value={lookCategory} onChange={e => setLookCategory(e.target.value)} className="pe-save-look-select">
                          {['กลางวัน', 'กลางคืน', 'ปาร์ตี้', 'ทำงาน', 'ลุคเกาหลี', 'ลุคธรรมชาติ', 'อื่นๆ'].map(c => (
                            <option key={c} value={c}>{c}</option>
                          ))}
                        </select>
                        <button onClick={saveLook} disabled={!lookName.trim() || savingLook} className="pe-save-look-btn">
                          {savingLook ? <Loader2 size={14} className="spin" /> : <Heart size={14} />} บันทึก
                        </button>
                      </div>
                    </div>
                  )}

                  {/* รายการลุคที่บันทึกไว้ */}
                  {savedLooks.length === 0 ? (
                    <p className="pe-panel-msg">ยังไม่มีลุคที่บันทึก — แต่งหน้าแล้วกดบันทึกเลย</p>
                  ) : (
                    <div className="pe-looks-list">
                      {savedLooks.map(look => (
                        <div key={look.look_id} className="pe-look-card">
                          <div className="pe-look-info">
                            <span className="pe-look-name">{look.name}</span>
                            <span className="pe-look-cat">{look.category || 'อื่นๆ'}</span>
                          </div>
                          <div className="pe-look-actions">
                            <button className="pe-look-load" onClick={() => loadLook(look)}>ใช้ลุคนี้</button>
                            <button className="pe-look-delete" onClick={() => deleteLook(look.look_id)}><Trash2 size={13} /></button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      <input ref={fileRef} type="file" accept="image/*" className="sr-only" onChange={handleFile} />
      <canvas ref={canvasRef} className="sr-only" />
    </div>
  )
}

function SliderControl({ label, icon, value, min, max, onChange, color = 'purple' }) {
  const percentage = ((value - min) / (max - min)) * 100

  const colorMap = {
    purple: '#a855f7',
    violet: '#8b5cf6',
    pink: '#ec4899',
  }

  return (
    <div className={`slider-control slider-control--${color}`}>
      <div className="slider-header">
        <div className="slider-label-group">
          <span className="slider-icon">{icon}</span>
          <span className="slider-label">{label}</span>
        </div>
        <span className={`slider-value slider-value--${color}`}>
          {value}%
        </span>
      </div>
      <div className="slider-input-wrapper">
        <input
          type="range"
          min={min}
          max={max}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className={`slider-range slider-range--${color}`}
          style={{
            background: `linear-gradient(to right, ${colorMap[color]} ${percentage}%, #e5e7eb ${percentage}%)`
          }}
        />
      </div>
      <div className="slider-ticks">
        <span>{min}%</span>
        <span>{max}%</span>
      </div>
    </div>
  )
}
