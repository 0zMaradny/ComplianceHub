import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'

describe('App', () => {
  it('renders without crashing', () => {
    const { container } = render(<App />)
    expect(container).toBeInTheDocument()
  })

  it('shows ComplianceHub title', () => {
    render(<App />)
    expect(screen.getByText('ComplianceHub')).toBeInTheDocument()
  })

  it('renders all nav items', () => {
    render(<App />)
    expect(screen.getAllByText('Dashboard').length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText('Audit Generator')).toBeInTheDocument()
    expect(screen.getByText('History')).toBeInTheDocument()
    expect(screen.getByText('Compliance')).toBeInTheDocument()
    expect(screen.getByText('Projects')).toBeInTheDocument()
  })
})
