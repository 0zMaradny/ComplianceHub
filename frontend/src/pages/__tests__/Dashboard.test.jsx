import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import Dashboard from '../Dashboard'

const mockFetch = vi.fn()
globalThis.fetch = mockFetch

const API = '/api'

const statsResponse = {
  total_jobs: 10, completed: 8, success_rate: 80, last_24h: 2,
  standards_used: { iso_9001: 5, iso_14001: 3 },
  cert_outcomes: { Certified: 6, Conditional: 2 },
}

beforeEach(() => {
  mockFetch.mockReset()
})

describe('Dashboard', () => {
  it('shows loading state initially', () => {
    mockFetch.mockResolvedValue({ json: async () => ({}) })
    const { container } = render(<Dashboard API={API} />)
    expect(container.querySelector('.animate-fadeIn')).toBeInTheDocument()
  })

  it('renders stats after fetch', async () => {
    mockFetch.mockResolvedValue({ json: async () => statsResponse })
    render(<Dashboard API={API} />)
    const total = await screen.findByText('10')
    expect(total).toBeInTheDocument()
  })

  it('renders page header', async () => {
    mockFetch.mockResolvedValue({ json: async () => ({}) })
    render(<Dashboard API={API} />)
    const heading = await screen.findByText('Dashboard')
    expect(heading).toBeInTheDocument()
  })
})
