import { useState } from 'react'

function Section({ title, children, defaultOpen = false, color = 'tru' }) {
  const [open, setOpen] = useState(defaultOpen)
  const colors = { tru: 'border-tru-200', amber: 'border-amber-200', red: 'border-red-200' }
  return (
    <div className={`border rounded-lg ${colors[color] || colors.tru}`}>
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-3 text-left"
      >
        <span className="font-medium text-sm text-gray-700">{title}</span>
        <span className="text-gray-400">{open ? '−' : '+'}</span>
      </button>
      {open && <div className="px-4 pb-3 text-sm text-gray-600 space-y-1">{children}</div>}
    </div>
  )
}

function ConfidenceGauge({ score }) {
  const color = score >= 80 ? '#16a34a' : score >= 60 ? '#d97706' : '#dc2626'
  return (
    <div className="flex items-center gap-3">
      <svg width="48" height="48" viewBox="0 0 36 36">
        <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          fill="none" stroke="#e5e7eb" strokeWidth="4" />
        <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          fill="none" stroke={color} strokeWidth="4" strokeDasharray={`${(score / 100) * 100} 100`} />
        <text x="18" y="20.5" textAnchor="middle" fontSize="8" fontWeight="bold" fill={color}>
          {score}%
        </text>
      </svg>
      <div>
        <p className="text-sm font-semibold text-gray-800">Confidence Score</p>
        <p className="text-xs text-gray-500">{score >= 80 ? 'High confidence' : score >= 60 ? 'Medium confidence' : 'Low confidence — human review recommended'}</p>
      </div>
    </div>
  )
}

export default function GovernancePanel({ governance }) {
  const [showAll, setShowAll] = useState(false)

  if (!governance) return null

  const displayReasoning = governance.reasoning_trace?.slice(0, showAll ? undefined : 3)
  const displayBias = governance.bias_check?.slice(0, showAll ? undefined : 2)

  return (
    <div className="bg-white rounded-lg border-2 border-amber-200 overflow-hidden">
      <div className="bg-amber-50 px-5 py-3 border-b border-amber-200">
        <div className="flex items-center gap-2">
          <span className="text-lg">🛡️</span>
          <div>
            <h3 className="font-semibold text-amber-900">Governance Agent</h3>
            <p className="text-xs text-amber-700">Responsible AI validation — every output is reviewed for confidence, bias, and transparency</p>
          </div>
        </div>
      </div>

      <div className="p-4 space-y-3">
        <ConfidenceGauge score={governance.confidence_score || 0} />

        {governance.confidence_rationale && (
          <div className="bg-blue-50 border border-blue-100 rounded-lg p-3 text-sm text-blue-800">
            {governance.confidence_rationale}
          </div>
        )}

        <Section title="🧠 Reasoning Trace" defaultOpen color="tru">
          <ol className="list-decimal list-inside space-y-1">
            {displayReasoning?.map((step, i) => (
              <li key={i} className="text-gray-700">{step}</li>
            ))}
          </ol>
          {governance.reasoning_trace?.length > 3 && (
            <button onClick={() => setShowAll(!showAll)} className="text-tru-600 text-xs mt-1 hover:underline">
              {showAll ? 'Show less' : `Show all ${governance.reasoning_trace.length} steps`}
            </button>
          )}
        </Section>

        <Section title="⚠️ Bias Check" color="amber">
          {displayBias?.map((bias, i) => (
            <div key={i} className="flex gap-2 py-1">
              <span className="text-amber-500 mt-0.5">!</span>
              <span>{bias}</span>
            </div>
          ))}
          {governance.bias_check?.length > 2 && (
            <button onClick={() => setShowAll(!showAll)} className="text-tru-600 text-xs mt-1 hover:underline">
              {showAll ? 'Show less' : `Show all ${governance.bias_check.length} items`}
            </button>
          )}
        </Section>

        {governance.counter_argument && (
          <Section title="⚖️ Counter-Argument" color="red" defaultOpen>
            <div className="flex gap-2">
              <span className="text-red-500 font-bold">?</span>
              <p className="text-gray-700">{governance.counter_argument}</p>
            </div>
          </Section>
        )}

        {governance.human_review_required && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start gap-2">
            <span className="text-lg">👤</span>
            <div>
              <p className="text-sm font-medium text-red-800">Human Review Required</p>
              <p className="text-xs text-red-600">{governance.human_review_reason || 'This recommendation requires human approval before action.'}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
