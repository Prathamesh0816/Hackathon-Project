import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getEmployeeProfile, getUpskilling } from '../services/api'
import { SkeletonPage } from '../components/Skeleton'
import ErrorState from '../components/ErrorState'
import StatusBadge from '../components/StatusBadge'

export default function EmployeeProfile() {
  const { name } = useParams()
  const [profile, setProfile] = useState(null)
  const [upskilling, setUpskilling] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([getEmployeeProfile(name), getUpskilling(name)])
      .then(([p, u]) => {
        setProfile(p)
        setUpskilling(u)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [name])

  if (loading) return <SkeletonPage />
  if (error) return <ErrorState message={error} />
  if (!profile || profile.error) return <ErrorState message={profile?.error || 'Employee not found'} />

  return (
    <div className="space-y-6">
      <Link to="/employees" className="text-tru-600 text-sm hover:underline">&larr; Back to Employees</Link>

      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{profile.employee}</h1>
            <p className="text-gray-500">{profile.role} · {profile.team}</p>
          </div>
          <div className="flex gap-2">
            <StatusBadge level={profile.criticality} />
            {profile.is_spof && <StatusBadge level="CRITICAL" />}
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-6">
          <div className="bg-gray-50 rounded p-3 text-center">
            <p className="text-2xl font-bold text-gray-800">{profile.experience_years}</p>
            <p className="text-xs text-gray-500">Experience (yrs)</p>
          </div>
          <div className="bg-gray-50 rounded p-3 text-center">
            <p className="text-2xl font-bold text-gray-800">{profile.tenure_years}</p>
            <p className="text-xs text-gray-500">Tenure (yrs)</p>
          </div>
          <div className="bg-gray-50 rounded p-3 text-center">
            <p className="text-2xl font-bold text-gray-800">${(profile.annual_salary_usd / 1000).toFixed(0)}K</p>
            <p className="text-xs text-gray-500">Salary</p>
          </div>
          <div className="bg-gray-50 rounded p-3 text-center">
            <p className="text-2xl font-bold text-gray-800">{profile.knowledge_count}</p>
            <p className="text-xs text-gray-500">Knowledge Areas</p>
          </div>
          <div className="bg-gray-50 rounded p-3 text-center">
            <p className="text-2xl font-bold text-gray-800">{profile.low_doc_areas}</p>
            <p className="text-xs text-gray-500">Low Documentation</p>
          </div>
        </div>

        {profile.backup_available === 'No' && (
          <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-red-700 text-sm font-medium">No backup available — Single Point of Failure</p>
          </div>
        )}
      </div>

      {profile.knowledge_areas?.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">Knowledge Areas</h2>
          <div className="space-y-2">
            {profile.knowledge_areas.map((ka, i) => (
              <div key={i} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                <span className="text-sm text-gray-700">{ka.KnowledgeArea}</span>
                <div className="flex gap-2">
                  <StatusBadge level={ka.Proficiency} small />
                  <StatusBadge level={ka.DocumentationLevel === 'High' ? 'LOW' : ka.DocumentationLevel === 'Medium' ? 'MEDIUM' : 'HIGH'} small />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {profile.dependents?.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">Dependents ({profile.dependents.length})</h2>
          <div className="space-y-2">
            {profile.dependents.map((d, i) => (
              <div key={i} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                <div>
                  <Link to={`/employee/${d.Dependent}`} className="text-tru-600 hover:underline text-sm font-medium">
                    {d.Dependent}
                  </Link>
                  <p className="text-xs text-gray-500">{d.DependencyType}</p>
                </div>
                <StatusBadge level={d.Criticality} small />
              </div>
            ))}
          </div>
        </div>
      )}

      {profile.projects?.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">Projects</h2>
          <div className="space-y-2">
            {profile.projects.map((p, i) => (
              <div key={i} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                <div>
                  <p className="text-sm font-medium text-gray-700">{p.Project}</p>
                  <p className="text-xs text-gray-500">{p.Client} · {p.DeadlineDays} days to deadline</p>
                </div>
                <StatusBadge level={p.Criticality} small />
              </div>
            ))}
          </div>
        </div>
      )}

      {upskilling && !upskilling.error && upskilling.recommendations?.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-5">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">Upskilling Recommendations</h2>
          <div className="space-y-3">
            {upskilling.recommendations.map((rec, i) => (
              <div key={i} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-medium text-gray-800">{rec.skill}</p>
                    <p className="text-sm text-gray-600 mt-1">{rec.action}</p>
                    <p className="text-xs text-gray-500 mt-1">{rec.method} · {rec.duration_weeks} weeks</p>
                  </div>
                  <StatusBadge level={rec.priority} small />
                </div>
                <p className="text-xs text-gray-500 mt-2">{rec.rationale}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
