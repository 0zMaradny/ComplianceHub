import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'
import { ToastProvider } from './components/Toast'

describe('App', () => {
  it('renders without crashing', () => {
    const { container } = render(<ToastProvider><App /></ToastProvider>)
    expect(container).toBeInTheDocument()
  })

  it('shows ComplianceHub title', () => {
    render(<ToastProvider><App /></ToastProvider>)
    expect(screen.getByText('ComplianceHub')).toBeInTheDocument()
  })

  it('renders all nav items', () => {
    render(<ToastProvider><App /></ToastProvider>)
    expect(screen.getAllByText('Dashboard').length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText('Audit Generator').length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText('History').length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText('Compliance').length).toBeGreaterThanOrEqual(1)
    expect(screen.getAllByText('Projects').length).toBeGreaterThanOrEqual(1)
  })
})
