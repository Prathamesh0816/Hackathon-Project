import { useState, useEffect } from 'react'
import { getSkillGaps } from '../services/api'
import { SkeletonPage } from '../components/Skeleton'
import ErrorState from '../components/ErrorState'
import KPICard from '../components/KPICard'
import StatusBadge from '../components/StatusBadge'

export default function SkillGaps() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedTeam, setSelectedTeam] = useState(null)

  useEffect(() => {
    getSkillGaps()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <SkeletonPage />
  if (error) return <ErrorState message={error} />
  if (!data) return <ErrorState message="No skill gap data" />

  const selected = selectedTeam
    ? data.teams.find((t) => t.team === selectedTeam)
    : null

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Skill Gap Analysis</h1>
        <p className="text-gray-500 mt-1">Knowledge areas with insufficient team coverage</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <KPICard label="Teams Analyzed" value={data.teams.length} />
        <KPICard label="Org-Wide Gaps" value={data.total_gap_count} risk={data.total_gap_count > 5 ? 'HIGH' : 'MEDIUM'} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h2 className="font-semibold text-gray-700 mb-3">Teams</h2>
          <div className="space-y-1">
            {data.teams.map((t) => (
              <button
                key={t.team}
                onClick={() => setSelectedTeam(t.team)}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                  selectedTeam === t.team
                    ? 'bg-tru-50 text-tru-700'
                    : 'hover:bg-gray-100 text-gray-600'
                }`}
              >
                <span className="font-medium">{t.team}</span>
                <span className="float-right text-xs opacity-60">{t.coverage_pct}% coverage</span>
              </button>
            ))}
          </div>
        </div>

        <div className="lg:col-span-2">
          {selected ? (
            <div className="bg-white rounded-lg border border-gray-200 p-5 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-800">{selected.team}</h2>
                <StatusBadge level={selected.coverage_pct >= 70 ? 'LOW' : selected.coverage_pct >= 45 ? 'MEDIUM' : 'HIGH'} small />
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="bg-gray-50 rounded p-3 text-center">
                  <p className="text-xl font-bold">{selected.employee_count}</p>
                  <p className="text-xs text-gray-500">Members</p>
                </div>
                <div className="bg-gray-50 rounded p-3 text-center">
                  <p className="text-xl font-bold">{selected.coverage_pct}%</p>
                  <p className="text-xs text-gray-500">Coverage</p>
                </div>
                <div className="bg-gray-50 rounded p-3 text-center">
                  <p className="text-xl font-bold">{selected.total_knowledge_areas}</p>
                  <p className="text-xs text-gray-500">Knowledge Areas</p>
                </div>
              </div>

              {selected.missing_areas?.length > 0 && (
                <div>
                  <h3 className="font-medium text-gray-700 mb-2">Missing Knowledge Areas</h3>
                  <div className="flex flex-wrap gap-2">
                    {selected.missing_areas.map((area) => (
                      <span key={area} className="px-3 py-1 bg-red-50 text-red-700 rounded-full text-xs font-medium">
                        {area}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {selected.critical_missing?.length > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                  <p className="text-sm font-medium text-red-700">Critical Missing Areas:</p>
                  <p className="text-xs text-red-600 mt-1">{selected.critical_missing.join(', ')}</p>
                </div>
              )}

              {selected.single_owner_areas?.length > 0 && (
                <div>
                  <h3 className="font-medium text-gray-700 mb-2">Bus-Factor 1 (Single Owner)</h3>
                  <div className="space-y-1">
                    {selected.single_owner_areas.map((item) => (
                      <div key={item.area} className="flex justify-between text-sm py-1 border-b border-gray-100">
                        <span className="text-gray-700">{item.area}</span>
                        <span className="text-gray-500 text-xs">{item.owner}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-gray-50 rounded-lg border border-gray-200 p-10 text-center">
              <p className="text-gray-500">Select a team to view skill gap details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
