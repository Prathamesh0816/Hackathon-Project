import { useState, useEffect } from 'react'
import { postWhatIf, postPipeline, getEmployees } from '../services/api'
import Loading from '../components/Loading'
import KPICard from '../components/KPICard'
import StatusBadge from '../components/StatusBadge'
import TimeMachine from '../components/TimeMachine'
import GovernancePanel from '../components/GovernancePanel'
import FeedbackModal from '../components/FeedbackModal'
import TextInput from '../components/TextInput'
import FeedbackPanel from '../components/FeedbackPanel'

const SCENARIOS = [
  { value: 'attrition', label: 'Attrition (Employee Departure)' },
  { value: 'workload_increase', label: 'Workload Increase' },
  { value: 'team_restructuring', label: 'Team Restructuring' },
  { value: 'baseline', label: 'Baseline (Current State)' },
]

export default function WhatIf() {
  const [allEmployees, setAllEmployees] = useState([])
  const [allTeams, setAllTeams] = useState([])
  const [scenarioType, setScenarioType] = useState('attrition')
  const [removedEmployees, setRemovedEmployees] = useState([])
  const [workloadPct, setWorkloadPct] = useState(20)
  const [restructureTeam, setRestructureTeam] = useState('')

  useEffect(() => {
    getEmployees().then((data) => {
      const emps = data.employees || []
      setAllEmployees(emps)
      const names = emps.map((e) => e.name || e.Employee).filter(Boolean)
      if (names.length > 0) setRemovedEmployees([names[0]])
      const teams = [...new Set(emps.map((e) => e.team))].filter(Boolean).sort()
      setAllTeams(teams)
      if (teams.length > 0) setRestructureTeam(teams[0])
    }).catch(() => {})
  }, [])

  const saved = JSON.parse(localStorage.getItem('trupulse_whatif') || 'null')
  const [result, setResult] = useState(saved?.result || null)
  const [pipelineResult, setPipelineResult] = useState(saved?.pipelineResult || null)
  const [loading, setLoading] = useState(false)
  const [pipelineLoading, setPipelineLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showPipeline, setShowPipeline] = useState(saved?.showPipeline || false)
  const [feedbackTarget, setFeedbackTarget] = useState(null)

  useEffect(() => {
    if (result || pipelineResult) {
      localStorage.setItem('trupulse_whatif', JSON.stringify({ result, pipelineResult, showPipeline }))
    }
  }, [result, pipelineResult, showPipeline])

  const toggleEmployee = (name) => {
    setRemovedEmployees((prev) =>
      prev.includes(name) ? prev.filter((e) => e !== name) : [...prev, name]
    )
  }

  const runSimulation = async () => {
    setLoading(true)
    setError(null)
    setPipelineResult(null)
    try {
      const res = await postWhatIf({
        scenario_type: scenarioType,
        removed_employees: removedEmployees,
        workload_increase_pct: workloadPct,
        restructure_team: restructureTeam,
      })
      setResult(res)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const runPipeline = async () => {
    setPipelineLoading(true)
    setError(null)
    try {
      const res = await postPipeline({
        scenario_type: scenarioType,
        removed_employees: removedEmployees,
        workload_increase_pct: workloadPct,
        restructure_team: restructureTeam,
        use_fallback: false,
      })
      setPipelineResult(res)
      setShowPipeline(true)
    } catch (e) {
      setError(e.message)
    } finally {
      setPipelineLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">What-If Simulator</h1>
        <p className="text-gray-500 mt-1">Simulate workforce scenarios and predict organizational impact</p>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-5 space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Scenario Type</label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {SCENARIOS.map((s) => (
              <button
                key={s.value}
                onClick={() => setScenarioType(s.value)}
                className={`p-3 rounded-lg border text-sm font-medium transition-colors ${
                  scenarioType === s.value
                    ? 'border-tru-500 bg-tru-50 text-tru-700'
                    : 'border-gray-200 text-gray-600 hover:bg-gray-50'
                }`}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>

        {scenarioType === 'attrition' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Employees to Remove ({removedEmployees.length} selected)
            </label>
            <div className="flex flex-wrap gap-2">
              {allEmployees.map((e) => e.name || e.Employee).filter(Boolean).map((name) => (
                <button
                  key={name}
                  onClick={() => toggleEmployee(name)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    removedEmployees.includes(name)
                      ? 'bg-red-500 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {name}
                </button>
              ))}
            </div>
          </div>
        )}

        {scenarioType === 'workload_increase' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Workload Increase: {workloadPct}%
            </label>
            <input
              type="range"
              min="10"
              max="100"
              value={workloadPct}
              onChange={(e) => setWorkloadPct(Number(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>10%</span>
              <span>100%</span>
            </div>
          </div>
        )}

        {scenarioType === 'team_restructuring' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Team to Restructure</label>
            <select
              value={restructureTeam}
              onChange={(e) => setRestructureTeam(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
            >
              {(allTeams.length > 0 ? allTeams : ['Engineering']).map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">Simulates 20% workforce reduction in the selected team</p>
          </div>
        )}

        <div className="flex gap-3">
          <button
            onClick={runSimulation}
            disabled={loading}
            className="bg-tru-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-tru-700 disabled:opacity-50"
          >
            {loading ? 'Simulating...' : 'Run Simulation'}
          </button>
          <button
            onClick={runPipeline}
            disabled={pipelineLoading || !result}
            className="bg-gray-800 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-gray-900 disabled:opacity-50"
          >
            {pipelineLoading ? 'Running AI Pipeline...' : 'Run AI Pipeline Analysis'}
          </button>
        </div>
      </div>

      <TextInput />

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      {result && (
        <div className="space-y-6">
          <h2 className="text-lg font-semibold text-gray-800">Time Machine: Before vs After</h2>
          <TimeMachine
            baseline={result.baseline}
            projected={result.projected}
            onShare={() => {
              navigator.clipboard?.writeText(
                `TruPulse AI — Composite: ${result.baseline.composite_score} → ${result.projected.composite_score} (Δ${result.comparison.composite_delta}). Revenue at risk: $${(result.comparison.revenue_at_risk_usd / 1e6).toFixed(1)}M`
              )
              alert('Impact summary copied to clipboard!')
            }}
          />
        </div>
      )}

      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <FeedbackPanel />
      </div>

      {pipelineResult && showPipeline && (
        <div className="space-y-6">
          <h2 className="text-lg font-semibold text-gray-800">AI Pipeline Analysis</h2>
          <p className="text-xs text-gray-500 -mt-4">Completed in {pipelineResult.elapsed_seconds}s · 5 agents · Full trace below</p>

          {pipelineResult.summary && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="bg-white rounded-lg border border-gray-200 p-5">
                  <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
                    <span className="w-6 h-6 bg-tru-100 text-tru-700 rounded-full flex items-center justify-center text-xs font-bold">1</span>
                    Insight Agent
                  </h3>
                  <p className="text-sm text-gray-700">{pipelineResult.summary.insight?.headline}</p>
                  {pipelineResult.summary.insight?.patterns?.map((p, i) => (
                    <div key={i} className="mt-2 flex items-center gap-2 text-sm text-gray-600">
                      <StatusBadge level={p.severity} small />
                      <span>{p.title}: {p.evidence}</span>
                    </div>
                  ))}
                </div>

                <div className="bg-white rounded-lg border border-gray-200 p-5">
                  <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
                    <span className="w-6 h-6 bg-red-100 text-red-700 rounded-full flex items-center justify-center text-xs font-bold">2</span>
                    Risk Agent
                  </h3>
                  <p className="text-sm text-gray-700">{pipelineResult.summary.risk?.headline}</p>
                  {pipelineResult.summary.risk?.critical_spofs?.map((s, i) => (
                    <div key={i} className="mt-2 text-sm text-gray-600">
                      ⚠ {s.employee} ({s.team}) — {s.why}
                    </div>
                  ))}
                </div>

                <div className="bg-white rounded-lg border border-gray-200 p-5">
                  <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
                    <span className="w-6 h-6 bg-amber-100 text-amber-700 rounded-full flex items-center justify-center text-xs font-bold">3</span>
                    Simulation Agent
                  </h3>
                  <p className="text-sm text-gray-700">{pipelineResult.summary.simulation?.headline}</p>
                  <p className="text-xs text-gray-500 mt-1">{pipelineResult.summary.simulation?.narrative}</p>
                </div>

                <div className="bg-white rounded-lg border border-gray-200 p-5">
                  <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
                    <span className="w-6 h-6 bg-green-100 text-green-700 rounded-full flex items-center justify-center text-xs font-bold">4</span>
                    Coaching Agent
                  </h3>
                  <p className="text-sm text-gray-700">{pipelineResult.summary.coaching?.headline}</p>
                  <div className="mt-3 space-y-2">
                    {pipelineResult.summary.coaching?.actions?.map((a, i) => (
                      <div key={i} className="border border-gray-200 rounded-lg p-3">
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1">
                            <p className="font-medium text-sm">{a.title}</p>
                            <p className="text-xs text-gray-500 mt-0.5">
                              Owner: {a.owner_role} · {a.deadline_days}d · ${a.estimated_cost_usd?.toLocaleString()}
                            </p>
                            <p className="text-xs text-gray-600 mt-1">{a.rationale}</p>
                          </div>
                          <button
                            onClick={() => setFeedbackTarget({ employee: a.owner_role, action: a.title })}
                            className="text-xs text-tru-600 hover:text-tru-800 whitespace-nowrap mt-1"
                          >
                            Review →
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <GovernancePanel governance={pipelineResult.summary.governance} />

                {pipelineResult.trace && (
                  <div className="bg-white rounded-lg border border-gray-200 p-5">
                    <h3 className="font-semibold text-gray-700 mb-3">Agent Execution Trace</h3>
                    <div className="space-y-2">
                      {pipelineResult.trace.map((t, i) => (
                        <div key={i} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0 text-sm">
                          <div className="flex items-center gap-2">
                            <span className="w-5 h-5 rounded-full bg-gray-100 flex items-center justify-center text-xs font-bold text-gray-600">
                              {t.step}
                            </span>
                            <span className="font-medium text-gray-700">{t.agent}</span>
                          </div>
                          <div className="flex items-center gap-3 text-xs text-gray-400">
                            <span>{t.latency_seconds}s</span>
                            <span className={`w-2 h-2 rounded-full ${t.latency_seconds > 0 ? 'bg-green-500' : 'bg-gray-300'}`} />
                          </div>
                        </div>
                      ))}
                    </div>
                    <p className="text-xs text-gray-400 mt-3">
                      Total: {pipelineResult.total_latency_seconds}s {pipelineResult.fallback_used ? '(fallback mode — Ollama unavailable)' : ''}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {feedbackTarget && (
        <FeedbackModal
          action={feedbackTarget.action}
          employee={feedbackTarget.employee}
          onClose={() => setFeedbackTarget(null)}
          onSubmit={(decision) => {
            console.log(`Feedback submitted: ${decision} on ${feedbackTarget.action}`)
          }}
        />
      )}
    </div>
  )
}
