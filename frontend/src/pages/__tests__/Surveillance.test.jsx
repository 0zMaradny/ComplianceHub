import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import '../../i18n'
import Surveillance from '../Surveillance'

const mockFetch = vi.fn()
globalThis.fetch = mockFetch

const API = '/api'

const cyclesResponse = {
  cycles: [
    { id: 1, project_id: 10, cycle_number: 1, scheduled_date: '2026-06-15', status: 'scheduled' },
    { id: 2, project_id: 20, cycle_number: 2, scheduled_date: '2026-04-01', status: 'completed' },
  ],
}

const projectsResponse = {
  projects: [
    { id: 10, title: 'Acme Corp' },
    { id: 20, title: 'Beta Inc' },
  ],
}

const dashboardResponse = {
  total_cycles: 2,
  upcoming_30d: 1,
  overdue: 0,
  completed: 1,
}

beforeEach(() => {
  mockFetch.mockReset()
})

describe('Surveillance', () => {
  it('shows loading state initially', () => {
    mockFetch.mockResolvedValue({ json: async () => cyclesResponse })
    render(<Surveillance API={API} />)
    expect(screen.getByText('Surveillance & Recertification')).toBeInTheDocument()
  })

  it('renders cycles list after loading', async () => {
    mockFetch
      .mockResolvedValueOnce({ json: async () => cyclesResponse })
      .mockResolvedValueOnce({ json: async () => projectsResponse })
      .mockResolvedValueOnce({ json: async () => dashboardResponse })
    render(<Surveillance API={API} />)
    const acme = await screen.findAllByText(/Acme Corp/)
    expect(acme.length).toBeGreaterThanOrEqual(1)
    const beta = await screen.findAllByText(/Beta Inc/)
    expect(beta.length).toBeGreaterThanOrEqual(1)
  })

  it('shows stat cards', async () => {
    mockFetch
      .mockResolvedValueOnce({ json: async () => cyclesResponse })
      .mockResolvedValueOnce({ json: async () => projectsResponse })
      .mockResolvedValueOnce({ json: async () => dashboardResponse })
    render(<Surveillance API={API} />)
    expect(await screen.findByText('2')).toBeInTheDocument()
  })

  it('shows empty state when no cycles', async () => {
    mockFetch
      .mockResolvedValueOnce({ json: async () => ({ cycles: [] }) })
      .mockResolvedValueOnce({ json: async () => ({ projects: [] }) })
      .mockResolvedValueOnce({ json: async () => ({}) })
    render(<Surveillance API={API} />)
    expect(await screen.findByText('No surveillance cycles yet')).toBeInTheDocument()
  })

  it('shows check overdue button', async () => {
    mockFetch
      .mockResolvedValueOnce({ json: async () => cyclesResponse })
      .mockResolvedValueOnce({ json: async () => projectsResponse })
      .mockResolvedValueOnce({ json: async () => dashboardResponse })
    render(<Surveillance API={API} />)
    expect(await screen.findByText('⚠ Check Overdue')).toBeInTheDocument()
  })

  it('shows auto-schedule section', async () => {
    mockFetch
      .mockResolvedValueOnce({ json: async () => cyclesResponse })
      .mockResolvedValueOnce({ json: async () => projectsResponse })
      .mockResolvedValueOnce({ json: async () => dashboardResponse })
    render(<Surveillance API={API} />)
    expect(await screen.findByText('Auto-Schedule Surveillance')).toBeInTheDocument()
  })
})
