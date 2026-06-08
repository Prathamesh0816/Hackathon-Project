import { useState, useEffect } from 'react'
import { getWorkforceReadiness } from '../services/api'
import { SkeletonPage } from '../components/Skeleton'
import ErrorState from '../components/ErrorState'
import KPICard from '../components/KPICard'
import StatusBadge from '../components/StatusBadge'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

export default function WorkforceReadiness() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getWorkforceReadiness()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <SkeletonPage />
  if (error) return <ErrorState message={error} />
  if (!data) return <ErrorState message="No readiness data" />

  const chartData = data.team_readiness.map((t) => ({
    name: t.team,
    readiness: t.readiness_score,
    projects: t.active_projects,
  }))

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Workforce Readiness</h1>
        <p className="text-gray-500 mt-1">Capacity to meet upcoming project demands</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <KPICard label="Org Readiness" value={data.readiness_score} subtitle={data.readiness_level} risk={data.readiness_level} />
        <KPICard label="Teams Analyzed" value={data.team_readiness.length} />
        <KPICard label="Future Skill Demands" value={data.future_skill_demand.length} subtitle="Low-documentation areas needing attention" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Team Readiness Scores</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="readiness" radius={[4, 4, 0, 0]}>
                {chartData.map((entry, i) => (
                  <Cell key={i} fill={entry.readiness >= 70 ? '#16a34a' : entry.readiness >= 45 ? '#d97706' : '#dc2626'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Readiness Details</h2>
          <div className="space-y-3 max-h-[350px] overflow-y-auto">
            {data.team_readiness.map((team, i) => (
              <div key={i} className="border border-gray-100 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-800">{team.team}</p>
                    <p className="text-xs text-gray-500">
                      {team.member_count} members · {team.active_projects} active projects · {team.advanced_experts} experts
                    </p>
                  </div>
                  <StatusBadge level={team.readiness_score >= 70 ? 'LOW' : team.readiness_score >= 45 ? 'MEDIUM' : 'HIGH'} small />
                </div>
                <div className="mt-2 bg-gray-100 rounded-full h-1.5">
                  <div
                    className="h-1.5 rounded-full bg-tru-500"
                    style={{ width: `${team.readiness_score}%` }}
                  />
                </div>
                <div className="mt-2 flex flex-wrap gap-1">
                  {team.projects.slice(0, 3).map((p, j) => (
                    <span key={j} className={`text-xs px-2 py-0.5 rounded-full ${
                      p.criticality === 'High' ? 'bg-red-50 text-red-700' : 'bg-gray-100 text-gray-600'
                    }`}>
                      {p.project} ({p.deadline_days}d)
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {data.future_skill_demand?.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">Future Skill Demand (Low Documentation Areas)</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-gray-600">
                <tr>
                  <th className="text-left px-4 py-2 font-medium">Team</th>
                  <th className="text-left px-4 py-2 font-medium">Knowledge Area</th>
                  <th className="text-left px-4 py-2 font-medium">Holder</th>
                  <th className="text-left px-4 py-2 font-medium">Proficiency</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {data.future_skill_demand.map((item, i) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="px-4 py-2 text-gray-700">{item.team}</td>
                    <td className="px-4 py-2 text-gray-700">{item.knowledge_area}</td>
                    <td className="px-4 py-2 text-gray-700">{item.employee}</td>
                    <td className="px-4 py-2">
                      <StatusBadge level={item.current_proficiency} small />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
