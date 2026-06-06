export default function GaugeChart({ score, label, size = 120 }) {
  const r = 45
  const circumference = 2 * Math.PI * r
  const offset = circumference - (score / 100) * circumference
  const color =
    score >= 70 ? '#16a34a'
    : score >= 45 ? '#d97706'
    : '#dc2626'

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size * 0.6} viewBox="0 0 100 55">
        <path
          d="M 10 50 A 40 40 0 0 1 90 50"
          fill="none"
          stroke="#e5e7eb"
          strokeWidth="8"
          strokeLinecap="round"
        />
        <path
          d="M 10 50 A 40 40 0 0 1 90 50"
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={`${(score / 100) * 180} 180`}
          strokeDashoffset="0"
        />
        <text x="50" y="42" textAnchor="middle" fontSize="16" fontWeight="bold" fill={color}>
          {score}
        </text>
      </svg>
      {label && <p className="text-xs text-gray-500 mt-1">{label}</p>}
    </div>
  )
}
