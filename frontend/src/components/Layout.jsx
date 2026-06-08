import { NavLink } from 'react-router-dom'
import { useTheme } from '../context/ThemeContext'
import KeyboardShortcuts from './KeyboardShortcuts'
import CommandPalette from './CommandPalette'
import WhatIfFloating from './WhatIfFloating'
import { useEffect, useState } from 'react'

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
  const { dark, toggleDark } = useTheme()
  const [apiOk, setApiOk] = useState(true)

  // Ctrl+D for dark mode
  useEffect(() => {
    const handler = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault()
        toggleDark()
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [toggleDark])

  return (
    <div className="min-h-screen flex bg-gray-50 dark:bg-gray-900 transition-colors">
      <aside className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col transition-colors">
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
                    ? 'bg-tru-50 dark:bg-tru-900/30 text-tru-700 dark:text-tru-300'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`
              }
            >
              <span className="text-lg">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-gray-400 dark:text-gray-500">Predict. Simulate. Strengthen.</p>
        </div>
      </aside>
      <main className="flex-1 flex flex-col">
        <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-3 flex items-center justify-between transition-colors">
          <p className="text-sm text-gray-500 dark:text-gray-400">TruPulse AI v2.0</p>
          <div className="flex items-center gap-3">
            <button
              onClick={toggleDark}
              className="text-sm text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors px-2 py-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
              title="Toggle dark mode (Ctrl+D)"
            >
              {dark ? '☀️' : '🌙'}
            </button>
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${apiOk ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-xs text-gray-500 dark:text-gray-400">{apiOk ? 'API Connected' : 'API Error'}</span>
            </div>
          </div>
        </header>
        <div className="flex-1 p-6 overflow-y-auto">{children}</div>
      </main>
      <WhatIfFloating />
      <KeyboardShortcuts />
      <CommandPalette />
    </div>
  )
}
