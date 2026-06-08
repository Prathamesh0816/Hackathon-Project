import { useState, useRef, useEffect } from 'react'

const SUGGESTIONS = [
  'What happens if our top 3 engineers leave?',
  'Who are our biggest single points of failure?',
  'Which team has the most skill gaps?',
  'Simulate a 30% workload increase across all teams',
  'What is our overall organizational health?',
  'Who should we cross-train first?',
]

export default function ChatPanel({ onResult }) {
  const [messages, setMessages] = useState([
    { role: 'system', text: 'Ask me anything about your organization\'s workforce resilience. I can run simulations, analyze risks, and recommend actions.' },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [showSuggestions, setShowSuggestions] = useState(true)
  const endRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (text) => {
    const query = text || input
    if (!query.trim() || loading) return

    setMessages((prev) => [...prev, { role: 'user', text: query }])
    setInput('')
    setLoading(true)
    setShowSuggestions(false)

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, messages }),
      })
      const data = await res.json()

      setMessages((prev) => [...prev, {
        role: 'assistant',
        text: data.answer || data.summary?.insight?.headline || 'Analysis complete. Check the dashboard for details.',
        data: data,
      }])

      onResult?.(data)
    } catch {
      setMessages((prev) => [...prev, {
        role: 'assistant',
        text: '⚠️ Sorry, I had trouble connecting to the analysis engine. Please try again.',
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 flex flex-col h-[400px]">
      <div className="border-b border-gray-200 px-4 py-3">
        <h3 className="font-semibold text-gray-800 text-sm">AI Assistant</h3>
        <p className="text-xs text-gray-500">Natural language workforce analysis</p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {showSuggestions && (
          <div className="space-y-1.5">
            <p className="text-xs text-gray-400 font-medium">Try asking:</p>
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => sendMessage(s)}
                className="block w-full text-left text-sm text-tru-600 hover:bg-tru-50 rounded-lg px-3 py-2 transition-colors"
              >
                {s}
              </button>
            ))}
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[85%] rounded-lg px-4 py-2.5 text-sm ${
                msg.role === 'user'
                  ? 'bg-tru-600 text-white'
                  : msg.role === 'system'
                  ? 'bg-gray-100 text-gray-600 italic'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {msg.text}
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
              ) : null}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-3">
              <div className="flex gap-1.5">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div className="border-t border-gray-200 p-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Ask about your workforce..."
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-tru-500"
          />
          <button
            onClick={() => sendMessage()}
            disabled={loading || !input.trim()}
            className="bg-tru-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-tru-700 disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}
