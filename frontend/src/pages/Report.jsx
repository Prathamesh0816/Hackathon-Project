import { useState } from 'react'
import { getReportHtml } from '../services/api'
import Loading from '../components/Loading'

const EMPLOYEES = ['Vikram', 'Rahul', 'Neha', 'Sanjay', 'Nikhil', 'Aarti', 'Meera']

export default function Report() {
  const [scenarioType, setScenarioType] = useState('baseline')
  const [removed, setRemoved] = useState([])
  const [html, setHtml] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const toggleEmployee = (name) => {
    setRemoved((prev) =>
      prev.includes(name) ? prev.filter((e) => e !== name) : [...prev, name]
    )
  }

  const generateReport = async () => {
    setLoading(true)
    setError(null)
    try {
      const h = await getReportHtml(scenarioType, removed.join(','))
      setHtml(h)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Resilience Report</h1>
        <p className="text-gray-500 mt-1">Generate a downloadable HTML report</p>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-5 space-y-4">
        <div className="flex gap-3">
          <button
            onClick={() => setScenarioType('baseline')}
            className={`px-4 py-2 rounded-lg text-sm font-medium border transition-colors ${
              scenarioType === 'baseline'
                ? 'border-tru-500 bg-tru-50 text-tru-700'
                : 'border-gray-200 text-gray-600 hover:bg-gray-50'
            }`}
          >
            Current State
          </button>
          <button
            onClick={() => setScenarioType('attrition')}
            className={`px-4 py-2 rounded-lg text-sm font-medium border transition-colors ${
              scenarioType === 'attrition'
                ? 'border-tru-500 bg-tru-50 text-tru-700'
                : 'border-gray-200 text-gray-600 hover:bg-gray-50'
            }`}
          >
            What-If Report
          </button>
        </div>

        {scenarioType === 'attrition' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Select employees leaving</label>
            <div className="flex flex-wrap gap-2">
              {EMPLOYEES.map((name) => (
                <button
                  key={name}
                  onClick={() => toggleEmployee(name)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    removed.includes(name)
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

        <button
          onClick={generateReport}
          disabled={loading || (scenarioType === 'attrition' && removed.length === 0)}
          className="bg-tru-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-tru-700 disabled:opacity-50"
        >
          {loading ? 'Generating...' : 'Generate Report'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      {html && (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div className="bg-gray-50 border-b border-gray-200 px-4 py-2 flex justify-between items-center">
            <p className="text-sm font-medium text-gray-700">Report Preview</p>
            <button
              onClick={() => {
                const blob = new Blob([html], { type: 'text/html' })
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = 'trupulse-report.html'
                a.click()
                URL.revokeObjectURL(url)
              }}
              className="bg-tru-600 text-white px-3 py-1.5 rounded text-xs font-medium hover:bg-tru-700"
            >
              Download HTML
            </button>
          </div>
          <iframe
            srcDoc={html}
            title="Report"
            className="w-full h-[600px] border-0"
          />
        </div>
      )}
    </div>
  )
}
