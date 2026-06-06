import { useState, useEffect, useRef, useCallback } from 'react'

export default function StressTest({ spofs, onComplete }) {
  const [phase, setPhase] = useState('idle')
  const [currentIndex, setCurrentIndex] = useState(-1)
  const [score, setScore] = useState(100)
  const [fallen, setFallen] = useState([])
  const timerRef = useRef(null)

  const startTest = useCallback(() => {
    if (!spofs?.length) return
    setPhase('running')
    setCurrentIndex(0)
    setScore(100)
    setFallen([])
  }, [spofs])

  useEffect(() => {
    if (phase !== 'running' || currentIndex < 0 || currentIndex >= spofs.length) {
      if (phase === 'running' && currentIndex >= spofs.length) {
        setPhase('done')
        onComplete?.({ finalScore: score, totalFallen: spofs.length })
      }
      return
    }

    timerRef.current = setTimeout(() => {
      const spof = spofs[currentIndex]
      const severity = spof.severity_score || 50
      const penalty = Math.round(severity / spofs.length * 3 + 5)

      setFallen((prev) => [...prev, spof.employee])
      setScore((prev) => {
        const next = Math.max(0, prev - penalty)
        return next
      })
      setCurrentIndex((prev) => prev + 1)
    }, 1200)

    return () => clearTimeout(timerRef.current)
  }, [phase, currentIndex, spofs, score, onComplete])

  const reset = useCallback(() => {
    clearTimeout(timerRef.current)
    setPhase('idle')
    setCurrentIndex(-1)
    setScore(100)
    setFallen([])
  }, [])

  const getBarColor = (s) => {
    if (s >= 70) return 'bg-green-500'
    if (s >= 45) return 'bg-amber-500'
    return 'bg-red-500'
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-800">Resilience Stress Test</h2>
        {phase === 'idle' && (
          <button
            onClick={startTest}
            disabled={!spofs?.length}
            className="bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-700 disabled:opacity-50"
          >
            🚨 Run Stress Test
          </button>
        )}
        {phase === 'done' && (
          <button
            onClick={reset}
            className="bg-gray-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-700"
          >
            Reset
          </button>
        )}
      </div>

      {/* Score Gauge */}
      <div className="flex items-center gap-4">
        <div className="relative w-24 h-24">
          <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
            <circle cx="50" cy="50" r="42" fill="none" stroke="#e5e7eb" strokeWidth="8" />
            <circle
              cx="50" cy="50" r="42"
              fill="none"
              stroke={score >= 70 ? '#16a34a' : score >= 45 ? '#d97706' : '#dc2626'}
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={`${(score / 100) * 264} 264`}
              className="transition-all duration-500"
            />
            <text x="50" y="50" textAnchor="middle" dy="5" fontSize="22" fontWeight="bold" fill="#1e293b">
              {score}
            </text>
          </svg>
        </div>
        <div className="flex-1 space-y-1">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Resilience Score</span>
            <span className="font-bold text-gray-800">{score}/100</span>
          </div>
          <div className="w-full bg-gray-100 rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all duration-500 ${getBarColor(score)}`}
              style={{ width: `${score}%` }}
            />
          </div>
          <p className="text-xs text-gray-500">
            {phase === 'idle' && `Ready to test ${spofs?.length || 0} single points of failure`}
            {phase === 'running' && `Failing: ${fallen[fallen.length - 1]} (${fallen.length}/${spofs.length})`}
            {phase === 'done' && `${spofs.length} SPOFs failed. Final resilience: ${score}/100`}
          </p>
        </div>
      </div>

      {/* SPOF domino track */}
      {phase !== 'idle' && (
        <div className="space-y-1 max-h-48 overflow-y-auto">
          {spofs.map((s, i) => {
            const isFallen = i < currentIndex
            const isCurrent = i === currentIndex
            return (
              <div
                key={s.employee}
                className={`flex items-center justify-between px-3 py-1.5 rounded-lg text-sm transition-all duration-300 ${
                  isFallen
                    ? 'bg-red-50 text-red-700 line-through opacity-60'
                    : isCurrent
                    ? 'bg-amber-50 text-amber-700 border border-amber-300 animate-pulse'
                    : 'bg-gray-50 text-gray-500'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span>{isFallen ? '✕' : isCurrent ? '⚡' : '○'}</span>
                  <span className="font-medium">{s.employee}</span>
                  <span className="text-xs opacity-60">{s.role}</span>
                </div>
                <span className={`text-xs font-medium ${isFallen ? 'text-red-600' : 'text-gray-400'}`}>
                  {s.severity_level || s.criticality} · ${(s.revenue_at_risk_usd || 0) / 1000}k at risk
                </span>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
