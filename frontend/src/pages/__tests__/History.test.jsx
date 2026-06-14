import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import History from '../History'

const mockFetch = vi.fn()
globalThis.fetch = mockFetch

const API = '/api'

beforeEach(() => {
  mockFetch.mockReset()
})

describe('History', () => {
  it('renders page header', async () => {
    mockFetch.mockResolvedValue({ json: async () => ({ jobs: [] }) })
    render(<History API={API} />)
    const header = await screen.findByText('Job History')
    expect(header).toBeInTheDocument()
  })

  it('shows search input', async () => {
    mockFetch.mockResolvedValue({ json: async () => ({ jobs: [] }) })
    render(<History API={API} />)
    const input = await screen.findByPlaceholderText('Search jobs...')
    expect(input).toBeInTheDocument()
  })
})
