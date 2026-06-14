import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ToastProvider } from '../../components/Toast'
import Projects from '../Projects'

const mockFetch = vi.fn()
globalThis.fetch = mockFetch

const API = '/api'

const Wrapper = ({ children }) => <ToastProvider>{children}</ToastProvider>

beforeEach(() => {
  mockFetch.mockReset()
})

describe('Projects', () => {
  it('renders page header', () => {
    mockFetch.mockResolvedValue({ json: async () => ({}) })
    render(<Projects API={API} />, { wrapper: Wrapper })
    expect(screen.getByText('Audit Projects')).toBeInTheDocument()
  })

  it('shows new project button', async () => {
    mockFetch.mockResolvedValue({ json: async () => ({}) })
    render(<Projects API={API} />, { wrapper: Wrapper })
    const btn = await screen.findByText('+ New Project')
    expect(btn).toBeInTheDocument()
  })
})
