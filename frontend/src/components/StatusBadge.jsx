export default function StatusBadge({ level, small }) {
  const map = {
    LOW: 'bg-green-100 text-green-800',
    MEDIUM: 'bg-yellow-100 text-yellow-800',
    HIGH: 'bg-orange-100 text-orange-800',
    CRITICAL: 'bg-red-100 text-red-800',
    'Ready Now': 'bg-green-100 text-green-800',
    'Ready in 6-12 months': 'bg-yellow-100 text-yellow-800',
    'Long-term potential': 'bg-blue-100 text-blue-800',
  }
  const cls = map[level] || 'bg-gray-100 text-gray-800'
  return (
    <span className={`inline-block font-semibold rounded-full ${small ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm'} ${cls}`}>
      {level}
    </span>
  )
}
