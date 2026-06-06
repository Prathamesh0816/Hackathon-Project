import { useState, useEffect } from 'react'
import { getKnowledgeConcentration } from '../services/api'
import Loading from '../components/Loading'
import ErrorState from '../components/ErrorState'
import KPICard from '../components/KPICard'
import StatusBadge from '../components/StatusBadge'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

export default function KnowledgeConcentration() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getKnowledgeConcentration()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Loading />
  if (error) return <ErrorState message={error} />
  if (!data) return <ErrorState message="No knowledge concentration data" />

  const chartData = data.concentrated_areas.slice(0, 10).map((a) => ({
    name: a.knowledge_area.length > 20 ? a.knowledge_area.slice(0, 18) + '...' : a.knowledge_area,
    risk: a.risk_score,
    holders: a.holder_count,
  }))

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Knowledge Concentration Risk</h1>
        <p className="text-gray-500 mt-1">Knowledge areas held by too few people</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <KPICard label="Total Knowledge Areas" value={data.total_areas} />
        <KPICard label="Critical/High Risk" value={data.critical_areas} risk={data.critical_areas > 5 ? 'CRITICAL' : 'HIGH'} />
        <KPICard label="Org Exposure" value={`${data.org_exposure_pct}%`} subtitle="Areas at critical or high risk" risk={data.org_exposure_pct > 30 ? 'HIGH' : data.org_exposure_pct > 15 ? 'MEDIUM' : 'LOW'} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Top 10 Riskiest Areas</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData} layout="vertical">
              <XAxis type="number" domain={[0, 100]} />
              <YAxis type="category" dataKey="name" width={140} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="risk" radius={[0, 4, 4, 0]}>
                {chartData.map((entry, i) => (
                  <Cell key={i} fill={entry.risk >= 70 ? '#dc2626' : entry.risk >= 50 ? '#d97706' : '#2563eb'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Knowledge Area Details</h2>
          <div className="space-y-3 max-h-[350px] overflow-y-auto">
            {data.concentrated_areas.map((area, i) => (
              <div key={i} className="border border-gray-100 rounded-lg p-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-800">{area.knowledge_area}</p>
                    <p className="text-xs text-gray-500 mt-0.5">
                      {area.holder_count} holder{(area.holder_count) !== 1 ? 's' : ''}
                      {area.low_documentation_count > 0 && ` · ${area.low_documentation_count} low-doc`}
                    </p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {area.holders.slice(0, 3).map((h) => (
                        <span key={h} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">{h}</span>
                      ))}
                      {area.holders.length > 3 && (
                        <span className="text-xs text-gray-400">+{area.holders.length - 3} more</span>
                      )}
                    </div>
                  </div>
                  <StatusBadge level={area.risk_level} small />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
