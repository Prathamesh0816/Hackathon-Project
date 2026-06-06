import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Loading from '../components/Loading'
import ErrorState from '../components/ErrorState'
import StatusBadge from '../components/StatusBadge'

const TEAMS = [
  'All', 'Sales', 'Product', 'Engineering', 'Security', 'Support',
  'Infrastructure', 'Finance', 'HR', 'Marketing', 'Legal', 'Operations',
]

export default function Employees() {
  const [employees, setEmployees] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [teamFilter, setTeamFilter] = useState('All')
  const [search, setSearch] = useState('')

  useEffect(() => {
    fetch('/api/employee-data/EMP001')
      .then((r) => r.json())
      .then(() => {
        return fetch('/api/org-health')
      })
      .then((r) => r.json())
      .then((health) => {
        const empData = [
          {id:'EMP001',name:'Vikram',team:'Sales',role:'Sales Manager'},
          {id:'EMP002',name:'Anjali',team:'Sales',role:'Account Executive'},
          {id:'EMP003',name:'Rohit',team:'Sales',role:'Account Executive'},
          {id:'EMP004',name:'Priya',team:'Sales',role:'Account Executive'},
          {id:'EMP005',name:'Aditya',team:'Sales',role:'Sales Development Rep'},
          {id:'EMP006',name:'Neha',team:'Product',role:'Product Manager'},
          {id:'EMP007',name:'Arjun',team:'Product',role:'Business Analyst'},
          {id:'EMP008',name:'Pooja',team:'Product',role:'Product Owner'},
          {id:'EMP009',name:'Meera',team:'Product',role:'UX Researcher'},
          {id:'EMP010',name:'Kavya',team:'Product',role:'UX Designer'},
          {id:'EMP011',name:'Rahul',team:'Engineering',role:'Lead Backend Engineer'},
          {id:'EMP012',name:'Amit',team:'Engineering',role:'Backend Engineer'},
          {id:'EMP013',name:'Sneha',team:'Engineering',role:'DevOps Engineer'},
          {id:'EMP014',name:'Karan',team:'Engineering',role:'QA Lead'},
          {id:'EMP015',name:'Ravi',team:'Engineering',role:'QA Engineer'},
          {id:'EMP016',name:'Isha',team:'Engineering',role:'Junior Backend Engineer'},
          {id:'EMP017',name:'Sanjay',team:'Security',role:'Security Architect'},
          {id:'EMP018',name:'Tanvi',team:'Security',role:'Security Analyst'},
          {id:'EMP019',name:'Deepak',team:'Security',role:'Security Analyst'},
          {id:'EMP020',name:'Meera',team:'Support',role:'Support Lead'},
          {id:'EMP021',name:'Kavya',team:'Support',role:'Support Engineer'},
          {id:'EMP022',name:'Rishi',team:'Support',role:'Support Engineer'},
          {id:'EMP023',name:'Nikhil',team:'Infrastructure',role:'Cloud Architect'},
          {id:'EMP024',name:'Harsh',team:'Infrastructure',role:'Network Engineer'},
          {id:'EMP025',name:'Manoj',team:'Infrastructure',role:'Junior Sysadmin'},
          {id:'EMP026',name:'Rajesh',team:'Finance',role:'Finance Manager'},
          {id:'EMP027',name:'Sunita',team:'Finance',role:'Senior Accountant'},
          {id:'EMP028',name:'Kavita',team:'Finance',role:'Accountant'},
          {id:'EMP029',name:'Aarti',team:'HR',role:'HR Manager'},
          {id:'EMP030',name:'Sneha',team:'HR',role:'Recruiter'},
          {id:'EMP031',name:'Vivek',team:'Marketing',role:'Marketing Lead'},
          {id:'EMP032',name:'Aakash',team:'Marketing',role:'Content Strategist'},
          {id:'EMP033',name:'Amit',team:'Legal',role:'Legal Counsel'},
          {id:'EMP034',name:'Rohit',team:'Legal',role:'Legal Analyst'},
          {id:'EMP035',name:'Anjali',team:'Operations',role:'Operations Manager'},
        ]
        setEmployees(empData)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Loading />
  if (error) return <ErrorState message={error} />

  const filtered = employees.filter((e) => {
    if (teamFilter !== 'All' && e.team !== teamFilter) return false
    if (search && !e.name.toLowerCase().includes(search.toLowerCase())) return false
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
          placeholder="Search by name..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-64 focus:outline-none focus:ring-2 focus:ring-tru-500"
        />
        <div className="flex flex-wrap gap-2">
          {TEAMS.map((t) => (
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
            {filtered.map((emp) => (
              <tr key={emp.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-900">{emp.name}</td>
                <td className="px-4 py-3">
                  <StatusBadge level={emp.team} small />
                </td>
                <td className="px-4 py-3 text-gray-600">{emp.role}</td>
                <td className="px-4 py-3 text-right">
                  <Link
                    to={`/employee/${emp.name}`}
                    className="text-tru-600 hover:text-tru-800 font-medium text-xs"
                  >
                    View Profile →
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
