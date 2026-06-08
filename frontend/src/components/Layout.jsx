import { NavLink } from 'react-router-dom'
import WhatIfFloating from './WhatIfFloating'

const navItems = [
  { path: '/', label: 'Dashboard', icon: '◉' },
  { path: '/employees', label: 'Employees', icon: '👥' },
  { path: '/whatif', label: 'What-If Simulator', icon: '🔮' },
  { path: '/spof', label: 'SPOF Ranking', icon: '⚠️' },
  { path: '/skill-gaps', label: 'Skill Gaps', icon: '📊' },
  { path: '/succession', label: 'Succession Planning', icon: '📋' },
  { path: '/knowledge-concentration', label: 'Knowledge Risk', icon: '🧠' },
  { path: '/workforce-readiness', label: 'Workforce Readiness', icon: '📈' },
  { path: '/report', label: 'Resilience Report', icon: '📄' },
  { path: '/upload', label: 'Upload Data', icon: '📁' },
]

export default function Layout({ children }) {
  return (
    <div className="min-h-screen flex">
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="tru-gradient p-4">
          <h1 className="text-white text-lg font-bold">TruPulse AI</h1>
          <p className="text-blue-200 text-xs">Organizational Resilience</p>
        </div>
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-tru-50 text-tru-700'
                    : 'text-gray-600 hover:bg-gray-100'
                }`
              }
            >
              <span className="text-lg">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-gray-200">
          <p className="text-xs text-gray-400">Predict. Simulate. Strengthen.</p>
        </div>
      </aside>
      <main className="flex-1 flex flex-col">
        <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
          <p className="text-sm text-gray-500">TruPulse AI v2.0</p>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-500" />
            <span className="text-xs text-gray-500">API Connected</span>
          </div>
        </header>
        <div className="flex-1 p-6 overflow-y-auto">{children}</div>
      </main>
      <WhatIfFloating />
    </div>
  )
}
