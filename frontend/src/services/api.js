const BASE = '/api'

async function fetcher(path) {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`)
  return res.json()
}

async function poster(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const detail = await res.text().catch(() => '')
    throw new Error(`POST ${path} failed: ${res.status} ${detail}`)
  }
  return res.json()
}

export const getOrgHealth = () => fetcher('/org-health')
export const getEmployeeProfile = (name) => fetcher(`/employee/${encodeURIComponent(name)}`)
export const getSkillGaps = () => fetcher('/skill-gaps')
export const getSuccessionPlanning = () => fetcher('/succession-planning')
export const getWorkforceReadiness = () => fetcher('/workforce-readiness')
export const getKnowledgeConcentration = () => fetcher('/knowledge-concentration')
export const getSpofRanking = () => fetcher('/spof-ranking')
export const getUpskilling = (name) => fetcher(`/upskilling/${encodeURIComponent(name)}`)
export const getEmployeeData = (id) => fetcher(`/employee-data/${id}`)
export const postWhatIf = (body) => poster('/whatif', body)
export const postPipeline = (body) => poster('/pipeline', body)
export const postTextInput = (body) => poster('/text-input', body)
export const postFeedback = (body) => poster('/feedback', body)
export const getFeedback = () => fetcher('/feedback')
export const getSuggestions = () => poster('/feedback/suggestions', {})
export const postApplyDecisions = (body) => poster('/feedback/apply', body)
export const getReportHtml = async (scenarioType, removed) => {
  const res = await fetch(`${BASE}/report?scenario_type=${scenarioType}&removed=${encodeURIComponent(removed)}`)
  if (!res.ok) throw new Error('Report fetch failed')
  return res.text()
}

// ---- Dataset / Upload API ----
export const uploadDataset = async (file) => {
  const form = new FormData()
  form.append('file', file)
  form.append('auto_activate', 'true')
  const res = await fetch(`${BASE}/dataset/upload`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(`Upload failed: ${res.status}`)
  return res.json()
}

export const previewDataset = async (file) => {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}/dataset/preview`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(`Preview failed: ${res.status}`)
  return res.json()
}

export const getDatasetInfo = () => fetcher('/dataset/info')
export const getDatasetFiles = () => fetcher('/dataset/files')
export const postDatasetActivate = (filename, mapping) => poster('/dataset/activate', { filename, column_mapping: mapping || null })
export const postDatasetClear = () => poster('/dataset/clear', {})
export const getDatasetEmployees = () => fetcher('/dataset/employees')

// ---- Scenarios API ----
export const getScenarios = () => fetcher('/scenarios')
export const postRunScenario = (body) => poster('/whatif', body)
export const postScenarioRun = (body) => poster('/scenario-run', body)
export const getReactions = () => fetcher('/reactions')
