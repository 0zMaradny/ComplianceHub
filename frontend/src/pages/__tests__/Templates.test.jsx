import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ToastProvider } from '../../components/Toast'
import Templates from '../Templates'

const mockFetch = vi.fn()
globalThis.fetch = mockFetch

const API = '/api'

const emptyTemplates = {
  document_templates: [],
  checklist_templates: [],
}

const Wrapper = ({ children }) => <ToastProvider>{children}</ToastProvider>

beforeEach(() => {
  mockFetch.mockReset()
})

describe('Templates', () => {
  it('renders page header', async () => {
    mockFetch.mockResolvedValue({ json: async () => emptyTemplates })
    render(<Templates API={API} />, { wrapper: Wrapper })
    const header = await screen.findByText('Template Manager')
    expect(header).toBeInTheDocument()
  })
})
