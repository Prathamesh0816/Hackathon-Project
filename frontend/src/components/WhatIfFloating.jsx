import { useState, useEffect } from 'react'
import { postWhatIf, getEmployees } from '../services/api'
import TimeMachine from './TimeMachine'

const SCENARIOS = [
  { value: 'attrition', label: 'Attrition' },
  { value: 'workload_increase', label: 'Workload' },
  { value: 'team_restructuring', label: 'Restructure' },
]

export default function WhatIfFloating() {
  const [open, setOpen] = useState(false)
  const [allEmployees, setAllEmployees] = useState([])
  const [allTeams, setAllTeams] = useState([])
  const [scenarioType, setScenarioType] = useState('attrition')
  const [removedEmployees, setRemovedEmployees] = useState([])
  const [workloadPct, setWorkloadPct] = useState(20)
  const [restructureTeam, setRestructureTeam] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [loadError, setLoadError] = useState(null)

  useEffect(() => {
    if (!open) return
    getEmployees().then((data) => {
      const emps = data.employees || []
      setAllEmployees(emps)
      const names = emps.map((e) => e.name || e.Employee).filter(Boolean)
      if (names.length > 0 && removedEmployees.length === 0) setRemovedEmployees([names[0]])
      const teams = [...new Set(emps.map((e) => e.team))].filter(Boolean).sort()
      setAllTeams(teams)
      if (teams.length > 0 && !restructureTeam) setRestructureTeam(teams[0])
    }).catch((e) => setLoadError(e.message))
  }, [open])

  const runSimulation = async () => {
    setLoading(true)
    setError(null)
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
    }
    setLoading(false)
  }

  const toggleEmployee = (name) => {
    setRemovedEmployees((prev) =>
      prev.includes(name) ? prev.filter((e) => e !== name) : [...prev, name]
    )
  }

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-tru-600 text-white rounded-full shadow-lg hover:bg-tru-700 transition-all z-50 flex items-center justify-center text-2xl"
        title="Run What-If Simulation"
      >
        ⚡
      </button>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30" onClick={() => setOpen(false)}>
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg max-h-[85vh] overflow-y-auto m-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between p-5 border-b border-gray-200">
              <div>
                <h2 className="text-lg font-bold text-gray-900">Quick Simulation</h2>
                <p className="text-sm text-gray-500">Simulate from any page</p>
              </div>
              <button onClick={() => setOpen(false)} className="text-gray-400 hover:text-gray-600 text-xl">&times;</button>
            </div>

            <div className="p-5 space-y-4">
              {loadError && (
                <div className="text-xs text-red-600 bg-red-50 p-2 rounded text-center">
                  Failed to load employee data — {loadError}
                </div>
              )}
              <div className="grid grid-cols-3 gap-2">
                {SCENARIOS.map((s) => (
                  <button
                    key={s.value}
                    onClick={() => setScenarioType(s.value)}
                    className={`p-2 rounded-lg border text-xs font-medium transition-colors ${
                      scenarioType === s.value
                        ? 'border-tru-500 bg-tru-50 text-tru-700'
                        : 'border-gray-200 text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    {s.label}
                  </button>
                ))}
              </div>

              {scenarioType === 'attrition' && (
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-2">
                    Employees ({removedEmployees.length} selected)
                  </label>
                  <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto">
                    {allEmployees.map((e) => (e.name || e.Employee)).filter(Boolean).map((name) => (
                      <button
                        key={name}
                        onClick={() => toggleEmployee(name)}
                        className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
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
                  <label className="block text-xs font-medium text-gray-700 mb-2">
                    Workload Increase: {workloadPct}%
                  </label>
                  <input type="range" min="10" max="100" value={workloadPct} onChange={(e) => setWorkloadPct(Number(e.target.value))} className="w-full" />
                </div>
              )}

              {scenarioType === 'team_restructuring' && (
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-2">Target Team</label>
                  <select value={restructureTeam} onChange={(e) => setRestructureTeam(e.target.value)} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
                    {allTeams.map((t) => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
              )}

              <button
                onClick={runSimulation}
                disabled={loading}
                className="w-full py-2.5 bg-tru-600 text-white rounded-lg font-medium hover:bg-tru-700 disabled:opacity-50 text-sm"
              >
                {loading ? 'Simulating...' : 'Run Simulation'}
              </button>

              {error && <p className="text-red-500 text-xs">{error}</p>}

              {result && (
                <div className="border-t border-gray-200 pt-4">
                  <TimeMachine
                    baseline={result.baseline}
                    projected={result.projected}
                    onShare={() => {
                      navigator.clipboard?.writeText(
                        `TruPulse AI — Composite: ${result.baseline.composite_score} → ${result.projected.composite_score} (Δ${result.comparison?.composite_delta}). Revenue at risk: $${(result.comparison?.revenue_at_risk_usd / 1e6).toFixed(1)}M`
                      )
                    }}
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  )
}
