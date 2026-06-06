import { useState } from 'react'

export default function FeedbackModal({ action, employee, onClose, onSubmit }) {
  const [decision, setDecision] = useState('accept')
  const [reason, setReason] = useState('')

  const handleSubmit = async () => {
    try {
      await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ employee, action_title: action, decision, reason }),
      })
      onSubmit?.(decision)
      onClose()
    } catch {
      alert('Failed to submit feedback')
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-xl shadow-2xl max-w-md w-full mx-4" onClick={(e) => e.stopPropagation()}>
        <div className="px-5 py-4 border-b border-gray-200">
          <h3 className="font-semibold text-gray-800">Human-in-the-Loop Review</h3>
          <p className="text-xs text-gray-500 mt-0.5">Your feedback improves future recommendations</p>
        </div>

        <div className="p-5 space-y-4">
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500">Action</p>
            <p className="font-medium text-gray-800">{action}</p>
            <p className="text-xs text-gray-500 mt-1">Employee: <span className="font-medium">{employee}</span></p>
          </div>

          <div>
            <p className="text-sm font-medium text-gray-700 mb-2">Your Decision</p>
            <div className="grid grid-cols-3 gap-2">
              {[
                { value: 'accept', label: '✅ Accept', desc: 'Proceed with this action', class: 'hover:border-green-400 hover:bg-green-50' },
                { value: 'veto', label: '❌ Veto', desc: 'Reject this recommendation', class: 'hover:border-red-400 hover:bg-red-50' },
                { value: 'modify', label: '✏️ Modify', desc: 'Suggest a change', class: 'hover:border-amber-400 hover:bg-amber-50' },
              ].map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => setDecision(opt.value)}
                  className={`p-3 rounded-lg border text-center transition-colors ${
                    decision === opt.value
                      ? 'border-tru-500 bg-tru-50'
                      : 'border-gray-200 ' + opt.class
                  }`}
                >
                  <p className="text-sm font-medium">{opt.label}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{opt.desc}</p>
                </button>
              ))}
            </div>
          </div>

          {decision === 'modify' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Your suggestion</label>
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                rows={3}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-tru-500"
                placeholder="Describe your alternative approach..."
              />
            </div>
          )}

          {decision === 'veto' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Reason (optional)</label>
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                rows={2}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-tru-500"
                placeholder="Why are you vetoing this?"
              />
            </div>
          )}
        </div>

        <div className="px-5 py-3 border-t border-gray-200 flex justify-end gap-2">
          <button onClick={onClose} className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800">
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            className={`px-4 py-2 rounded-lg text-sm font-medium text-white ${
              decision === 'accept' ? 'bg-green-600 hover:bg-green-700'
              : decision === 'veto' ? 'bg-red-600 hover:bg-red-700'
              : 'bg-amber-600 hover:bg-amber-700'
            }`}
          >
            Submit {decision === 'accept' ? 'Approval' : decision === 'veto' ? 'Veto' : 'Modification'}
          </button>
        </div>
      </div>
    </div>
  )
}
