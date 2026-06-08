import { useState, useEffect, useCallback } from 'react'
import { useToast } from '../context/ToastContext'
import {
  getAnalyticsWeights,
  getOrgHealth,
  postAnalyticsWeights,
  postAnalyticsWeightsReset,
  postAnalyticsWeightsAiGenerate,
} from '../services/api'

const SLIDER_STYLE = 'w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-tru-600'

function WeightSlider({ label, value, onChange, min = 0, max = 1, step = 0.05 }) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-gray-600 w-32 shrink-0">{label}</span>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className={SLIDER_STYLE}
      />
      <span className="text-xs font-mono text-gray-800 w-10 text-right">{value.toFixed(2)}</span>
    </div>
  )
}

function WeightGroup({ title, weights, onChange }) {
  const normalized = { ...weights }
  return (
    <div className="bg-gray-50 rounded-lg p-3 space-y-2">
      <h4 className="text-sm font-medium text-gray-700 mb-2">{title}</h4>
      {Object.entries(normalized).map(([key, val]) => (
        <WeightSlider
          key={key}
          label={key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
          value={val}
          onChange={(newVal) => onChange(key, newVal)}
        />
      ))}
    </div>
  )
}

export default function AnalyticsWeightsConfig({ onDataChanged }) {
  const { addToast } = useToast()
  const [weights, setWeights] = useState(null)
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [activeTab, setActiveTab] = useState('indicator')

  const fetchData = useCallback(async () => {
    try {
      setLoading(true)
      const [w, h] = await Promise.all([
        getAnalyticsWeights(),
        getOrgHealth(),
      ])
      setWeights(w)
      setHealth(h)
    } catch {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const computePreviewScore = (iw) => {
    if (!health) return null
    const r = health.indicators.resilience.score
    const t = health.indicators.trust.score
    const b = health.indicators.burnout.score
    const rt = health.indicators.retention.score
    const w = iw || weights?.indicator_weights
    if (!w) return null
    const total = Object.values(w).reduce((a, b) => a + b, 0)
    if (total === 0) return 0
    const score = (w.resilience * r + w.trust * t + w.burnout * (100 - b) + w.retention * rt) / total
    return Math.round(Math.min(Math.max(score, 0), 100) * 10) / 10
  }

  const handleIndicatorChange = (key, value) => {
    if (!weights) return
    const newWeights = { ...weights, indicator_weights: { ...weights.indicator_weights, [key]: value } }
    const iw = newWeights.indicator_weights
    const total = Object.values(iw).reduce((a, b) => a + b, 0)
    if (total > 0) {
      Object.keys(iw).forEach((k) => {
        if (k !== key) {
          iw[k] = parseFloat((iw[k] / (total - value + (total - value === 0 ? 1 : 0)) * (1 - value)).toFixed(2))
        }
      })
      iw[key] = value
    }
    setWeights(newWeights)
  }

  const handleSubChange = (group, key, value) => {
    if (!weights) return
    const newWeights = { ...weights, [group]: { ...weights[group], [key]: value } }
    setWeights(newWeights)
  }

  const handleSave = async () => {
    if (!weights) return
    try {
      setSaving(true)
      const body = {
        indicator_weights: weights.indicator_weights,
        burnout_sub_weights: weights.burnout_sub_weights,
        retention_sub_weights: weights.retention_sub_weights,
        resilience_sub_weights: weights.resilience_sub_weights,
        source: 'user',
      }
      const result = await postAnalyticsWeights(body)
      addToast(`Weights saved (source: ${result.weights.source})`)
      setWeights(result.weights)
      const h = await getOrgHealth()
      setHealth(h)
      onDataChanged?.()
    } catch {
      addToast('Failed to save weights', 'error')
    } finally {
      setSaving(false)
    }
  }

  const handleReset = async () => {
    try {
      setSaving(true)
      const result = await postAnalyticsWeightsReset()
      addToast('Reset to default weights')
      setWeights(result.weights)
      const h = await getOrgHealth()
      setHealth(h)
      onDataChanged?.()
    } catch {
      addToast('Failed to reset weights', 'error')
    } finally {
      setSaving(false)
    }
  }

  const handleAiGenerate = async () => {
    try {
      setSaving(true)
      addToast('AI is analyzing org data...', 'info')
      const result = await postAnalyticsWeightsAiGenerate()
      if (result.status === 'ok') {
        addToast(`AI weights applied`)
        setWeights(result.weights)
        const h = await getOrgHealth()
        setHealth(h)
        onDataChanged?.()
      } else {
        addToast('AI generation failed, using defaults', 'warning')
      }
    } catch {
      addToast('AI generation failed', 'error')
    } finally {
      setSaving(false)
    }
  }

  const previewScore = computePreviewScore()

  if (loading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-gray-200 rounded w-1/3" />
          <div className="h-8 bg-gray-200 rounded" />
          <div className="h-8 bg-gray-200 rounded" />
        </div>
      </div>
    )
  }

  if (!weights) return null

  const sourceLabel = weights.source === 'default' ? 'System Defaults' : weights.source === 'user' ? 'Your Custom Values' : 'AI-Generated'

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-semibold text-gray-800 text-sm">Analytics Weights</h3>
          <p className="text-xs text-gray-500">Source: {sourceLabel}</p>
        </div>
        <div className="flex gap-2">
          {saving && (
            <span className="text-xs text-purple-600 animate-pulse flex items-center gap-1">
              <span className="w-1.5 h-1.5 bg-purple-400 rounded-full animate-bounce" />
              Processing...
            </span>
          )}
          <button
            onClick={handleAiGenerate}
            disabled={saving}
            className="text-xs px-3 py-1.5 rounded bg-purple-100 text-purple-700 hover:bg-purple-200 disabled:opacity-50"
          >
            AI Suggest
          </button>
          <button
            onClick={handleReset}
            disabled={saving}
            className="text-xs px-3 py-1.5 rounded bg-gray-100 text-gray-600 hover:bg-gray-200 disabled:opacity-50"
          >
            Reset
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="text-xs px-3 py-1.5 rounded bg-tru-600 text-white hover:bg-tru-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Apply'}
          </button>
        </div>
      </div>

      {previewScore !== null && (
        <div className={`mb-3 px-3 py-2 rounded text-xs font-medium text-center ${
          previewScore >= 70 ? 'bg-green-50 text-green-700' :
          previewScore >= 50 ? 'bg-amber-50 text-amber-700' :
          'bg-red-50 text-red-700'
        }`}>
          Preview Composite: {previewScore}/100
          {health && previewScore !== Math.round(health.composite_score * 10) / 10 && (
            <span className="ml-1 opacity-75">
              ({previewScore > health.composite_score ? '▲' : '▼'} {(Math.abs(previewScore - health.composite_score)).toFixed(1)})
            </span>
          )}
        </div>
      )}

      <div className="flex gap-1 mb-3 border-b border-gray-200">
        {[
          { id: 'indicator', label: 'Indicators' },
          { id: 'burnout', label: 'Burnout' },
          { id: 'retention', label: 'Retention' },
          { id: 'resilience', label: 'Resilience' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`text-xs px-3 py-1.5 border-b-2 -mb-px transition-colors ${
              activeTab === tab.id ? 'border-tru-600 text-tru-600 font-medium' : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'indicator' && weights.indicator_weights && (
        <WeightGroup
          title="Composite Indicator Weights (must sum to 1.0)"
          weights={weights.indicator_weights}
          onChange={(k, v) => handleIndicatorChange(k, v)}
        />
      )}
      {activeTab === 'burnout' && weights.burnout_sub_weights && (
        <WeightGroup
          title="Burnout Sub-Weights"
          weights={weights.burnout_sub_weights}
          onChange={(k, v) => handleSubChange('burnout_sub_weights', k, v)}
        />
      )}
      {activeTab === 'retention' && weights.retention_sub_weights && (
        <WeightGroup
          title="Retention Sub-Weights"
          weights={weights.retention_sub_weights}
          onChange={(k, v) => handleSubChange('retention_sub_weights', k, v)}
        />
      )}
      {activeTab === 'resilience' && weights.resilience_sub_weights && (
        <WeightGroup
          title="Resilience Sub-Weights"
          weights={weights.resilience_sub_weights}
          onChange={(k, v) => handleSubChange('resilience_sub_weights', k, v)}
        />
      )}
    </div>
  )
}