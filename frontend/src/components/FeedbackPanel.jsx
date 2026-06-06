import { useState } from 'react'
import { getSuggestions, postApplyDecisions } from '../services/api'
import StatusBadge from './StatusBadge'

export default function FeedbackPanel({ onRecalculated }) {
  const [suggestions, setSuggestions] = useState([])
  const [decisions, setDecisions] = useState({})
  const [customTitle, setCustomTitle] = useState('')
  const [customDesc, setCustomDesc] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [calcLoading, setCalcLoading] = useState(false)
  const [error, setError] = useState(null)

  const loadSuggestions = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await getSuggestions()
      setSuggestions(res.suggestions || [])
      const initial = {}
      ;(res.suggestions || []).forEach((s) => { initial[s.id] = 'pending' })
      setDecisions(initial)
      setResult(null)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const setDecision = (id, decision) => {
    setDecisions((prev) => ({ ...prev, [id]: decision }))
  }

  const addCustom = () => {
    if (!customTitle.trim()) return
    setSuggestions((prev) => [
      ...prev,
      {
        id: `custom_${Date.now()}`,
        title: customTitle,
        description: customDesc || 'Custom action added by user',
        type: 'custom',
        target_employee: '',
        target_team: '',
        estimated_impact: 'User-defined action',
        estimated_cost_usd: 0,
        status: 'pending',
        is_custom: true,
      },
    ])
    setDecisions((prev) => ({ ...prev, [`custom_${Date.now()}`]: 'pending' }))
    setCustomTitle('')
    setCustomDesc('')
  }

  const applyDecisions = async () => {
    setCalcLoading(true)
    setError(null)
    try {
      const accepted = Object.entries(decisions)
        .filter(([, d]) => d === 'accept')
        .map(([id]) => id)
      const rejected = Object.entries(decisions)
        .filter(([, d]) => d === 'reject')
        .map(([id]) => id)
      const modified = Object.entries(decisions)
        .filter(([, d]) => d === 'modify')
        .map(([id]) => {
          const sug = suggestions.find((s) => s.id === id)
          return { ...sug, status: 'modified' }
        })
      const userAdded = suggestions
        .filter((s) => s.is_custom && decisions[s.id] !== 'reject')
        .map((s) => ({ ...s, status: 'accepted' }))

      const res = await postApplyDecisions({
        accepted_ids: accepted,
        rejected_ids: rejected,
        modified,
        user_added: userAdded,
      })
      setResult(res)
      if (onRecalculated) onRecalculated(res)
    } catch (e) {
      setError(e.message)
    } finally {
      setCalcLoading(false)
    }
  }

  const statusColor = (decision) => {
    if (decision === 'accept') return 'bg-green-100 text-green-800 border-green-300'
    if (decision === 'reject') return 'bg-red-100 text-red-800 border-red-300'
    if (decision === 'modify') return 'bg-yellow-100 text-yellow-800 border-yellow-300'
    return 'bg-gray-100 text-gray-600 border-gray-200'
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-900">Human-AI Decision Center</h3>
        <button
          onClick={loadSuggestions}
          disabled={loading}
          className="px-3 py-1.5 bg-tru-600 text-white rounded-lg text-xs font-medium hover:bg-tru-700 disabled:opacity-50 transition-colors"
        >
          {loading ? 'Generating...' : 'Generate AI Suggestions'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-2 text-xs text-red-700">
          {error}
        </div>
      )}

      {suggestions.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs text-gray-500">
            Review each suggestion and decide: Accept, Reject, or Modify.
            Accepted actions will be applied to recalculate the org health score.
          </p>
          {suggestions.map((sug) => (
            <div key={sug.id} className={`border rounded-lg p-3 ${statusColor(decisions[sug.id])}`}>
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-gray-900">{sug.title}</span>
                    <StatusBadge level={sug.type} small />
                    {sug.is_custom && (
                      <span className="bg-purple-100 text-purple-700 text-[10px] px-1.5 py-0.5 rounded-full font-medium">
                        CUSTOM
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-gray-600 mt-1">{sug.description}</p>
                  <div className="flex gap-3 mt-1 text-[10px] text-gray-500">
                    {sug.estimated_impact && <span>Impact: {sug.estimated_impact}</span>}
                    {sug.estimated_cost_usd > 0 && <span>Cost: ${sug.estimated_cost_usd.toLocaleString()}</span>}
                  </div>
                </div>
                <div className="flex gap-1 shrink-0">
                  {['accept', 'reject', 'modify'].map((action) => (
                    <button
                      key={action}
                      onClick={() => setDecision(sug.id, action)}
                      className={`px-2 py-1 rounded text-[10px] font-medium border transition-colors ${
                        decisions[sug.id] === action
                          ? 'ring-2 ring-tru-500'
                          : 'hover:bg-gray-50'
                      }`}
                    >
                      {action === 'accept' ? '✓ Accept' : action === 'reject' ? '✗ Reject' : '✎ Edit'}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
        <p className="text-xs font-medium text-gray-700 mb-2">Add Your Own Suggestion</p>
        <div className="flex gap-2">
          <input
            type="text"
            value={customTitle}
            onChange={(e) => setCustomTitle(e.target.value)}
            placeholder="Action title..."
            className="flex-1 border border-gray-300 rounded px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-tru-500"
          />
          <input
            type="text"
            value={customDesc}
            onChange={(e) => setCustomDesc(e.target.value)}
            placeholder="Description (optional)..."
            className="flex-1 border border-gray-300 rounded px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-tru-500"
          />
          <button
            onClick={addCustom}
            disabled={!customTitle.trim()}
            className="px-3 py-1.5 bg-gray-700 text-white rounded-lg text-xs font-medium hover:bg-gray-800 disabled:opacity-50 transition-colors"
          >
            + Add
          </button>
        </div>
      </div>

      {suggestions.length > 0 && (
        <div className="flex items-center gap-3">
          <button
            onClick={applyDecisions}
            disabled={calcLoading}
            className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50 transition-colors"
          >
            {calcLoading ? 'Recalculating...' : 'Apply Decisions & Recalculate'}
          </button>
          <span className="text-xs text-gray-500">
            {Object.values(decisions).filter((d) => d !== 'pending').length} of {suggestions.length} reviewed
          </span>
        </div>
      )}

      {result && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 space-y-2">
          <h4 className="text-sm font-semibold text-green-800">Recalculation Result</h4>
          <div className="flex gap-4">
            <div className="text-center">
              <div className="text-xs text-gray-600">Before AI</div>
              <div className="text-2xl font-bold text-gray-800">{result.before_score}</div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-600">After Human-AI</div>
              <div className="text-2xl font-bold text-green-600">{result.after_score}</div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-600">Improvement</div>
              <div className="text-2xl font-bold text-blue-600">+{result.delta}</div>
            </div>
          </div>
          <p className="text-xs text-gray-600 mt-2">
            {result.applied_actions.length} action(s) applied. Showing projected composite score after human-AI collaboration.
          </p>
        </div>
      )}
    </div>
  )
}
