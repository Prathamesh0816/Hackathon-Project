import { useState, useEffect } from 'react'

const EVENTS = [
  { icon: '📊', text: 'Composite health score: 27.5/100 — HIGH risk', type: 'alert' },
  { icon: '⚠️', text: '56 single points of failure detected across 14 teams', type: 'alert' },
  { icon: '💰', text: '$5.6M annual revenue at risk from top-3 SPOFs', type: 'risk' },
  { icon: '👤', text: 'Vikram (Sales) — no backup, 8yr tenure, $2.7M revenue at risk', type: 'risk' },
  { icon: '🔥', text: '10 employees flagged for high burnout signals', type: 'alert' },
  { icon: '🧠', text: '211 of 468 knowledge areas at low documentation risk', type: 'alert' },
  { icon: '✅', text: 'AI pipeline ready — 5 agents operational', type: 'success' },
  { icon: '📋', text: 'Succession coverage: 95% of critical roles have ready successors', type: 'success' },
]

export default function OrgPulseTicker() {
  const [current, setCurrent] = useState(0)
  const [paused, setPaused] = useState(false)

  useEffect(() => {
    if (paused) return
    const timer = setInterval(() => {
      setCurrent((prev) => (prev + 1) % EVENTS.length)
    }, 3500)
    return () => clearInterval(timer)
  }, [paused])

  const event = EVENTS[current]
  const bgClass = event.type === 'alert' ? 'bg-amber-50 border-amber-200'
    : event.type === 'risk' ? 'bg-red-50 border-red-200'
    : 'bg-green-50 border-green-200'

  return (
    <div
      className={`border rounded-lg px-4 py-2.5 ${bgClass} transition-colors duration-500 cursor-pointer`}
      onClick={() => setPaused(!paused)}
      title={paused ? 'Resume' : 'Pause'}
    >
      <div className="flex items-center gap-3">
        <span className="text-lg">{event.icon}</span>
        <p className="text-sm text-gray-700 flex-1">{event.text}</p>
        <div className="flex gap-1">
          {EVENTS.map((_, i) => (
            <span
              key={i}
              className={`w-1.5 h-1.5 rounded-full transition-all duration-300 ${
                i === current ? 'bg-tru-500 scale-125' : 'bg-gray-300'
              }`}
            />
          ))}
        </div>
        <span className="text-xs text-gray-400">{paused ? '▶' : '⏸'}</span>
      </div>
    </div>
  )
}
