export default function KPICard({ label, value, subtitle, color = 'tru', risk }) {
  const colorMap = {
    tru: 'text-tru-600 bg-tru-50 border-tru-200',
    green: 'text-green-600 bg-green-50 border-green-200',
    yellow: 'text-yellow-600 bg-yellow-50 border-yellow-200',
    red: 'text-red-600 bg-red-50 border-red-200',
  }
  const riskColor =
    risk === 'LOW' || risk === 'Low' ? 'green'
    : risk === 'HIGH' || risk === 'High' || risk === 'Critical' ? 'red'
    : risk === 'MEDIUM' || risk === 'Medium' ? 'yellow'
    : color

  return (
    <div className={`rounded-lg border p-4 ${colorMap[riskColor]}`}>
      <p className="text-sm font-medium opacity-75">{label}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
      {subtitle && <p className="text-xs mt-1 opacity-70">{subtitle}</p>}
      {risk && (
        <span className="inline-block mt-2 text-xs font-semibold uppercase tracking-wide px-2 py-0.5 rounded-full bg-white/60">
          {risk} Risk
        </span>
      )}
    </div>
  )
}
