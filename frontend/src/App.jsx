import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import Layout from './components/Layout'
import ErrorBoundary from './components/ErrorBoundary'
import Dashboard from './pages/Dashboard'
import Employees from './pages/Employees'
import EmployeeProfile from './pages/EmployeeProfile'
import WhatIf from './pages/WhatIf'
import SpofRanking from './pages/SpofRanking'
import SkillGaps from './pages/SkillGaps'
import SuccessionPlanning from './pages/SuccessionPlanning'
import KnowledgeConcentration from './pages/KnowledgeConcentration'
import WorkforceReadiness from './pages/WorkforceReadiness'
import Report from './pages/Report'
import Upload from './pages/Upload'

function Page({ children, fallback }) {
  return <ErrorBoundary fallback={fallback}>{children}</ErrorBoundary>
}

const TITLES = {
  '/': 'Dashboard',
  '/employees': 'Employees',
  '/whatif': 'What-If Simulator',
  '/spof': 'SPOF Ranking',
  '/skill-gaps': 'Skill Gaps',
  '/succession': 'Succession Planning',
  '/knowledge-concentration': 'Knowledge Concentration',
  '/workforce-readiness': 'Workforce Readiness',
  '/report': 'Report',
  '/upload': 'Upload',
}

export default function App() {
  const location = useLocation()

  useEffect(() => {
    const base = Object.entries(TITLES).find(([path]) => location.pathname === path)
    document.title = base ? `${base[1]} - TruPulse AI` : 'TruPulse AI'
  }, [location.pathname])

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Page fallback="Dashboard failed to load"><Dashboard /></Page>} />
        <Route path="/employees" element={<Page fallback="Employees page failed to load"><Employees /></Page>} />
        <Route path="/employee/:name" element={<Page fallback="Employee profile failed to load"><EmployeeProfile /></Page>} />
        <Route path="/whatif" element={<Page fallback="What-If simulator failed to load"><WhatIf /></Page>} />
        <Route path="/spof" element={<Page fallback="SPOF ranking failed to load"><SpofRanking /></Page>} />
        <Route path="/skill-gaps" element={<Page fallback="Skill gaps failed to load"><SkillGaps /></Page>} />
        <Route path="/succession" element={<Page fallback="Succession planning failed to load"><SuccessionPlanning /></Page>} />
        <Route path="/knowledge-concentration" element={<Page fallback="Knowledge concentration failed to load"><KnowledgeConcentration /></Page>} />
        <Route path="/workforce-readiness" element={<Page fallback="Workforce readiness failed to load"><WorkforceReadiness /></Page>} />
        <Route path="/report" element={<Page fallback="Report failed to load"><Report /></Page>} />
        <Route path="/upload" element={<Page fallback="Upload page failed to load"><Upload /></Page>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}
