import { useState, useEffect } from 'react'
import {
  getEmployeeProfile,
  getOrgHealth,
  getSpofRanking,
  getSuccessionPlanning,
} from '../services/api'

const FALLBACK_EVENTS = [
  { icon: '📊', text: 'Loading organizational health...', type: 'alert' },
  { icon: '⚠️', text: 'Loading SPOF ranking...', type: 'alert' },
  { icon: '💰', text: 'Loading revenue risk...', type: 'risk' },
  { icon: '👤', text: 'Loading Vikram profile...', type: 'risk' },
  { icon: '🔥', text: 'Loading burnout signals...', type: 'alert' },
  { icon: '🧠', text: 'Loading knowledge documentation risk...', type: 'alert' },
  { icon: '✅', text: 'Checking AI pipeline status...', type: 'success' },
  { icon: '📋', text: 'Loading succession coverage...', type: 'success' },
]

function formatMoney(value) {
  if (!Number.isFinite(value)) return '$0'
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`
  if (value >= 1_000) return `$${Math.round(value / 1_000)}K`
  return `$${Math.round(value)}`
}

function riskType(risk) {
  return risk === 'LOW' ? 'success' : risk === 'MEDIUM' ? 'risk' : 'alert'
}

function buildEvents({ health, spof, vikram, pipeline, succession }) {
  const trustDetails = health?.indicators?.trust?.details || {}
  const burnoutDetails = health?.indicators?.burnout?.details || {}
  const resilienceDetails = health?.indicators?.resilience?.details || {}
  const topSpofs = spof?.spofs || resilienceDetails.all_spofs || []
  const top3Revenue = topSpofs
    .slice(0, 3)
    .reduce((sum, item) => sum + Number(item.revenue_at_risk_usd || 0), 0)
  const vikramRisk = topSpofs.find((item) => item.employee === 'Vikram')
  const successionPct = Number(succession?.org_readiness || 0)

  return [
    {
      icon: '📊',
      text: `Composite health score: ${health.composite_score}/100 - ${health.overall_risk} risk`,
      type: riskType(health.overall_risk),
    },
    {
      icon: '⚠️',
      text: `${spof.total_spofs} single points of failure detected across ${health.team_count} teams`,
      type: spof.total_spofs > 0 ? 'alert' : 'success',
    },
    {
      icon: '💰',
      text: `${formatMoney(top3Revenue)} annual revenue at risk from top-3 SPOFs`,
      type: top3Revenue > 0 ? 'risk' : 'success',
    },
    {
      icon: '👤',
      text: `${vikram.employee} (${vikram.team}) - ${vikram.backup_available === 'No' ? 'no backup' : 'backup available'}, ${vikram.tenure_years}yr tenure, ${formatMoney(vikramRisk?.revenue_at_risk_usd || 0)} revenue at risk`,
      type: vikram.backup_available === 'No' ? 'risk' : 'success',
    },
    {
      icon: '🔥',
      text: `${burnoutDetails.high_burnout_count || 0} employees flagged for high burnout signals`,
      type: (burnoutDetails.high_burnout_count || 0) > 0 ? 'alert' : 'success',
    },
    {
      icon: '🧠',
      text: `${trustDetails.low_documentation_areas || 0} of ${trustDetails.total_knowledge_areas || 0} knowledge areas at low documentation risk`,
      type: (trustDetails.low_documentation_areas || 0) > 0 ? 'alert' : 'success',
    },
    {
      icon: '✅',
      text: pipeline?.message
        ? `AI pipeline ready - 5 agents operational (${pipeline.pipeline_backend})`
        : 'AI pipeline status unavailable',
      type: pipeline?.message ? 'success' : 'risk',
    },
    {
      icon: '📋',
      text: `Succession coverage: ${successionPct}% of critical roles have ready successors`,
      type: successionPct >= 80 ? 'success' : successionPct >= 50 ? 'risk' : 'alert',
    },
  ]
}

export default function OrgPulseTicker() {
  const [events, setEvents] = useState(FALLBACK_EVENTS)
  const [current, setCurrent] = useState(0)
  const [paused, setPaused] = useState(false)

  useEffect(() => {
    let cancelled = false

    async function loadEvents() {
      try {
        const [health, spof, vikram, pipeline, succession] = await Promise.all([
          getOrgHealth(),
          getSpofRanking(),
          getEmployeeProfile('Vikram'),
          fetch('/api/').then((res) => (res.ok ? res.json() : null)).catch(() => null),
          getSuccessionPlanning(),
        ])

        if (!cancelled) {
          setEvents(buildEvents({ health, spof, vikram, pipeline, succession }))
        }
      } catch (err) {
        console.error('Org pulse ticker failed to load:', err)
        if (!cancelled) {
          setEvents([
            { icon: '⚠️', text: 'Unable to load live org pulse metrics. Check backend connection.', type: 'risk' },
          ])
        }
      }
    }

    loadEvents()
    const refresh = setInterval(loadEvents, 30000)
    return () => {
      cancelled = true
      clearInterval(refresh)
    }
  }, [])

  useEffect(() => {
    setCurrent((prev) => Math.min(prev, events.length - 1))
  }, [events.length])

  useEffect(() => {
    if (paused || events.length <= 1) return
    const timer = setInterval(() => {
      setCurrent((prev) => (prev + 1) % events.length)
    }, 3500)
    return () => clearInterval(timer)
  }, [paused, events.length])

  const event = events[current] || events[0]
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
          {events.map((_, i) => (
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
