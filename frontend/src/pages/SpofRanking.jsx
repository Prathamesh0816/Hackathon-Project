import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { getSpofRanking } from '../services/api'
import KPICard from '../components/KPICard'
import StatusBadge from '../components/StatusBadge'
import Loading from '../components/Loading'
import ErrorState from '../components/ErrorState'
import DependencyGraph from '../components/DependencyGraph'
import StressTest from '../components/StressTest'

export default function SpofRanking() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    getSpofRanking()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Loading />
  if (error) return <ErrorState message={error} />
  if (!data) return <ErrorState message="No SPOF data" />

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">SPOF Ranking</h1>
        <p className="text-gray-500 mt-1">Single Points of Failure — employees with no backup</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <KPICard label="Total SPOFs" value={data.total_spofs} risk="HIGH" />
        <KPICard label="Critical SPOFs" value={data.critical_spofs} risk="CRITICAL" />
        <KPICard label="Annual Revenue at Risk" value={`$${(data.total_annual_revenue_at_risk_usd / 1e6).toFixed(1)}M`} risk="HIGH" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h2 className="text-lg font-semibold text-gray-800 mb-3">Dependency Network</h2>
          <DependencyGraph
            employees={data.spofs}
            dependencies={data.spofs.flatMap((s) =>
              Array.from({ length: s.dependents_count }, (_, i) => ({
                owner: s.employee,
                dependent: `Dependent ${i + 1}`,
              }))
            )}
            onNodeClick={(id) => {
              const emp = data.spofs.find((s) => s.employee === id)
              if (emp) {
                const el = document.getElementById(`spof-row-${emp.employee}`)
                el?.scrollIntoView({ behavior: 'smooth', block: 'center' })
                el?.classList.add('ring-2', 'ring-tru-500')
                setTimeout(() => el?.classList.remove('ring-2', 'ring-tru-500'), 2000)
              }
            }}
          />
        </div>
        <div>
          <StressTest spofs={data.spofs} />
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-600">
            <tr>
              <th className="text-left px-4 py-3 font-medium">Employee</th>
              <th className="text-left px-4 py-3 font-medium">Team</th>
              <th className="text-left px-4 py-3 font-medium">Role</th>
              <th className="text-center px-4 py-3 font-medium">Severity</th>
              <th className="text-center px-4 py-3 font-medium">Dependents</th>
              <th className="text-center px-4 py-3 font-medium">Low Doc</th>
              <th className="text-center px-4 py-3 font-medium">Hours/Week</th>
              <th className="text-right px-4 py-3 font-medium">Revenue at Risk</th>
              <th className="text-center px-4 py-3 font-medium">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {data.spofs.map((s, i) => (
              <tr key={i} id={`spof-row-${s.employee}`} className="hover:bg-gray-50 transition-all">
                <td className="px-4 py-3 font-medium text-gray-900">{s.employee}</td>
                <td className="px-4 py-3 text-gray-600">{s.team}</td>
                <td className="px-4 py-3 text-gray-600">{s.role}</td>
                <td className="px-4 py-3 text-center">
                  <StatusBadge level={s.severity_level} small />
                </td>
                <td className="px-4 py-3 text-center text-gray-700">{s.dependents_count}</td>
                <td className="px-4 py-3 text-center text-gray-700">{s.low_doc_areas}</td>
                <td className="px-4 py-3 text-center text-gray-700">{s.weekly_hours}</td>
                <td className="px-4 py-3 text-right text-gray-700">${(s.revenue_at_risk_usd / 1e3).toFixed(0)}K</td>
                <td className="px-4 py-3 text-center">
                  <Link to={`/employee/${s.employee}`} className="text-tru-600 hover:underline text-xs font-medium">
                    Profile
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
