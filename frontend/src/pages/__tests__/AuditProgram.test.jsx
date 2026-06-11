import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import AuditProgram from '../AuditProgram'

const mockFetch = vi.fn()
global.fetch = mockFetch

const API = '/api'

beforeEach(() => {
  mockFetch.mockReset()
})

describe('AuditProgram', () => {
  it('renders page header', async () => {
    mockFetch.mockResolvedValue({ json: async () => [] })
    render(<AuditProgram API={API} />)
    const header = await screen.findByText('Audit Programs')
    expect(header).toBeInTheDocument()
  })

  it('shows new program button', async () => {
    mockFetch.mockResolvedValue({ json: async () => [] })
    render(<AuditProgram API={API} />)
    const btn = await screen.findByText('+ New Audit Program')
    expect(btn).toBeInTheDocument()
  })
})
