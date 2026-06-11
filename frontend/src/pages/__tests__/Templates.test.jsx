import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import Templates from '../Templates'

const mockFetch = vi.fn()
global.fetch = mockFetch

const API = '/api'

const emptyTemplates = {
  document_templates: [],
  checklist_templates: [],
}

beforeEach(() => {
  mockFetch.mockReset()
})

describe('Templates', () => {
  it('shows loading state initially', () => {
    mockFetch.mockResolvedValue({ json: async () => emptyTemplates })
    render(<Templates API={API} />)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders page header', async () => {
    mockFetch.mockResolvedValue({ json: async () => emptyTemplates })
    render(<Templates API={API} />)
    const header = await screen.findByText('Template Manager')
    expect(header).toBeInTheDocument()
  })
})
