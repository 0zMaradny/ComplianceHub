import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import Chat from '../Chat'

const mockFetch = vi.fn()
globalThis.fetch = mockFetch

const API = '/api'

beforeEach(() => {
  mockFetch.mockReset()
})

describe('Chat', () => {
  it('renders page header', () => {
    mockFetch.mockResolvedValue({ json: async () => ({ jobs: [] }) })
    render(<Chat API={API} />)
    expect(screen.getByText('AI Chat')).toBeInTheDocument()
  })

  it('shows empty state when no jobs', async () => {
    mockFetch.mockResolvedValue({ json: async () => ({ jobs: [] }) })
    render(<Chat API={API} />)
    const msg = await screen.findByText('No completed jobs found. Generate documents first.')
    expect(msg).toBeInTheDocument()
  })

  it('renders job select heading', async () => {
    mockFetch.mockResolvedValue({ json: async () => ({ jobs: [] }) })
    render(<Chat API={API} />)
    const heading = await screen.findByText('Select a Job')
    expect(heading).toBeInTheDocument()
  })
})
