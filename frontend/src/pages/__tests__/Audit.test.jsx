import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import Audit from '../Audit'

const API = '/api'
const standards = {
  standards: { iso_9001: 'ISO 9001:2015' },
  doc_labels: { Audit_Report: 'Audit Report' },
  audit_package_docs: [],
  standalone_docs: [],
}

describe('Audit', () => {
  it('renders upload form with standards prop loaded', () => {
    render(<Audit API={API} standards={standards} />)
    expect(screen.getByText('Audit Document Generator')).toBeInTheDocument()
  })

  it('shows loading when standards prop is null', () => {
    render(<Audit API={API} standards={null} />)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders file upload inputs', () => {
    render(<Audit API={API} standards={standards} />)
    expect(screen.getByText('Audit Notes (.docx or .txt) *')).toBeInTheDocument()
    expect(screen.getByText('Manday Calculation (.docx) *')).toBeInTheDocument()
  })

  it('renders ISO standards section', () => {
    render(<Audit API={API} standards={standards} />)
    expect(screen.getByText('ISO Standards *')).toBeInTheDocument()
  })
})
