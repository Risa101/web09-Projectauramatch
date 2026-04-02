import { useState, useRef, useEffect } from 'react'
import api from '../api/axios'
import { Send, Upload, Sparkles, Loader2, ImagePlus, X } from 'lucide-react'
import './GeminiChat.css'

export default function GeminiChat() {
  const [messages, setMessages] = useState([])
  const [prompt, setPrompt] = useState('')
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const fileRef = useRef(null)
  const chatEndRef = useRef(null)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const startSession = async () => {
    const res = await api.post('/gemini/session?title=New Chat')
    return res.data.session_id
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

  const handleSend = async () => {
    if (!prompt.trim()) return
    setLoading(true)

    const sid = sessionId || await startSession()
    if (!sessionId) setSessionId(sid)

    const userMsg = { role: 'user', prompt, image_input: preview }
    setMessages(prev => [...prev, userMsg])
    setPrompt('')
    setPreview(null)

    try {
      const formData = new FormData()
      if (file) formData.append('file', file)
      setFile(null)

      const res = await api.post(
        `/gemini/session/${sid}/chat?prompt=${encodeURIComponent(prompt)}`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
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
          <div className="gemini-header-inner">
            <div className="gemini-logo-icon">
              <Sparkles size={24} />
            </div>
            <h1 className="gemini-title">
              Gemini AI Assistant
            </h1>
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
                  <p className="gemini-bubble-text">{msg.prompt || msg.response}</p>
                </div>

                {/* User avatar */}
                {msg.role === 'user' && (
                  <div className="gemini-avatar gemini-avatar--user">
                    U
                  </div>
                )}
              </div>
            ))}

            {/* Loading indicator */}
            {loading && (
              <div className="gemini-loading-row">
                <div className="gemini-loading-avatar">
                  <Sparkles size={14} />
                </div>
                <div className="gemini-loading-bubble">
                  <Loader2 size={16} className="gemini-loading-spinner" />
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
