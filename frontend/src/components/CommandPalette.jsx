import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTheme } from '../context/ThemeContext'

const PAGES = [
  { id: 'dashboard', label: 'Dashboard', path: '/', keywords: 'home overview health' },
  { id: 'employees', label: 'Employees', path: '/employees', keywords: 'people staff team members list' },
  { id: 'whatif', label: 'What-If Simulator', path: '/whatif', keywords: 'simulate scenario attrition workload restructuring' },
  { id: 'spof', label: 'SPOF Ranking', path: '/spof', keywords: 'single point failure critical risk' },
  { id: 'skillgaps', label: 'Skill Gaps', path: '/skill-gaps', keywords: 'skills missing gaps knowledge' },
  { id: 'succession', label: 'Succession Planning', path: '/succession', keywords: 'succession backup replacement pipeline' },
  { id: 'knowledge', label: 'Knowledge Risk', path: '/knowledge-concentration', keywords: 'knowledge concentration risk documentation' },
  { id: 'readiness', label: 'Workforce Readiness', path: '/workforce-readiness', keywords: 'readiness capacity project demand' },
  { id: 'report', label: 'Resilience Report', path: '/report', keywords: 'report download pdf generate' },
  { id: 'upload', label: 'Upload Data', path: '/upload', keywords: 'upload csv dataset file import' },
]

const ACTIONS = [
  { id: 'darkmode', label: 'Toggle dark mode', action: 'toggleDark', keywords: 'dark light theme mode' },
]

function fuzzyMatch(text, query) {
  const q = query.toLowerCase()
  const t = text.toLowerCase()
  let qi = 0
  for (let i = 0; i < t.length && qi < q.length; i++) {
    if (t[i] === q[qi]) qi++
  }
  return qi === q.length
}

export default function CommandPalette() {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [selectedIdx, setSelectedIdx] = useState(0)
  const inputRef = useRef(null)
  const navigate = useNavigate()
  const { toggleDark } = useTheme()

  // Filter items
  const allItems = [
    ...PAGES.map((p) => ({ ...p, type: 'page' })),
    ...ACTIONS.map((a) => ({ ...a, type: 'action' })),
  ]

  const filtered = query.trim()
    ? allItems.filter((item) => fuzzyMatch(`${item.label} ${item.keywords}`, query))
    : allItems

  useEffect(() => {
    const handler = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        setOpen((o) => !o)
        setQuery('')
        setSelectedIdx(0)
      }
      if (e.key === 'Escape' && open) {
        setOpen(false)
        setQuery('')
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [open])

  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [open])

  const execute = useCallback((item) => {
    setOpen(false)
    setQuery('')
    if (item.type === 'page') {
      navigate(item.path)
    } else if (item.action === 'toggleDark') {
      toggleDark()
    }
  }, [navigate, toggleDark])

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setSelectedIdx((i) => Math.min(i + 1, filtered.length - 1))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setSelectedIdx((i) => Math.max(i - 1, 0))
    } else if (e.key === 'Enter' && filtered[selectedIdx]) {
      e.preventDefault()
      execute(filtered[selectedIdx])
    }
  }

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]" onClick={() => { setOpen(false); setQuery('') }}>
      <div className="fixed inset-0 bg-black/40" onClick={() => { setOpen(false); setQuery('') }} />
      <div
        className="relative bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden animate-fade-in"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-200 dark:border-gray-700">
          <span className="text-gray-400 text-lg">⌘</span>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => { setQuery(e.target.value); setSelectedIdx(0) }}
            onKeyDown={handleKeyDown}
            placeholder="Search pages or run commands..."
            className="flex-1 bg-transparent text-sm text-gray-800 dark:text-gray-100 outline-none placeholder-gray-400"
          />
          <kbd className="text-[10px] px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-400 font-mono border border-gray-200 dark:border-gray-600">
            ESC
          </kbd>
        </div>

        <div className="max-h-72 overflow-y-auto p-2">
          {filtered.length === 0 ? (
            <div className="text-center py-8 text-sm text-gray-400">No results for "{query}"</div>
          ) : (
            <div className="space-y-0.5">
              {filtered.map((item, i) => (
                <button
                  key={item.id}
                  onClick={() => execute(item)}
                  onMouseEnter={() => setSelectedIdx(i)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-left transition-colors ${
                    i === selectedIdx
                      ? 'bg-tru-50 dark:bg-tru-900/30 text-tru-700 dark:text-tru-300'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50'
                  }`}
                >
                  <span className="text-base">
                    {item.type === 'page' ? '📄' : item.action === 'toggleDark' ? '🌙' : '🗑'}
                  </span>
                  <div className="flex-1">
                    <p className="font-medium">{item.label}</p>
                    <p className="text-xs text-gray-400">
                      {item.type === 'page' ? item.path : item.keywords?.split(' ').slice(0, 3).join(' · ')}
                    </p>
                  </div>
                  {item.type === 'page' && (
                    <span className="text-[10px] text-gray-400 font-mono">↵</span>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="flex items-center gap-4 px-4 py-2 border-t border-gray-200 dark:border-gray-700 text-[10px] text-gray-400">
          <span><kbd className="px-1 py-0.5 rounded bg-gray-100 dark:bg-gray-700 font-mono">↑↓</kbd> navigate</span>
          <span><kbd className="px-1 py-0.5 rounded bg-gray-100 dark:bg-gray-700 font-mono">↵</kbd> select</span>
          <span><kbd className="px-1 py-0.5 rounded bg-gray-100 dark:bg-gray-700 font-mono">Esc</kbd> close</span>
        </div>
      </div>
    </div>
  )
}
