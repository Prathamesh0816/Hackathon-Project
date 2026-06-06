import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
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

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/employees" element={<Employees />} />
        <Route path="/employee/:name" element={<EmployeeProfile />} />
        <Route path="/whatif" element={<WhatIf />} />
        <Route path="/spof" element={<SpofRanking />} />
        <Route path="/skill-gaps" element={<SkillGaps />} />
        <Route path="/succession" element={<SuccessionPlanning />} />
        <Route path="/knowledge-concentration" element={<KnowledgeConcentration />} />
        <Route path="/workforce-readiness" element={<WorkforceReadiness />} />
        <Route path="/report" element={<Report />} />
        <Route path="/upload" element={<Upload />} />
      </Routes>
    </Layout>
  )
}
