import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../api/axios'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Send, Sparkles, Loader2, ImagePlus, X, MessageSquarePlus } from 'lucide-react'
import './GeminiChat.css'

export default function GeminiChat() {
  // --- All hooks declared first (React Hook Rules) ---
  const { user } = useAuth()
  const navigate = useNavigate()
  const [messages, setMessages] = useState([])
  const [prompt, setPrompt] = useState('')
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const fileRef = useRef(null)
  const chatEndRef = useRef(null)

  // Restore session from sessionStorage on mount
  useEffect(() => {
    if (!user) return
    const savedId = sessionStorage.getItem('gemini_session_id')
    if (!savedId) return

    const sid = Number(savedId)
    setSessionId(sid)
    api.get(`/gemini/session/${sid}/messages`)
      .then(res => {
        const restored = []
        for (const msg of res.data) {
          if (msg.prompt) {
            restored.push({ role: 'user', prompt: msg.prompt, image_input: msg.image_input || null })
          }
          if (msg.response) {
            restored.push({ role: 'model', response: msg.response })
          }
        }
        setMessages(restored)
      })
      .catch(() => {
        sessionStorage.removeItem('gemini_session_id')
        setSessionId(null)
      })
  }, [user])

  // Auto-scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // --- Auth guard early return (after all hooks) ---
  if (!user) {
    return (
      <div className="gemini-page">
        <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-100 to-pink-100 flex items-center justify-center">
            <Sparkles size={28} className="text-purple-400" />
          </div>
          <p className="text-gray-500 font-[Prompt] text-lg">
            กรุณาเข้าสู่ระบบก่อนใช้งาน
          </p>
          <button
            onClick={() => navigate('/login')}
            className="px-6 py-2.5 rounded-xl text-white font-medium bg-gradient-to-r from-purple-600 via-purple-400 to-pink-400 shadow-lg shadow-purple-300/25 hover:scale-105 transition-transform cursor-pointer"
          >
            เข้าสู่ระบบ
          </button>
        </div>
      </div>
    )
  }

  const startSession = async () => {
    const res = await api.post('/gemini/session?title=New Chat')
    const sid = res.data.session_id
    sessionStorage.setItem('gemini_session_id', String(sid))
    return sid
  }

  const handleFile = (e) => {
    const f = e.target.files[0]
    if (!f) return
    setFile(f)
    setPreview(URL.createObjectURL(f))
  }

  const clearFile = () => {
    setFile(null)
    setPreview(null)
    if (fileRef.current) fileRef.current.value = ''
  }

  const handleNewChat = () => {
    setMessages([])
    setSessionId(null)
    setPrompt('')
    clearFile()
    sessionStorage.removeItem('gemini_session_id')
  }

  const handleSend = async () => {
    if (!prompt.trim()) return
    setLoading(true)

    // Await session creation to avoid race condition
    let sid = sessionId
    if (!sid) {
      sid = await startSession()
      setSessionId(sid)
    }

    const userMsg = { role: 'user', prompt, image_input: preview }
    setMessages(prev => [...prev, userMsg])
    setPrompt('')
    setPreview(null)

    try {
      let res
      if (file) {
        const formData = new FormData()
        formData.append('file', file)
        setFile(null)
        res = await api.post(
          `/gemini/session/${sid}/chat?prompt=${encodeURIComponent(prompt)}`,
          formData,
          { headers: { 'Content-Type': 'multipart/form-data' } }
        )
      } else {
        res = await api.post(
          `/gemini/session/${sid}/chat?prompt=${encodeURIComponent(prompt)}`
        )
      }
      setMessages(prev => [...prev, { role: 'model', response: res.data.response }])
    } catch {
      setMessages(prev => [...prev, { role: 'model', response: 'เกิดข้อผิดพลาด กรุณาลองใหม่' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="gemini-page">
      <div className="gemini-container">

        {/* Header */}
        <div className="gemini-header">
          <div className="flex items-center justify-between mb-3">
            <div className="gemini-header-inner">
              <div className="gemini-logo-icon">
                <Sparkles size={24} />
              </div>
              <h1 className="gemini-title">
                Gemini AI Assistant
              </h1>
            </div>
            {sessionId && (
              <button
                onClick={handleNewChat}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-purple-200 text-purple-600 text-sm font-medium hover:bg-purple-50 hover:border-purple-400 transition-all cursor-pointer"
              >
                <MessageSquarePlus size={16} />
                สร้างแชทใหม่
              </button>
            )}
          </div>
          <p className="gemini-subtitle">
            พิมพ์ prompt เพื่อแต่งรูปหรือขอคำแนะนำด้านความงาม
          </p>
        </div>

        {/* Chat Area */}
        <div className="gemini-chat-area">
          <div className="gemini-chat-scroll">

            {/* Empty state */}
            {messages.length === 0 && !loading && (
              <div className="gemini-empty-state">
                <div className="gemini-empty-icon">
                  <Sparkles size={28} />
                </div>
                <p className="gemini-empty-text">
                  เริ่มต้นสนทนากับ Gemini AI
                </p>
              </div>
            )}

            {/* Messages */}
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`gemini-message-row ${msg.role === 'user' ? 'gemini-message-row--user' : 'gemini-message-row--model'}`}
              >
                {/* AI avatar */}
                {msg.role === 'model' && (
                  <div className="gemini-avatar gemini-avatar--ai">
                    <Sparkles size={14} />
                  </div>
                )}

                <div
                  className={`gemini-bubble ${
                    msg.role === 'user'
                      ? 'gemini-bubble--user'
                      : 'gemini-bubble--model'
                  }`}
                >
                  {msg.image_input && (
                    <img
                      src={msg.image_input}
                      className="gemini-bubble-image"
                      alt="uploaded"
                    />
                  )}
                  {msg.role === 'user' ? (
                    <p className="gemini-bubble-text">{msg.prompt}</p>
                  ) : (
                    <div className="gemini-bubble-text prose prose-purple prose-sm max-w-none">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.response}</ReactMarkdown>
                    </div>
                  )}
                </div>

                {/* User avatar */}
                {msg.role === 'user' && (
                  <div className="gemini-avatar gemini-avatar--user">
                    U
                  </div>
                )}
              </div>
            ))}

            {/* Loading indicator — pulsing dots */}
            {loading && (
              <div className="gemini-loading-row">
                <div className="gemini-loading-avatar">
                  <Sparkles size={14} />
                </div>
                <div className="gemini-loading-bubble">
                  <div className="flex items-center gap-1">
                    <span className="gemini-typing-dot" />
                    <span className="gemini-typing-dot" />
                    <span className="gemini-typing-dot" />
                  </div>
                  <span className="gemini-loading-text">กำลังคิด...</span>
                </div>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>
        </div>

        {/* Image preview */}
        {preview && (
          <div className="gemini-preview-bar">
            <div className="gemini-preview-wrapper">
              <img
                src={preview}
                alt="preview"
                className="gemini-preview-image"
              />
              <button
                onClick={clearFile}
                className="gemini-preview-remove"
              >
                <X size={12} />
              </button>
            </div>
          </div>
        )}

        {/* Input area */}
        <div className="gemini-input-bar">
          <button
            onClick={() => fileRef.current.click()}
            className="gemini-upload-btn"
            title="อัปโหลดรูปภาพ"
          >
            <ImagePlus size={18} />
          </button>
          <input ref={fileRef} type="file" accept="image/*" className="gemini-file-input" onChange={handleFile} />

          <input
            type="text"
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
            placeholder="พิมพ์ prompt เช่น แต่งรูปให้ดูเป็นธรรมชาติ..."
            className="gemini-text-input"
          />

          <button
            onClick={handleSend}
            disabled={loading || !prompt.trim()}
            className={`gemini-send-btn ${loading || !prompt.trim() ? 'gemini-send-btn--disabled' : 'gemini-send-btn--active'}`}
          >
            {loading ? (
              <Loader2 size={18} className="gemini-loading-spinner" />
            ) : (
              <Send size={18} />
            )}
          </button>
        </div>

      </div>
    </div>
  )
}
