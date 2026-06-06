import { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, LabelList } from 'recharts'

function DeltaBadge({ value }) {
  if (value === 0) return <span className="text-gray-400 text-sm">0</span>
  const isDown = value < 0
  return (
    <span className={`inline-flex items-center gap-0.5 text-sm font-bold ${isDown ? 'text-red-600' : 'text-green-600'}`}>
      {isDown ? '▼' : '▲'} {Math.abs(value)}
    </span>
  )
}

export default function TimeMachine({ baseline, projected, onShare }) {
  const [view, setView] = useState('cards')

  if (!baseline || !projected) return null

  const indicators = ['resilience', 'trust', 'burnout', 'retention']
  const chartData = indicators.map((key) => {
    const bVal = typeof baseline.indicators[key] === 'object'
      ? baseline.indicators[key].score || baseline.indicators[key]
      : baseline.indicators[key]
    const pVal = typeof projected.indicators[key] === 'object'
      ? projected.indicators[key].score || projected.indicators[key]
      : projected.indicators[key]
    return {
      name: key.charAt(0).toUpperCase() + key.slice(1),
      Before: bVal,
      After: pVal,
      delta: Math.round((pVal - bVal) * 10) / 10,
    }
  })

  const revenueAtRisk = projected.revenue_at_risk_usd || 0
  const compositeBefore = baseline.composite_score || baseline.composite
  const compositeAfter = projected.composite_score || projected.composite
  const compositeDelta = Math.round((compositeAfter - compositeBefore) * 10) / 10

  return (
    <div className="bg-white rounded-lg border-2 border-tru-200 overflow-hidden">
      <div className="tru-gradient px-5 py-4 flex items-center justify-between">
        <div>
          <h2 className="text-white text-lg font-bold">⏳ Time Machine</h2>
          <p className="text-blue-200 text-xs mt-0.5">Drag the timeline to compare scenarios</p>
        </div>
        {onShare && (
          <button onClick={onShare} className="bg-white/20 text-white px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-white/30">
            Share This View
          </button>
        )}
      </div>

      <div className="p-5 space-y-5">
        {/* Composite score showdown */}
        <div className="flex items-center gap-6 p-4 bg-gray-50 rounded-lg">
          <div className="flex-1 text-center">
            <p className="text-xs text-gray-500 uppercase tracking-wide">Before</p>
            <p className="text-3xl font-bold text-gray-800">{compositeBefore}</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-gray-500 uppercase tracking-wide">Delta</p>
            <DeltaBadge value={compositeDelta} />
            <p className="text-base font-bold mt-1">
              {compositeDelta < 0 ? `${Math.abs(compositeDelta)} point drop` : `${compositeDelta} point gain`}
            </p>
          </div>
          <div className="flex-1 text-center">
            <p className="text-xs text-gray-500 uppercase tracking-wide">After</p>
            <p className="text-3xl font-bold text-gray-800">{compositeAfter}</p>
          </div>
        </div>

        {/* Revenue at risk banner */}
        {revenueAtRisk > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
            <p className="text-xs text-red-600 uppercase tracking-wide font-medium">Revenue at Risk</p>
            <p className="text-2xl font-bold text-red-700">${(revenueAtRisk / 1e6).toFixed(1)}M</p>
            <p className="text-xs text-red-500 mt-0.5">Annual contract value exposed if this scenario materializes</p>
          </div>
        )}

        {/* Indicator comparison chart */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-gray-700">Indicator Comparison</h3>
            <div className="flex gap-1 bg-gray-100 rounded-lg p-0.5">
              <button
                onClick={() => setView('cards')}
                className={`px-3 py-1 rounded text-xs font-medium transition-colors ${view === 'cards' ? 'bg-white shadow' : 'text-gray-500'}`}
              >
                Cards
              </button>
              <button
                onClick={() => setView('chart')}
                className={`px-3 py-1 rounded text-xs font-medium transition-colors ${view === 'chart' ? 'bg-white shadow' : 'text-gray-500'}`}
              >
                Chart
              </button>
            </div>
          </div>

          {view === 'cards' ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {chartData.map((item) => (
                <div key={item.name} className="border border-gray-200 rounded-lg p-3">
                  <p className="text-xs text-gray-500 font-medium uppercase">{item.name}</p>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-gray-500 text-sm">{item.Before}</span>
                    <span className="text-gray-300">→</span>
                    <span className="font-bold text-gray-800">{item.After}</span>
                  </div>
                  <div className="mt-1">
                    <DeltaBadge value={item.delta} />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={chartData}>
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Bar dataKey="Before" fill="#94a3b8" radius={[4, 4, 0, 0]} />
                <Bar dataKey="After" fill="#2563eb" radius={[4, 4, 0, 0]}>
                  <LabelList dataKey="delta" position="top" fontSize={11} fontWeight="bold" fill={compositeDelta < 0 ? '#dc2626' : '#16a34a'} />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Impact summary */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-semibold text-gray-700 text-sm mb-2">Impact Summary</h3>
          <ul className="space-y-1 text-sm text-gray-600">
            {chartData.map((item) => (
              <li key={item.name} className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${item.delta < 0 ? 'bg-red-500' : item.delta > 0 ? 'bg-green-500' : 'bg-gray-300'}`} />
                <span className="font-medium capitalize">{item.name}:</span>
                <span className="text-gray-500">{item.Before} → {item.After}</span>
                <DeltaBadge value={item.delta} />
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}
