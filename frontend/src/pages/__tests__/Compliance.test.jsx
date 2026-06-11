import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import Compliance from '../Compliance'

const mockFetch = vi.fn()
global.fetch = mockFetch

const API = '/api'

const standardsResponse = {
  standards: { iso_9001: 'ISO 9001:2015', iso_14001: 'ISO 14001:2015' },
  doc_labels: {},
}

beforeEach(() => {
  mockFetch.mockReset()
})

describe('Compliance', () => {
  it('renders page header', () => {
    mockFetch.mockResolvedValue({ json: async () => standardsResponse })
    render(<Compliance API={API} />)
    expect(screen.getByText('Compliance Assessment')).toBeInTheDocument()
  })

  it('renders standards list', async () => {
    mockFetch.mockResolvedValue({ json: async () => standardsResponse })
    render(<Compliance API={API} />)
    const standard = await screen.findByText('ISO 9001:2015')
    expect(standard).toBeInTheDocument()
  })
})
