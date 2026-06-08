import { useState, useRef, useEffect, useCallback } from 'react'
import { useToast } from '../context/ToastContext'

const SUGGESTIONS = [
  'What happens if our top 3 engineers leave?',
  'Who are our biggest single points of failure?',
  'Which team has the most skill gaps?',
  'Simulate a 30% workload increase across all teams',
  'What is our overall organizational health?',
  'Who should we cross-train first?',
  'What is our retention risk?',
  'How is our resilience score?',
]

const WS_BASE = `ws://${window.location.hostname}:8000/ws/query`

function copyText(text) {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).catch(() => {})
  }
}

export default function ChatPanel({ onResult }) {
  const { addToast } = useToast()
  const [messages, setMessages] = useState(() => {
    try {
      const saved = localStorage.getItem('trupulse_chat')
      if (saved) return JSON.parse(saved)
    } catch {}
    return [
      { role: 'system', text: 'Ask me anything about your organization\'s workforce resilience. I can run simulations, analyze risks, and recommend actions.' },
    ]
  })
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [showSuggestions, setShowSuggestions] = useState(true)
  const [wsStatus, setWsStatus] = useState('connecting') // connecting | connected | fallback
  const endRef = useRef(null)
  const inputRef = useRef(null)
  const wsRef = useRef(null)
  const streamingIdRef = useRef(null)

  const scrollToBottom = useCallback(() => {
    requestAnimationFrame(() => {
      endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
    })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  // Persist to localStorage
  useEffect(() => {
    localStorage.setItem('trupulse_chat', JSON.stringify(messages))
  }, [messages])

  // Global keyboard shortcut: Ctrl+/ or Cmd+/ to focus input
  useEffect(() => {
    const handler = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault()
        inputRef.current?.focus()
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  // WebSocket connection
  useEffect(() => {
    let ws
    let reconnectTimer

    function connect() {
      try {
        ws = new WebSocket(WS_BASE)
        wsRef.current = ws

        ws.onopen = () => setWsStatus('connected')

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            if (data.type === 'answer') {
              // Update or create streaming assistant message
              setMessages((prev) => {
                const idx = prev.findIndex((m) => m._id === streamingIdRef.current)
                if (idx >= 0) {
                  const updated = [...prev]
                  updated[idx] = { ...updated[idx], text: data.content, data: data }
                  return updated
                }
                return prev
              })
            } else if (data.type === 'done') {
              setLoading(false)
              streamingIdRef.current = null
              const lastMsg = messages[messages.length - 1]
              if (lastMsg && lastMsg.role === 'assistant' && lastMsg._id) {
                onResult?.(lastMsg.data || {})
              }
            } else if (data.type === 'error') {
              setMessages((prev) => [...prev, { role: 'assistant', text: `⚠️ ${data.content}` }])
              setLoading(false)
            }
          } catch { /* ignore parse errors */ }
        }

        ws.onclose = () => {
          setWsStatus('fallback')
          wsRef.current = null
        }

        ws.onerror = () => {
          setWsStatus('fallback')
          wsRef.current = null
        }
      } catch {
        setWsStatus('fallback')
      }
    }

    connect()

    return () => {
      if (ws) ws.close()
      if (reconnectTimer) clearTimeout(reconnectTimer)
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const sendMessage = async (text) => {
    const query = text || input
    if (!query.trim() || loading) return

    const userMsg = { role: 'user', text: query }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setLoading(true)
    setShowSuggestions(false)

    // Create placeholder assistant message for streaming
    const streamingId = Date.now() + '_' + Math.random().toString(36).slice(2)
    streamingIdRef.current = streamingId
    setMessages((prev) => [...prev, { role: 'assistant', text: '', _id: streamingId }])

    // Build history
    const history = messages
      .filter((m) => m.role !== 'system')
      .slice(-6)
      .map((m) => ({ role: m.role, text: m.text }))

    // Try WebSocket first
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ query, messages: history }))
      return
    }

    // Fallback to REST
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 20000)

      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, messages: history }),
        signal: controller.signal,
      })
      clearTimeout(timeoutId)

      if (!res.ok) throw new Error(`HTTP ${res.status}`)

      const data = await res.json()

      setMessages((prev) =>
        prev.map((m) =>
          m._id === streamingId
            ? { ...m, text: data.answer || data.summary?.insight?.headline || 'Analysis complete.', data }
            : m
        )
      )
      onResult?.(data)
    } catch (err) {
      const errorText = err.name === 'AbortError'
        ? '⚠️ Request timed out. Please try a simpler question.'
        : '⚠️ Sorry, I had trouble connecting. Please try again.'
      setMessages((prev) =>
        prev.map((m) => (m._id === streamingId ? { ...m, text: errorText } : m))
      )
    } finally {
      setLoading(false)
      streamingIdRef.current = null
      inputRef.current?.focus()
    }
  }

  const clearChat = () => {
    setMessages([
      { role: 'system', text: 'Ask me anything about your organization\'s workforce resilience. I can run simulations, analyze risks, and recommend actions.' },
    ])
    localStorage.removeItem('trupulse_chat')
    setShowSuggestions(true)
    addToast('Conversation cleared')
  }

  const nonSystemMessages = messages.filter((m) => m.role !== 'system')
  const assistantCount = nonSystemMessages.filter((m) => m.role === 'assistant' && m.text).length

  return (
    <div className="bg-white rounded-lg border border-gray-200 flex flex-col h-[500px]">
      <div className="border-b border-gray-200 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div>
            <h3 className="font-semibold text-gray-800 text-sm">AI Assistant</h3>
            <p className="text-xs text-gray-500">Natural language workforce analysis</p>
          </div>
          {wsStatus === 'fallback' && (
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-yellow-100 text-yellow-700 font-medium">REST</span>
          )}
          {wsStatus === 'connected' && (
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-100 text-green-700 font-medium">Live</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {assistantCount > 0 && (
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-500 font-medium">
              {assistantCount}
            </span>
          )}
          <button
            onClick={clearChat}
            className="text-xs text-gray-400 hover:text-gray-600 px-2 py-1 rounded hover:bg-gray-100"
            title="Clear conversation"
          >
            Clear
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {showSuggestions && (
          <div className="space-y-1.5">
            <p className="text-xs text-gray-400 font-medium">Try asking:</p>
            <div className="grid grid-cols-2 gap-1.5">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => sendMessage(s)}
                  className="block text-left text-sm text-tru-600 hover:bg-tru-50 rounded-lg px-3 py-2 transition-colors border border-tru-100 hover:border-tru-300"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}>
            <div
              className={`max-w-[85%] rounded-lg px-4 py-2.5 text-sm ${
                msg.role === 'user'
                  ? 'bg-tru-600 text-white'
                  : msg.role === 'system'
                  ? 'bg-gray-100 text-gray-600 italic'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              <div className="group relative">
                {msg.text || (msg._id ? (
                  <span className="inline-flex gap-1">
                    <span className="w-1.5 h-1.5 bg-tru-400 rounded-full animate-bounce" />
                    <span className="w-1.5 h-1.5 bg-tru-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <span className="w-1.5 h-1.5 bg-tru-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </span>
                ) : null)}
                {msg.text && msg.role === 'assistant' && (
                  <button
                    onClick={() => { copyText(msg.text); addToast('Copied to clipboard') }}
                    className="absolute top-0 right-0 opacity-0 group-hover:opacity-100 transition-opacity text-[10px] px-1.5 py-0.5 rounded bg-white/80 text-gray-400 hover:text-gray-600"
                  >
                    📋
                  </button>
                )}
              </div>
              {msg.data?.summary?.coaching?.actions?.length > 0 ? (
                <div className="mt-2 pt-2 border-t border-gray-200">
                  <p className="text-xs font-medium text-tru-600 mb-1">Recommended Actions:</p>
                  {msg.data.summary.coaching.actions.slice(0, 3).map((a, j) => (
                    <p key={j} className="text-xs text-gray-600">→ {a.title}</p>
                  ))}
                </div>
              ) : msg.data?.actions?.length > 0 ? (
                <div className="mt-2 pt-2 border-t border-gray-200">
                  <p className="text-xs font-medium text-tru-600 mb-1">Recommended Actions:</p>
                  {msg.data.actions.slice(0, 3).map((a, j) => (
                    <p key={j} className="text-xs text-gray-600">→ {a.title || a}</p>
                  ))}
                </div>
              ) : msg.data?.spofs?.length > 0 ? (
                <div className="mt-2 pt-2 border-t border-gray-200">
                  <p className="text-xs font-medium text-tru-600 mb-1">Top SPOFs:</p>
                  {msg.data.spofs.slice(0, 3).map((s, j) => (
                    <p key={j} className="text-xs text-gray-600">→ {s.employee} ({s.team})</p>
                  ))}
                </div>
              ) : msg.data?.scenario ? (
                <div className="mt-2 pt-2 border-t border-gray-200">
                  <p className="text-xs font-medium text-amber-600 mb-1">
                    Scenario Impact: {msg.data.scenario.composite_score}/100
                  </p>
                  <p className="text-xs text-gray-500">
                    Revenue at risk: ${(msg.data.scenario.revenue_at_risk_usd || 0).toLocaleString()}
                  </p>
                </div>
              ) : null}
            </div>
          </div>
        ))}

        {loading && !streamingIdRef.current && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-3">
              <div className="flex gap-1.5">
                <div className="w-2 h-2 bg-tru-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-tru-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-tru-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div className="border-t border-gray-200 p-3">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask about your workforce..."
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-tru-500"
            disabled={loading}
          />
          <button
            onClick={() => sendMessage()}
            disabled={loading || !input.trim()}
            className="bg-tru-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-tru-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? '...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  )
}