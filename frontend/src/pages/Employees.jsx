import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { SkeletonTable } from '../components/Skeleton'
import ErrorState from '../components/ErrorState'
import StatusBadge from '../components/StatusBadge'
import { getEmployees } from '../services/api'

export default function Employees() {
  const [employees, setEmployees] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [teamFilter, setTeamFilter] = useState('All')
  const [search, setSearch] = useState('')

  useEffect(() => {
    getEmployees()
      .then((data) => setEmployees(data.employees || []))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const teams = [...new Set(employees.map((e) => e.team))].sort()

  if (loading) return <div className="space-y-5"><div className="h-6 bg-gray-200 rounded w-48 animate-pulse" /><SkeletonTable rows={8} cols={4} /></div>
  if (error) return <ErrorState message={error} />

  const filtered = employees.filter((e) => {
    if (teamFilter !== 'All' && e.team !== teamFilter) return false
    if (search) {
      const q = search.toLowerCase()
      const name = (e.name || e.Employee || '').toLowerCase()
      const team = (e.team || '').toLowerCase()
      const role = (e.role || '').toLowerCase()
      if (!name.includes(q) && !team.includes(q) && !role.includes(q)) return false
    }
    return true
  })

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Employees</h1>
        <p className="text-gray-500 mt-1">{filtered.length} employees</p>
      </div>

      <div className="flex flex-wrap gap-3 items-center">
        <input
          type="text"
          placeholder="Search by name, team, role..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-64 focus:outline-none focus:ring-2 focus:ring-tru-500"
        />
        <div className="flex flex-wrap gap-2">
          {['All', ...teams].map((t) => (
            <button
              key={t}
              onClick={() => setTeamFilter(t)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                teamFilter === t
                  ? 'bg-tru-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-gray-600">
            <tr>
              <th className="text-left px-4 py-3 font-medium">Name</th>
              <th className="text-left px-4 py-3 font-medium">Team</th>
              <th className="text-left px-4 py-3 font-medium">Role</th>
              <th className="text-right px-4 py-3 font-medium">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-4 py-12 text-center text-gray-400">
                  {search ? 'No employees match your search' : 'No employees found'}
                </td>
              </tr>
            ) : (
              filtered.map((emp) => (
                <tr key={emp.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{emp.name || emp.Employee}</td>
                  <td className="px-4 py-3">
                    <StatusBadge level={emp.team} small />
                  </td>
                  <td className="px-4 py-3 text-gray-600">{emp.role || '—'}</td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      to={`/employee/${encodeURIComponent(emp.name || emp.Employee || '')}`}
                      className="text-tru-600 hover:text-tru-800 font-medium text-xs"
                    >
                      View Profile →
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
