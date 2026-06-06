import { useState } from 'react'
import { postTextInput } from '../services/api'

const TEMPLATE = `Employee: Vikram, Team: Sales, Role: Sales Manager, Criticality: High, Backup: No
Employee: Anjali, Team: Sales, Role: Account Executive, Criticality: Medium, Backup: Yes
Employee: Rahul, Team: Engineering, Role: Lead Engineer, Criticality: High, Backup: No`

export default function TextInput({ onParsed }) {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleSubmit = async () => {
    if (!text.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await postTextInput({ text, source: 'manual' })
      setResult(res)
      if (onParsed) onParsed(res.employees)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5">
      <h3 className="text-sm font-semibold text-gray-900 mb-2">Paste Employee Data</h3>
      <p className="text-xs text-gray-500 mb-3">
        Enter employee data as plain text. One employee per line. Format: <code className="bg-gray-100 px-1 rounded">Employee: Name, Team: Team, Role: Role, Criticality: High/Medium/Low, Backup: Yes/No</code>
      </p>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={TEMPLATE}
        rows={6}
        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-tru-500 resize-none"
      />
      <div className="flex items-center gap-3 mt-3">
        <button
          onClick={handleSubmit}
          disabled={loading || !text.trim()}
          className="px-4 py-2 bg-tru-600 text-white rounded-lg text-sm font-medium hover:bg-tru-700 disabled:opacity-50 transition-colors"
        >
          {loading ? 'Parsing...' : 'Parse & Add'}
        </button>
        {result && (
          <span className="text-xs text-green-600">
            Parsed {result.parsed_count} employees
          </span>
        )}
      </div>
      {error && <p className="text-xs text-red-500 mt-2">{error}</p>}
    </div>
  )
}
