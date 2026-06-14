import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import '../../i18n'
import Reporting from '../Reporting'
import { ToastProvider } from '../../components/Toast'

const mockFetch = vi.fn()
globalThis.fetch = mockFetch

const API = '/api'

function renderWithToast(ui) {
  return render(<ToastProvider>{ui}</ToastProvider>)
}

beforeEach(() => {
  mockFetch.mockReset()
})

describe('Reporting', () => {
  it('renders page header', () => {
    mockFetch.mockResolvedValue({ json: async () => ({}) })
    renderWithToast(<Reporting API={API} />)
    expect(screen.getByText('Reporting')).toBeInTheDocument()
  })

  it('shows pdf report card', () => {
    mockFetch.mockResolvedValue({ json: async () => ({}) })
    renderWithToast(<Reporting API={API} />)
    expect(screen.getByText('PDF Summary Report')).toBeInTheDocument()
    expect(screen.getByText('Download PDF Report')).toBeInTheDocument()
  })

  it('shows csv export card', () => {
    mockFetch.mockResolvedValue({ json: async () => ({}) })
    renderWithToast(<Reporting API={API} />)
    expect(screen.getByText('CSV Data Export')).toBeInTheDocument()
    expect(screen.getByText('Download CSV')).toBeInTheDocument()
  })

  it('shows quick links card', () => {
    mockFetch.mockResolvedValue({ json: async () => ({}) })
    renderWithToast(<Reporting API={API} />)
    expect(screen.getByText('Quick Links')).toBeInTheDocument()
  })

  it('shows months input when nc_trends dataset selected', () => {
    mockFetch.mockResolvedValue({ json: async () => ({}) })
    renderWithToast(<Reporting API={API} />)
    const selects = screen.getAllByRole('combobox')
    const datasetSelect = selects[1]
    expect(datasetSelect).toBeInTheDocument()
  })
})
