import { useState, useEffect } from 'react'
import { getOrgHealth, getSpofRanking, getSkillGaps, getWorkforceReadiness, getDatasetInfo } from '../services/api'
import KPICard from '../components/KPICard'
import GaugeChart from '../components/GaugeChart'
import { SkeletonGrid, SkeletonCard, SkeletonPage } from '../components/Skeleton'
import ErrorState from '../components/ErrorState'
import ChatPanel from '../components/ChatPanel'
import OrgPulseTicker from '../components/OrgPulseTicker'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function Dashboard() {
  const [health, setHealth] = useState(null)
  const [spof, setSpof] = useState(null)
  const [gaps, setGaps] = useState(null)
  const [readiness, setReadiness] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [chatResult, setChatResult] = useState(null)
  const [dataInfo, setDataInfo] = useState(null)

  useEffect(() => {
    Promise.all([
      getOrgHealth(),
      getSpofRanking(),
      getSkillGaps(),
      getWorkforceReadiness(),
      getDatasetInfo().catch(() => null),
    ])
      .then(([h, s, g, r, di]) => {
        setHealth(h)
        setSpof(s)
        setGaps(g)
        setReadiness(r)
        setDataInfo(di)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <SkeletonPage />
  if (error) return <ErrorState message={error} />
  if (!health) return <ErrorState message="No health data returned" />

  const indicators = health.indicators
  const indChartData = [
    { name: 'Resilience', score: indicators.resilience.score },
    { name: 'Trust', score: indicators.trust.score },
    { name: 'Burnout', score: indicators.burnout.score },
    { name: 'Retention', score: indicators.retention.score },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Organizational Health Dashboard</h1>
          <p className="text-gray-500 mt-1">
            {health.employee_count} employees · {health.team_count} teams · {health.project_count} active projects
          </p>
        </div>
        <div className="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-xs">
          <span className={`w-2 h-2 rounded-full ${dataInfo?.active ? 'bg-green-500' : 'bg-blue-500'}`} />
          <span className="text-gray-500">Data:</span>
          <span className="font-medium text-gray-700">{health.data_source || 'employees.csv'}</span>
        </div>
      </div>

      <OrgPulseTicker />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <KPICard
          label="Composite Health"
          value={health.composite_score}
          subtitle="Overall Score"
          risk={health.overall_risk}
        />
        <KPICard
          label="Resilience"
          value={indicators.resilience.score}
          subtitle={`${indicators.resilience.details.spof_count} SPOFs`}
          risk={indicators.resilience.risk_level}
        />
        <KPICard
          label="Trust"
          value={indicators.trust.score}
          subtitle={`${indicators.trust.details.low_documentation_areas} low-doc areas`}
          risk={indicators.trust.risk_level}
        />
        <KPICard
          label="Retention"
          value={indicators.retention.score}
          subtitle="Employee retention index"
          risk={indicators.retention.risk_level}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Indicator Scores</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={indChartData}>
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="score" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Health Gauges</h2>
          <div className="grid grid-cols-2 gap-4">
            <GaugeChart score={health.composite_score} label="Composite" />
            <GaugeChart score={indicators.resilience.score} label="Resilience" />
            <GaugeChart score={indicators.trust.score} label="Trust" />
            <GaugeChart score={100 - indicators.burnout.score} label="Burnout (inverted)" />
          </div>
        </div>
      </div>

      {spof && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <KPICard label="Single Points of Failure" value={spof.total_spofs} subtitle="Employees with no backup" risk="HIGH" />
          <KPICard label="Critical SPOFs" value={spof.critical_spofs} subtitle="Highest severity" risk="CRITICAL" color="red" />
          <KPICard
            label="Annual Revenue at Risk"
            value={`$${(spof.total_annual_revenue_at_risk_usd / 1e6).toFixed(1)}M`}
            subtitle="From SPOF-related disruptions"
            risk="HIGH"
          />
        </div>
      )}

      {readiness && gaps && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <KPICard
            label="Workforce Readiness"
            value={`${readiness.readiness_score}`}
            subtitle={readiness.readiness_level}
            risk={readiness.readiness_level}
          />
          <KPICard
            label="Org-Wide Skill Gaps"
            value={gaps.total_gap_count}
            subtitle="Knowledge areas with no coverage"
            risk={gaps.total_gap_count > 5 ? 'HIGH' : 'MEDIUM'}
          />
        </div>
      )}

      {indicators.burnout.details.high_burnout_count > 0 && (
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <h3 className="font-semibold text-orange-800">Burnout Alert</h3>
          <p className="text-orange-700 text-sm mt-1">
            {indicators.burnout.details.high_burnout_count} employees show high burnout signals:
            {' '}{indicators.burnout.details.high_burnout_employees?.join(', ')}
          </p>
        </div>
      )}

      <ChatPanel onResult={setChatResult} />
    </div>
  )
}
