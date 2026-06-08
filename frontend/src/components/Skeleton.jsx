export function SkeletonLine({ width = '100%', className = '' }) {
  return <div className={`h-4 bg-gray-200 rounded animate-pulse ${className}`} style={{ width }} />
}

export function SkeletonCard({ lines = 3, className = '' }) {
  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-5 space-y-3 ${className}`}>
      <SkeletonLine width="60%" />
      {Array.from({ length: lines }).map((_, i) => (
        <SkeletonLine key={i} width={`${70 + Math.random() * 30}%`} />
      ))}
    </div>
  )
}

export function SkeletonTable({ rows = 5, cols = 4 }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden animate-pulse">
      <div className="bg-gray-50 px-4 py-3 flex gap-4">
        {Array.from({ length: cols }).map((_, i) => (
          <div key={i} className="h-3 bg-gray-200 rounded" style={{ width: `${100 / cols}%` }} />
        ))}
      </div>
      {Array.from({ length: rows }).map((_, r) => (
        <div key={r} className="flex gap-4 px-4 py-3 border-t border-gray-100">
          {Array.from({ length: cols }).map((_, c) => (
            <div key={c} className="h-3 bg-gray-200 rounded" style={{ width: `${100 / cols}%` }} />
          ))}
        </div>
      ))}
    </div>
  )
}

export function SkeletonGrid({ cards = 4 }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {Array.from({ length: cards }).map((_, i) => (
        <SkeletonCard key={i} lines={2} />
      ))}
    </div>
  )
}

export function SkeletonPage() {
  return (
    <div className="space-y-5 animate-pulse">
      <div className="space-y-2">
        <div className="h-6 bg-gray-200 rounded w-48" />
        <div className="h-4 bg-gray-200 rounded w-72" />
      </div>
      <SkeletonGrid />
      <SkeletonCard lines={4} />
      <SkeletonTable rows={4} />
    </div>
  )
}
