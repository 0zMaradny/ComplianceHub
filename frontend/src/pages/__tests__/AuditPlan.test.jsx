import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import AuditPlan from '../AuditPlan'

const API = '/api'

describe('AuditPlan', () => {
  it('renders form header', () => {
    render(<AuditPlan API={API} />)
    expect(screen.getByText('Audit Plan Generator')).toBeInTheDocument()
  })

  it('renders client info section', () => {
    render(<AuditPlan API={API} />)
    expect(screen.getByText('Client & Audit Information')).toBeInTheDocument()
  })

  it('renders generate button', () => {
    render(<AuditPlan API={API} />)
    expect(screen.getByText('📄 Generate Audit Plan')).toBeInTheDocument()
  })
})
