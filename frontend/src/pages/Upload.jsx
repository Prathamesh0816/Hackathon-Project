import { useState, useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useToast } from '../context/ToastContext'
import { uploadDataset, previewDataset, getDatasetInfo, getDatasetFiles, postDatasetActivate, postDatasetClear, getScenarios, postScenarioRun, getReactions } from '../services/api'

export default function Upload() {
  const { addToast } = useToast()
  const [mode, setMode] = useState('default') // 'default' | 'upload' | 'scenario'
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [datasetInfo, setDatasetInfo] = useState(null)
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [scenarios, setScenarios] = useState(null)
  const [reactions, setReactions] = useState(null)
  const [scenarioResult, setScenarioResult] = useState(null)
  const [loadingScenario, setLoadingScenario] = useState(false)
  const [selectedScenario, setSelectedScenario] = useState(null)
  const [selectedReaction, setSelectedReaction] = useState('standard')
  const [expandedCategory, setExpandedCategory] = useState(null)
  const [probability, setProbability] = useState(50)
  const inputRef = useRef(null)

  useEffect(() => { loadInfo(); loadScenarios() }, [])

  async function loadInfo() {
    try {
      const [info, files] = await Promise.all([getDatasetInfo(), getDatasetFiles()])
      setDatasetInfo(info)
      setUploadedFiles(files.files || [])
    } catch {}
  }

  async function loadScenarios() {
    try {
      const [s, r] = await Promise.all([getScenarios(), getReactions()])
      setScenarios(s)
      setReactions(r)
    } catch {}
  }

  async function handleSelect(e) {
    const f = e.target.files?.[0]
    if (!f) return
    setFile(f)
    setError('')
    setResult(null)
    try {
      const p = await previewDataset(f)
      setPreview(p)
    } catch (err) {
      setError('Preview failed: ' + err.message)
    }
  }

  function handleDrop(e) {
    e.preventDefault()
    const f = e.dataTransfer?.files?.[0]
    if (f) {
      setFile(f)
      setError('')
      setResult(null)
      previewDataset(f).then(setPreview).catch(err => setError('Preview failed: ' + err.message))
    }
  }

  async function handleUpload() {
    if (!file) return
    setUploading(true)
    setError('')
    try {
      const r = await uploadDataset(file)
      setResult(r)
      addToast(`Dataset "${file.name}" uploaded successfully`)
      await loadInfo()
    } catch (err) {
      setError(err.message)
      addToast(err.message, 'error')
    }
    setUploading(false)
  }

  async function handleActivate(filename) {
    try {
      const r = await postDatasetActivate(filename)
      setResult(r)
      addToast(`Activated: ${filename}`)
      await loadInfo()
    } catch (err) {
      setError(err.message)
      addToast(err.message, 'error')
    }
  }

  async function handleClear() {
    try {
      await postDatasetClear()
      setResult({ message: 'Reset to default CSVs' })
      setFile(null)
      setPreview(null)
      setScenarioResult(null)
      setSelectedScenario(null)
      setSelectedReaction('standard')
      setProbability(50)
      addToast('Reset to default dataset')
      await loadInfo()
    } catch (err) {
      setError(err.message)
      addToast(err.message, 'error')
    }
  }

  function getScenarioBody(scenarioDef) {
    if (scenarioDef.workload_increase_pct) {
      return { scenario_type: 'workload_increase', workload_increase_pct: scenarioDef.workload_increase_pct }
    }
    if (scenarioDef.restructured_team) {
      return { scenario_type: 'team_restructuring', restructure_team: scenarioDef.restructured_team }
    }
    if (scenarioDef.removed && scenarioDef.removed.length > 0) {
      return { scenario_type: 'attrition', removed_employees: scenarioDef.removed }
    }
    return { scenario_type: 'attrition', removed_employees: [] }
  }

  async function handleRunScenario() {
    if (!selectedScenario) {
      setError('Select a scenario first')
      return
    }
    setLoadingScenario(true)
    setError('')
    setScenarioResult(null)
    try {
      const body = { ...getScenarioBody(selectedScenario), reaction_type: selectedReaction, probability }
      const r = await postScenarioRun(body)
      setScenarioResult(r)
    } catch (err) {
      setError('Scenario failed: ' + err.message)
    }
    setLoadingScenario(false)
  }

  function randomScenario() {
    if (!scenarios?.categories) return
    const cats = Object.values(scenarios.categories)
    const cat = cats[Math.floor(Math.random() * cats.length)]
    const s = cat.scenarios[Math.floor(Math.random() * cat.scenarios.length)]
    setSelectedScenario(s)
    if (s.probability) setProbability(s.probability)
  }

  function randomReaction() {
    if (!reactions?.reactions) return
    const r = reactions.reactions[Math.floor(Math.random() * reactions.reactions.length)]
    setSelectedReaction(r.id)
  }

  function randomBoth() {
    randomScenario()
    randomReaction()
    setProbability(Math.floor(Math.random() * 81) + 10)
  }

  const isActive = datasetInfo?.active

  function deltaColor(delta) {
    if (delta > 0) return 'text-green-600'
    if (delta < 0) return 'text-red-600'
    return 'text-gray-600'
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Data Source & Scenarios</h1>
      <p className="text-gray-500 text-sm">
        Three modes supported. Toggle between <b>Default CSVs</b> (pre-loaded 115 employees),
        <b> Uploaded Files</b> (your own data), or <b>Scenario Explorer</b> (predefined permutations).
      </p>

      {/* Mode Selector — Three Cards */}
      <div className="grid grid-cols-3 gap-3">
        <button onClick={() => { setMode('default'); handleClear() }}
          className={`p-4 rounded-xl border-2 text-left transition-all ${
            mode === 'default' ? 'border-tru-500 bg-tru-50 ring-2 ring-tru-200' : 'border-gray-200 bg-white hover:border-gray-300'
          }`}>
          <p className="text-sm font-bold text-gray-800">Default Dataset</p>
          <p className="text-xs text-gray-500 mt-1">115 employees across 14 teams</p>
          <p className="text-xs text-gray-400">Pre-loaded analytics</p>
          {mode === 'default' && <p className="text-xs text-tru-600 font-medium mt-1">Active</p>}
        </button>
        <button onClick={() => { setMode('upload'); document.getElementById('file-input')?.click() }}
          className={`p-4 rounded-xl border-2 text-left transition-all ${
            mode === 'upload' ? 'border-tru-500 bg-tru-50 ring-2 ring-tru-200' : 'border-gray-200 bg-white hover:border-gray-300'
          }`}>
          <p className="text-sm font-bold text-gray-800">Uploaded File</p>
          <p className="text-xs text-gray-500 mt-1">CSV &middot; XLSX &middot; TXT &middot; DOCX</p>
          <p className="text-xs text-gray-400">Auto-detect columns</p>
          {mode === 'upload' && datasetInfo?.active && <p className="text-xs text-tru-600 font-medium mt-1">Active: {datasetInfo?.filename}</p>}
        </button>
        <button onClick={() => { setMode('scenario'); setFile(null); setPreview(null) }}
          className={`p-4 rounded-xl border-2 text-left transition-all ${
            mode === 'scenario' ? 'border-tru-500 bg-tru-50 ring-2 ring-tru-200' : 'border-gray-200 bg-white hover:border-gray-300'
          }`}>
          <p className="text-sm font-bold text-gray-800">Scenario Explorer</p>
          <p className="text-xs text-gray-500 mt-1">20+ predefined permutations</p>
          <p className="text-xs text-gray-400">Profit &middot; Loss &middot; Break-even &middot; SPOF</p>
          {mode === 'scenario' && <p className="text-xs text-tru-600 font-medium mt-1">Browse scenarios</p>}
        </button>
      </div>

      {/* Active Dataset Banner */}
      {mode !== 'scenario' && (isActive ? (
        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-green-800">Active Dataset: {datasetInfo.filename}</p>
              <p className="text-xs text-green-600 mt-1">
                {datasetInfo.employee_count} employees across {datasetInfo.team_count} teams
              </p>
            </div>
            <button onClick={handleClear} className="text-xs text-red-600 hover:text-red-800 px-3 py-1 border border-red-200 rounded">Reset</button>
          </div>
        </div>
      ) : (
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm font-medium text-blue-800">Using Default Dataset</p>
          <p className="text-xs text-blue-600 mt-1">115 employees &middot; 14 teams &middot; Composite: {scenarios?.org_health_baseline || '...'}/100 (HIGH Risk)</p>
        </div>
      ))}

      {/* MODE: SCENARIO EXPLORER — Two-axis system */}
      {mode === 'scenario' && (
        <div className="space-y-4">
          <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
            <p className="text-sm font-medium text-purple-800">Scenario Explorer — Two-Axis System</p>
            <p className="text-xs text-purple-600 mt-1">
              Choose a <b>Scenario</b> (what happens) and a <b>Reaction</b> (how it's analyzed). These two dimensions are
              independently permutable — any scenario can pair with any reaction type. Use <b>Randomize</b> for
              exploratory analysis, or make deliberate selections for targeted insights. Results link to
              <b> What-If</b> (scenario view) and <b>AI Human Interaction</b> (reaction view) modes.
            </p>
          </div>

          {/* Three-panel layout */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Left: Scenario Selection */}
            <div className="bg-white border rounded-lg">
              <div className="flex items-center justify-between p-3 border-b bg-gray-50">
                <div>
                  <p className="text-sm font-bold text-gray-800">Step 1: Scenario</p>
                  <p className="text-xs text-gray-500">What happens?</p>
                </div>
                <button onClick={randomScenario} className="text-xs px-3 py-1.5 border border-gray-300 rounded-lg hover:bg-gray-100">
                  Randomize
                </button>
              </div>

              {scenarios && scenarios.categories ? (
                <div className="divide-y max-h-[420px] overflow-y-auto">
                  {Object.entries(scenarios.categories).map(([catKey, cat]) => (
                    <div key={catKey}>
                      <button
                        onClick={() => setExpandedCategory(expandedCategory === catKey ? null : catKey)}
                        className="w-full flex items-center justify-between p-2.5 hover:bg-gray-50 text-left"
                      >
                        <div>
                          <p className="text-xs font-semibold text-gray-700">{cat.description}</p>
                          <p className="text-xs text-gray-400">{cat.scenarios.length} scenarios</p>
                        </div>
                        <span className={`text-gray-400 text-xs transition-transform ${expandedCategory === catKey ? 'rotate-180' : ''}`}>▼</span>
                      </button>

                      {expandedCategory === catKey && (
                        <div className="bg-gray-50 border-t divide-y">
                          {cat.scenarios.map((s, i) => (
                            <button
                              key={i}
                              onClick={() => { setSelectedScenario(s); if (s.probability) setProbability(s.probability) }}
                              className={`w-full text-left p-2.5 hover:bg-white transition-colors ${
                                selectedScenario?.name === s.name ? 'bg-tru-50 border-l-2 border-tru-500' : ''
                              }`}
                            >
                              <div className="flex items-center gap-2">
                                <div className={`w-3 h-3 rounded-full border-2 flex-shrink-0 ${
                                  selectedScenario?.name === s.name ? 'border-tru-500 bg-tru-500' : 'border-gray-300'
                                }`} />
                                <div className="flex-1 min-w-0">
                                  <p className="text-xs font-medium text-gray-800 truncate">{s.name}</p>
                                  <div className="flex gap-2 text-xs text-gray-400 mt-0.5 flex-wrap">
                                    {s.probability !== undefined && (
                                      <span className={s.probability >= 50 ? 'text-orange-500' : s.probability >= 25 ? 'text-yellow-600' : 'text-green-600'}>
                                        p:{s.probability}%
                                      </span>
                                    )}
                                    {s.projected_composite !== undefined && (
                                      <span>d:{s.delta > 0 ? '+' : ''}{s.delta}</span>
                                    )}
                                    {s.expected_delta !== undefined && (
                                      <span className="text-gray-500">e:{s.expected_delta > 0 ? '+' : ''}{s.expected_delta}</span>
                                    )}
                                    {s.revenue_at_risk_usd > 0 && (
                                      <span>${(s.revenue_at_risk_usd / 1000000).toFixed(1)}M</span>
                                    )}
                                    {s.workload_increase_pct && <span>+{s.workload_increase_pct}%</span>}
                                    {s.restructured_team && <span>{s.restructured_team}</span>}
                                  </div>
                                </div>
                              </div>
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-6 text-center text-xs text-gray-400">Loading scenarios...</div>
              )}
            </div>

            {/* Middle: Reaction Selection */}
            <div className="bg-white border rounded-lg">
              <div className="flex items-center justify-between p-3 border-b bg-gray-50">
                <div>
                  <p className="text-sm font-bold text-gray-800">Step 2: Reaction</p>
                  <p className="text-xs text-gray-500">How is it analyzed?</p>
                </div>
                <button onClick={randomReaction} className="text-xs px-3 py-1.5 border border-gray-300 rounded-lg hover:bg-gray-100">
                  Randomize
                </button>
              </div>

              <div className="p-3 space-y-2">
                {reactions && reactions.reactions ? (
                  reactions.reactions.map((r) => (
                    <button
                      key={r.id}
                      onClick={() => setSelectedReaction(r.id)}
                      className={`w-full text-left p-3 rounded-lg border transition-all ${
                        selectedReaction === r.id
                          ? 'border-tru-500 bg-tru-50 ring-1 ring-tru-200'
                          : 'border-gray-200 hover:border-gray-300 bg-white'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <div className={`w-3 h-3 rounded-full border-2 flex-shrink-0 ${
                          selectedReaction === r.id ? 'border-tru-500 bg-tru-500' : 'border-gray-300'
                        }`} />
                        <div>
                          <p className="text-sm font-medium text-gray-800">{r.name}</p>
                          <p className="text-xs text-gray-500 mt-0.5">{r.description}</p>
                        </div>
                      </div>
                    </button>
                  ))
                ) : (
                  <div className="text-center text-xs text-gray-400 py-4">Loading reactions...</div>
                )}
              </div>
            </div>

            {/* Right: Probability Selection */}
            <div className="bg-white border rounded-lg">
              <div className="flex items-center justify-between p-3 border-b bg-gray-50">
                <div>
                  <p className="text-sm font-bold text-gray-800">Step 3: Probability</p>
                  <p className="text-xs text-gray-500">How likely is it?</p>
                </div>
                <button onClick={() => { const r = Math.floor(Math.random() * 81) + 10; setProbability(r) }} className="text-xs px-3 py-1.5 border border-gray-300 rounded-lg hover:bg-gray-100">
                  Randomize
                </button>
              </div>

              <div className="p-4 space-y-4">
                {/* Probability meter */}
                <div className="text-center">
                  <div className={`text-5xl font-bold ${probability >= 70 ? 'text-red-500' : probability >= 40 ? 'text-orange-500' : 'text-green-500'}`}>
                    {probability}%
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {probability >= 70 ? 'High likelihood — urgent attention' :
                     probability >= 40 ? 'Moderate likelihood — monitor' :
                     'Low likelihood — low priority'}
                  </p>
                </div>

                {/* Slider */}
                <div>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={probability}
                    onChange={(e) => setProbability(Number(e.target.value))}
                    className="w-full h-2 rounded-lg appearance-none cursor-pointer"
                    style={{
                      background: `linear-gradient(to right, 
                        ${probability >= 70 ? '#dc2626' : probability >= 40 ? '#ea580c' : '#16a34a'} 
                        ${probability}%, #e5e7eb ${probability}%)`
                    }}
                  />
                  <div className="flex justify-between text-xs text-gray-400 mt-1">
                    <span>0%</span>
                    <span>25%</span>
                    <span>50%</span>
                    <span>75%</span>
                    <span>100%</span>
                  </div>
                </div>

                {/* Quick probability presets */}
                <div>
                  <p className="text-xs text-gray-500 mb-2 font-medium">Quick presets:</p>
                  <div className="grid grid-cols-3 gap-2">
                    <button onClick={() => setProbability(25)} className={`text-xs py-1.5 rounded border ${probability === 25 ? 'border-green-500 bg-green-50 text-green-700' : 'border-gray-200 hover:bg-gray-50 text-gray-600'}`}>
                      25% Low
                    </button>
                    <button onClick={() => setProbability(50)} className={`text-xs py-1.5 rounded border ${probability === 50 ? 'border-orange-500 bg-orange-50 text-orange-700' : 'border-gray-200 hover:bg-gray-50 text-gray-600'}`}>
                      50% Medium
                    </button>
                    <button onClick={() => setProbability(75)} className={`text-xs py-1.5 rounded border ${probability === 75 ? 'border-red-500 bg-red-50 text-red-700' : 'border-gray-200 hover:bg-gray-50 text-gray-600'}`}>
                      75% High
                    </button>
                  </div>
                </div>

                {/* Expected impact preview */}
                {selectedScenario && selectedScenario.delta !== undefined && (
                  <div className="p-2.5 bg-gray-50 rounded-lg text-xs">
                    <p className="text-gray-500">Expected impact preview:</p>
                    <p className="font-medium text-gray-800 mt-1">
                      d: {selectedScenario.delta > 0 ? '+' : ''}{selectedScenario.delta} × p:{probability}%
                      = <span className={selectedScenario.delta < 0 ? 'text-red-600' : 'text-green-600'}>
                        {(selectedScenario.delta * probability / 100) > 0 ? '+' : ''}
                        {(selectedScenario.delta * probability / 100).toFixed(1)}
                      </span>
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Selected summary bar */}
          <div className="flex items-center justify-between p-3 bg-white border rounded-lg">
            <div className="flex items-center gap-4 text-sm">
              <div>
                <span className="text-gray-500 text-xs">Scenario:</span>
                <p className="font-medium text-gray-800">{selectedScenario?.name || 'None selected'}</p>
              </div>
              <div className="w-px h-8 bg-gray-200" />
              <div>
                <span className="text-gray-500 text-xs">Reaction:</span>
                <p className="font-medium text-gray-800 capitalize">{selectedReaction.replace(/_/g, ' ')}</p>
              </div>
              <div className="w-px h-8 bg-gray-200" />
              <div>
                <span className="text-gray-500 text-xs">Probability:</span>
                <p className={`font-medium ${probability >= 70 ? 'text-red-600' : probability >= 40 ? 'text-orange-600' : 'text-green-600'}`}>
                  {probability}%
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button onClick={randomBoth} className="text-xs px-3 py-1.5 border border-gray-300 rounded-lg hover:bg-gray-100">
                Randomize All
              </button>
              <button
                onClick={handleRunScenario}
                disabled={loadingScenario || !selectedScenario}
                className="text-sm px-5 py-2 bg-tru-600 text-white rounded-lg font-medium hover:bg-tru-700 disabled:opacity-50"
              >
                {loadingScenario ? 'Running...' : 'Run Scenario'}
              </button>
            </div>
          </div>

          {/* Scenario Result */}
          {scenarioResult && (
            <div className="bg-white border border-purple-200 rounded-lg overflow-hidden">
              <div className="flex items-center justify-between p-3 bg-purple-50 border-b border-purple-200">
                <div>
                  <h3 className="text-sm font-bold text-purple-800">Result: {scenarioResult.reaction_type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</h3>
                  <p className="text-xs text-purple-600 mt-0.5">{selectedScenario?.name}</p>
                </div>
              </div>

              {/* Numerical impact (always present) */}
              <div className="p-3 border-b">
                <p className="text-xs font-semibold text-gray-600 mb-2 uppercase tracking-wide">Numerical Impact</p>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="p-2.5 bg-gray-50 rounded-lg text-center">
                    <p className="text-xs text-gray-500">Baseline</p>
                    <p className="text-lg font-bold">{scenarioResult.baseline?.composite_score || '-'}</p>
                  </div>
                  <div className="p-2.5 bg-gray-50 rounded-lg text-center">
                    <p className="text-xs text-gray-500">Projected</p>
                    <p className={`text-lg font-bold ${deltaColor(scenarioResult.comparison?.composite_delta || 0)}`}>{scenarioResult.projected?.composite_score || '-'}</p>
                  </div>
                  <div className="p-2.5 bg-gray-50 rounded-lg text-center">
                    <p className="text-xs text-gray-500">Delta</p>
                    <p className={`text-lg font-bold ${deltaColor(scenarioResult.comparison?.composite_delta || 0)}`}>
                      {scenarioResult.comparison?.composite_delta > 0 ? '+' : ''}{scenarioResult.comparison?.composite_delta || 0}
                    </p>
                  </div>
                  <div className="p-2.5 bg-gray-50 rounded-lg text-center">
                    <p className="text-xs text-gray-500">Revenue at Risk</p>
                    <p className="text-lg font-bold text-red-600">${(scenarioResult.comparison?.revenue_at_risk_usd || 0).toLocaleString()}</p>
                  </div>
                </div>
                {scenarioResult.comparison?.indicator_deltas && (
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-2">
                    {Object.entries(scenarioResult.comparison.indicator_deltas).map(([key, val]) => (
                      <div key={key} className="flex items-center justify-between text-xs p-1.5 bg-gray-50 rounded">
                        <span className="capitalize text-gray-600">{key}</span>
                        <span className={deltaColor(val.delta)}>{val.delta > 0 ? '+' : ''}{val.delta}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Probability-Weighted Impact */}
              {scenarioResult.probability !== undefined && (
                <div className="p-3 border-b bg-gradient-to-r from-purple-50 to-blue-50">
                  <p className="text-xs font-semibold text-gray-600 mb-2 uppercase tracking-wide">
                    Probability-Weighted Impact — p = {scenarioResult.probability}%
                  </p>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div className="p-2.5 bg-white/80 rounded-lg text-center">
                      <p className="text-xs text-gray-500">Expected Delta</p>
                      <p className={`text-lg font-bold ${deltaColor(scenarioResult.expected_delta || 0)}`}>
                        {scenarioResult.expected_delta > 0 ? '+' : ''}{scenarioResult.expected_delta || 0}
                      </p>
                    </div>
                    <div className="p-2.5 bg-white/80 rounded-lg text-center">
                      <p className="text-xs text-gray-500">Expected Revenue Loss</p>
                      <p className="text-lg font-bold text-red-600">${(scenarioResult.expected_revenue_loss || 0).toLocaleString()}</p>
                    </div>
                    <div className="p-2.5 bg-white/80 rounded-lg text-center">
                      <p className="text-xs text-gray-500">Risk-Weighted Score</p>
                      <p className={`text-lg font-bold ${deltaColor(scenarioResult.risk_weighted_score !== undefined ? scenarioResult.risk_weighted_score - (scenarioResult.baseline?.composite_score || 0) : 0)}`}>
                        {scenarioResult.risk_weighted_score ?? '-'}
                      </p>
                    </div>
                    <div className="p-2.5 bg-white/80 rounded-lg text-center">
                      <p className="text-xs text-gray-500">Probability</p>
                      <p className={`text-lg font-bold ${scenarioResult.probability >= 70 ? 'text-red-500' : scenarioResult.probability >= 40 ? 'text-orange-500' : 'text-green-500'}`}>
                        {scenarioResult.probability}%
                      </p>
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 mt-2 text-center">
                    Expected values = raw impact × (probability / 100). Risk-weighted score = baseline + expected delta.
                  </p>
                </div>
              )}

              {/* Pipeline analysis */}
              {scenarioResult.pipeline && (
                <div className="p-3 border-b">
                  <p className="text-xs font-semibold text-gray-600 mb-2 uppercase tracking-wide">AI Analysis</p>
                  <div className="space-y-2 text-xs">
                    <div className="p-2 bg-blue-50 rounded">
                      <p className="font-medium text-blue-800">{scenarioResult.pipeline.summary?.insight?.headline}</p>
                    </div>
                    {scenarioResult.pipeline.summary?.risk?.critical_spofs?.length > 0 && (
                      <div>
                        <p className="font-medium text-gray-700 mb-1">Critical SPOFs:</p>
                        <ul className="space-y-1">
                          {scenarioResult.pipeline.summary.risk.critical_spofs.slice(0, 3).map((spof, i) => (
                            <li key={i} className="p-1.5 bg-gray-50 rounded text-gray-600">{spof.employee} — {spof.why}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {scenarioResult.pipeline.summary?.simulation?.narrative && (
                      <div className="p-2 bg-orange-50 rounded text-gray-700">
                        {scenarioResult.pipeline.summary.simulation.narrative}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Human decisions */}
              {scenarioResult.human_decisions && (
                <div className="p-3 border-b">
                  <p className="text-xs font-semibold text-gray-600 mb-2 uppercase tracking-wide">Human-in-the-Loop Decisions</p>
                  <div className="space-y-1.5">
                    {scenarioResult.human_decisions.map((d, i) => (
                      <div key={i} className="flex items-center justify-between p-2 bg-gray-50 rounded text-xs">
                        <div className="flex-1">
                          <p className="font-medium text-gray-700">{d.action_title}</p>
                          <p className="text-gray-500 mt-0.5">{d.reason}</p>
                        </div>
                        <span className={`ml-2 px-2 py-0.5 rounded text-xs font-medium ${
                          d.decision === 'accept' ? 'bg-green-100 text-green-700' :
                          d.decision === 'veto' ? 'bg-red-100 text-red-700' :
                          'bg-yellow-100 text-yellow-700'
                        }`}>
                          {d.decision}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Agent suggestions */}
              {scenarioResult.agent_suggestions && (
                <div className="p-3 border-b">
                  <p className="text-xs font-semibold text-gray-600 mb-2 uppercase tracking-wide">Agent Intervention — Mitigation Suggestions</p>
                  <div className="space-y-1.5">
                    {scenarioResult.agent_suggestions.map((s, i) => (
                      <div key={i} className="p-2 bg-gray-50 rounded text-xs">
                        <div className="flex items-center justify-between">
                          <p className="font-medium text-gray-700">{s.title}</p>
                          <span className="text-gray-400">${s.estimated_cost_usd?.toLocaleString()}</span>
                        </div>
                        <p className="text-gray-500 mt-0.5">{s.rationale}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Navigation links */}
              <div className="flex gap-2 p-3 bg-gray-50">
                <Link to="/whatif" className="text-xs px-4 py-2 bg-tru-600 text-white rounded-lg hover:bg-tru-700">
                  View in What-If
                </Link>
                <Link to="/feedback" className="text-xs px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
                  View in AI Human Interaction
                </Link>
                <button onClick={handleRunScenario} className="text-xs px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 ml-auto">
                  Re-run
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* MODE: UPLOAD */}
      {mode === 'upload' && (
        <>
          <div
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            onClick={() => inputRef.current?.click()}
            className="border-2 border-dashed border-gray-300 rounded-xl p-10 text-center cursor-pointer hover:border-tru-500 transition-colors"
          >
            <input ref={inputRef} id="file-input" type="file" accept=".csv,.xlsx,.txt,.docx" onChange={handleSelect} className="hidden" />
            <p className="text-gray-500 text-sm">{file ? file.name : 'Drop your file here or click to browse'}</p>
            <p className="text-gray-400 text-xs mt-1">Supports CSV, XLSX, TXT, and DOCX files</p>
          </div>

          {preview && (
            <div className="bg-white border rounded-lg p-4 space-y-3">
              <h3 className="text-sm font-semibold text-gray-700">Preview & Column Mapping</h3>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div><span className="text-gray-500">Rows:</span> {preview.row_count}</div>
                <div><span className="text-gray-500">Columns:</span> {preview.column_count}</div>
              </div>
              {preview.suggested_mapping && Object.keys(preview.suggested_mapping).length > 0 && (
                <div>
                  <p className="text-xs font-medium text-gray-600 mb-1">Auto-Detected Column Mapping:</p>
                  <table className="w-full text-xs border-collapse">
                    <thead><tr className="bg-gray-50">
                      <th className="border p-1 text-left text-gray-600">Field</th>
                      <th className="border p-1 text-left text-gray-600">Mapped Column</th>
                    </tr></thead>
                    <tbody>{Object.entries(preview.suggested_mapping).map(([field, col]) => (
                      <tr key={field}><td className="border p-1 font-medium">{field}</td><td className="border p-1 text-tru-600">{col}</td></tr>
                    ))}</tbody>
                  </table>
                </div>
              )}
              <button onClick={handleUpload} disabled={uploading}
                className="w-full py-2 bg-tru-600 text-white rounded-lg text-sm font-medium hover:bg-tru-700 disabled:opacity-50">
                {uploading ? 'Uploading & Activating...' : `Upload & Activate "${file?.name}"`}
              </button>
            </div>
          )}
        </>
      )}

      {/* Error */}
      {error && <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{error}</div>}

      {/* Result */}
      {result && mode !== 'scenario' && (
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg space-y-2">
          <p className="text-sm font-medium text-blue-800">{result.message || 'Dataset activated'}</p>
          {result.activation?.employee_count && <p className="text-xs text-blue-600">{result.activation.employee_count} employees loaded</p>}
        </div>
      )}

      {/* Previously Uploaded Files */}
      {mode === 'upload' && uploadedFiles.length > 0 && (
        <div className="bg-white border rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Previously Uploaded Files</h3>
          <div className="space-y-2">
            {uploadedFiles.map((f) => (
              <div key={f.filename} className="flex items-center justify-between p-2 bg-gray-50 rounded text-sm">
                <div><span className="font-medium text-gray-700">{f.filename}</span><span className="text-gray-400 ml-2">({(f.size_bytes / 1024).toFixed(1)} KB)</span></div>
                <button onClick={() => handleActivate(f.filename)} className="text-xs text-tru-600 hover:text-tru-800 px-3 py-1 border border-tru-200 rounded">Activate</button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
