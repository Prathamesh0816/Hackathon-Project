import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  getEmployees, getOrgHealth, getSkillGaps, getSpofRanking,
  postWhatIf, postFeedback, getReportHtml,
} from '../services/api'

const BASE = '/api'

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('API service - GET endpoints', () => {
  it('getEmployees fetches /employees', async () => {
    const fake = [{ Employee: 'Alice', Team: 'Engineering' }]
    globalThis.fetch = vi.fn().mockResolvedValue({ ok: true, json: () => fake })
    const result = await getEmployees()
    expect(globalThis.fetch).toHaveBeenCalledWith(`${BASE}/employees`)
    expect(result).toEqual(fake)
  })

  it('getOrgHealth fetches /org-health', async () => {
    const fake = { composite_score: 72 }
    globalThis.fetch = vi.fn().mockResolvedValue({ ok: true, json: () => fake })
    const result = await getOrgHealth()
    expect(globalThis.fetch).toHaveBeenCalledWith(`${BASE}/org-health`)
    expect(result.composite_score).toBe(72)
  })

  it('getSkillGaps fetches /skill-gaps', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({ ok: true, json: () => ({ teams: [] }) })
    await getSkillGaps()
    expect(globalThis.fetch).toHaveBeenCalledWith(`${BASE}/skill-gaps`)
  })

  it('getSpofRanking fetches /spof-ranking', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({ ok: true, json: () => ({ spofs: [] }) })
    await getSpofRanking()
    expect(globalThis.fetch).toHaveBeenCalledWith(`${BASE}/spof-ranking`)
  })

  it('throws on non-ok response', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({ ok: false, status: 500 })
    await expect(getEmployees()).rejects.toThrow('GET /employees failed: 500')
  })
})

describe('API service - POST endpoints', () => {
  it('postWhatIf sends body as JSON', async () => {
    const body = { scenario_type: 'attrition', removed_employees: ['Vikram'] }
    globalThis.fetch = vi.fn().mockResolvedValue({ ok: true, json: () => ({}) })
    await postWhatIf(body)
    expect(globalThis.fetch).toHaveBeenCalledWith(
      `${BASE}/whatif`,
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      }),
    )
  })

  it('postFeedback sends feedback body', async () => {
    const fb = { employee: 'Alice', action_title: 'Cross-train', decision: 'accept', reason: '' }
    globalThis.fetch = vi.fn().mockResolvedValue({ ok: true, json: () => ({}) })
    await postFeedback(fb)
    expect(globalThis.fetch).toHaveBeenCalledWith(
      `${BASE}/feedback`,
      expect.objectContaining({ method: 'POST', body: JSON.stringify(fb) }),
    )
  })
})

describe('API service - getReportHtml', () => {
  it('returns text response', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({ ok: true, text: () => '<html>report</html>' })
    const html = await getReportHtml('baseline', '')
    expect(globalThis.fetch).toHaveBeenCalledWith(`${BASE}/report?scenario_type=baseline&removed=`)
    expect(html).toBe('<html>report</html>')
  })
})
