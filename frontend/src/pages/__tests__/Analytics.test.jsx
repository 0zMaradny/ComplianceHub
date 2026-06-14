import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import '../../i18n'
import Analytics from '../Analytics'

const mockFetch = vi.fn()
globalThis.fetch = mockFetch

const API = '/api'

const trendsData = {
  months: ['2026-01', '2026-02', '2026-03'],
  major_nc: [2, 1, 0],
  minor_nc: [5, 3, 2],
  ofi: [3, 2, 1],
  closed: [4, 3, 2],
  recurring_rate_pct: [10, 8, 5],
}

const healthData = {
  projects: [
    { id: 1, title: 'Acme Corp', client: 'Acme', healthScore: 85, open_ncs: 1, pending_capas: 0, current_gate: 3, days_in_gate: 45 },
    { id: 2, title: 'Beta Inc', client: 'Beta', healthScore: 42, open_ncs: 4, pending_capas: 2, current_gate: 2, days_in_gate: 120 },
  ],
}

const capaData = {
  total_capas: 15,
  closure_rate_pct: 73,
  avg_closure_days: 28,
  overdue_count: 2,
  by_status: { Open: 5, Closed: 10 },
  avg_days_by_severity: { Major: 35, Minor: 22 },
}

const modelsData = {
  models: [
    { name: 'Nemotron-3-550B', total_uses: 120, healthy: true, tier_category: 'Frontier', avg_quality_score: 92, avg_response_time_ms: 1800 },
    { name: 'Groq-Llama', total_uses: 45, healthy: true, tier_category: 'Fast', avg_quality_score: 85, avg_response_time_ms: 340 },
  ],
  recommended_for: { 'clause_check': 'Nemotron-3-550B' },
}

beforeEach(() => {
  mockFetch.mockReset()
})

describe('Analytics', () => {
  it('shows loading skeleton initially', () => {
    mockFetch.mockResolvedValue({ json: async () => null })
    const { container } = render(<Analytics API={API} />)
    expect(container.querySelector('.animate-fadeIn')).toBeInTheDocument()
  })

  it('renders nc trends chart after loading', async () => {
    mockFetch
      .mockResolvedValueOnce({ json: async () => trendsData })
      .mockResolvedValueOnce({ json: async () => healthData })
      .mockResolvedValueOnce({ json: async () => modelsData })
      .mockResolvedValueOnce({ json: async () => capaData })
      .mockResolvedValueOnce({ json: async () => modelsData })
    render(<Analytics API={API} />)
    expect(await screen.findByText('2026-01')).toBeInTheDocument()
    expect(await screen.findByText('2026-02')).toBeInTheDocument()
    expect(await screen.findByText('2026-03')).toBeInTheDocument()
  })

  it('shows empty nc trends fallback', async () => {
    mockFetch
      .mockResolvedValueOnce({ json: async () => null })
      .mockResolvedValueOnce({ json: async () => healthData })
      .mockResolvedValueOnce({ json: async () => modelsData })
      .mockResolvedValueOnce({ json: async () => capaData })
      .mockResolvedValueOnce({ json: async () => modelsData })
    render(<Analytics API={API} />)
    expect(await screen.findByText('No NC data yet')).toBeInTheDocument()
  })

  it('shows empty project health fallback', async () => {
    mockFetch
      .mockResolvedValueOnce({ json: async () => trendsData })
      .mockResolvedValueOnce({ json: async () => ({ projects: [] }) })
      .mockResolvedValueOnce({ json: async () => modelsData })
      .mockResolvedValueOnce({ json: async () => capaData })
      .mockResolvedValueOnce({ json: async () => modelsData })
    render(<Analytics API={API} />)
    expect(await screen.findByText('No active projects')).toBeInTheDocument()
  })

  it('shows capa metrics after loading', async () => {
    mockFetch
      .mockResolvedValueOnce({ json: async () => trendsData })
      .mockResolvedValueOnce({ json: async () => healthData })
      .mockResolvedValueOnce({ json: async () => modelsData })
      .mockResolvedValueOnce({ json: async () => capaData })
      .mockResolvedValueOnce({ json: async () => modelsData })
    render(<Analytics API={API} />)
    const total15 = await screen.findAllByText('15')
    expect(total15.length).toBeGreaterThanOrEqual(1)
    expect(await screen.findByText('73%')).toBeInTheDocument()
  })

  it('shows ai usage models', async () => {
    mockFetch
      .mockResolvedValueOnce({ json: async () => trendsData })
      .mockResolvedValueOnce({ json: async () => healthData })
      .mockResolvedValueOnce({ json: async () => modelsData })
      .mockResolvedValueOnce({ json: async () => capaData })
      .mockResolvedValueOnce({ json: async () => modelsData })
    render(<Analytics API={API} />)
    const nemo = await screen.findAllByText('Nemotron-3-550B')
    expect(nemo.length).toBeGreaterThanOrEqual(1)
    const groq = await screen.findAllByText('Groq-Llama')
    expect(groq.length).toBeGreaterThanOrEqual(1)
  })
})
