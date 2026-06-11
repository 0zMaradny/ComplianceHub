import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import Dashboard from '../Dashboard'

const mockFetch = vi.fn()
global.fetch = mockFetch

const API = '/api'

const statsResponse = {
  total_jobs: 10, completed: 8, success_rate: 80, last_24h: 2,
  standards_used: { iso_9001: 5, iso_14001: 3 },
  cert_outcomes: { Certified: 6, Conditional: 2 },
}

const jobsResponse = { jobs: [{ job_id: 'abc123', status: 'done', created_at: 1000000 }] }
const standardsResponse = { standards: { iso_9001: 'ISO 9001:2015' } }

beforeEach(() => {
  mockFetch.mockReset()
})

describe('Dashboard', () => {
  it('shows loading state initially', () => {
    mockFetch.mockResolvedValue({ json: async () => ({}) })
    render(<Dashboard API={API} />)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders stats after fetch', async () => {
    mockFetch.mockResolvedValue({ json: async () => statsResponse })
    render(<Dashboard API={API} />)
    const total = await screen.findByText('10')
    expect(total).toBeInTheDocument()
  })

  it('renders page header', () => {
    mockFetch.mockResolvedValue({ json: async () => ({}) })
    render(<Dashboard API={API} />)
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })
})
