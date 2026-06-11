import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import Projects from '../Projects'

const mockFetch = vi.fn()
global.fetch = mockFetch

const API = '/api'

beforeEach(() => {
  mockFetch.mockReset()
})

describe('Projects', () => {
  it('renders page header', () => {
    mockFetch.mockResolvedValue({ json: async () => ({}) })
    render(<Projects API={API} />)
    expect(screen.getByText('Audit Projects')).toBeInTheDocument()
  })

  it('shows new project button', async () => {
    mockFetch.mockResolvedValue({ json: async () => ({}) })
    render(<Projects API={API} />)
    const btn = await screen.findByText('+ New Project')
    expect(btn).toBeInTheDocument()
  })
})
