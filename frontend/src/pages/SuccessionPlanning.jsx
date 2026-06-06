import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getSuccessionPlanning } from '../services/api'
import Loading from '../components/Loading'
import ErrorState from '../components/ErrorState'
import KPICard from '../components/KPICard'
import StatusBadge from '../components/StatusBadge'

export default function SuccessionPlanning() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [expanded, setExpanded] = useState(null)

  useEffect(() => {
    getSuccessionPlanning()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Loading />
  if (error) return <ErrorState message={error} />
  if (!data) return <ErrorState message="No succession data" />

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Succession Planning</h1>
        <p className="text-gray-500 mt-1">Backfill readiness for every critical role</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <KPICard label="Org Readiness" value={`${data.org_readiness}%`} subtitle={`${data.roles_covered}/${data.total_high_roles} roles covered`} risk={data.org_readiness >= 70 ? 'LOW' : data.org_readiness >= 45 ? 'MEDIUM' : 'HIGH'} />
        <KPICard label="Critical Roles" value={data.total_high_roles} subtitle="High-criticality positions" />
        <KPICard label="Roles With Successor" value={data.roles_covered} subtitle="At least one ready candidate" risk={data.roles_covered < data.total_high_roles * 0.5 ? 'HIGH' : 'MEDIUM'} />
      </div>

      <div className="space-y-4">
        {data.roles.map((role, i) => (
          <div key={i} className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <button
              onClick={() => setExpanded(expanded === i ? null : i)}
              className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div>
                  <p className="font-medium text-gray-900">{role.role}</p>
                  <p className="text-sm text-gray-500">{role.employee} · {role.team}</p>
                </div>
                {!role.backup_available && <StatusBadge level="CRITICAL" small />}
              </div>
              <div className="flex items-center gap-3">
                <StatusBadge
                  level={role.has_ready_successor ? 'LOW' : 'HIGH'}
                  small
                />
                <span className="text-gray-400 text-lg">{expanded === i ? '−' : '+'}</span>
              </div>
            </button>

            {expanded === i && (
              <div className="border-t border-gray-100 p-4">
                {role.potential_successors?.length > 0 ? (
                  <div className="space-y-3">
                    {role.potential_successors.map((s, j) => (
                      <div key={j} className="flex items-center justify-between border border-gray-100 rounded-lg p-3">
                        <div>
                          <Link to={`/employee/${s.employee}`} className="font-medium text-tru-600 hover:underline text-sm">
                            {s.employee}
                          </Link>
                          <p className="text-xs text-gray-500">{s.role} · {s.experience_years} yrs exp</p>
                          <p className="text-xs text-gray-400">Knowledge overlap: {s.knowledge_overlap} areas</p>
                        </div>
                        <div className="text-right">
                          <p className="text-lg font-bold text-gray-800">{s.readiness_score}</p>
                          <StatusBadge level={s.readiness_level} small />
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No potential successors identified in the same team.</p>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
