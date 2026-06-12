import { useState, useEffect, useCallback, startTransition } from 'react'
import Skeleton from '../components/Skeleton'

function formatDate(ts) {
  if (!ts) return '—'
  const d = new Date(ts * 1000)
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function findStatus(results) {
  if (!results || typeof results !== 'object') return '—'
  const decisions = Object.values(results)
    .filter(v => v && typeof v === 'object' && v.certification_decision)
    .map(v => v.certification_decision)
  if (decisions.length > 0) {
    const all = decisions.every(d => d === 'Certified')
    return all ? 'Certified' : decisions.includes('Conditional') ? 'Conditional' : 'Non-Certified'
  }
  return 'Generated'
}

function getStandardsLabel(standards) {
  if (!standards) return '—'
  const arr = Array.isArray(standards) ? standards : [standards]
  return arr.map(s => s.replace('iso_', 'ISO ').replace('_', ':')).join(', ')
}

function History({ API }) {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selected, setSelected] = useState(null)
  const [page, setPage] = useState(0)
  const [search, setSearch] = useState('')
  const [hasMore, setHasMore] = useState(false)
  const limit = 15

  const fetchJobs = useCallback((pageNum, searchTerm) => {
    setLoading(true)
    const params = new URLSearchParams({ limit, offset: pageNum * limit })
    if (searchTerm) params.set('search', searchTerm)
    fetch(`${API}/jobs?${params}`)
      .then(r => r.json())
      .then(data => { setJobs(data.jobs || []); setHasMore((data.jobs || []).length >= limit); setLoading(false) })
      .catch(e => { setError(e.message); setLoading(false) })
  }, [API])

  useEffect(() => { startTransition(() => fetchJobs(page, search)) }, [fetchJobs, page, search])

  return (
    <div className="animate-fadeIn">
      <div className="page-header">
        <h2>Job History</h2>
        <p>All past audit generation jobs</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="mb-4">
        <input type="text" placeholder="Search jobs..." value={search}
          onChange={e => { setSearch(e.target.value); setPage(0) }}
          className="w-full max-w-xs px-3 py-2 rounded-md text-sm"
          style={{ border: '1px solid var(--border)', background: 'var(--bg-card)', color: 'var(--text)' }} />
      </div>

      {loading ? (
        <div className="animate-fadeIn"><Skeleton variant="table-row" count={8} className="mb-2" /></div>
      ) : jobs.length === 0 ? (
        <div className="empty-state">No jobs found. Generate your first audit documents from the Audit Generator page.</div>
      ) : (
        <div className="animate-slideIn">
          <div className="table-container">
            <table className="jobs-table">
              <thead><tr>
                <th>Date</th><th>Standards</th><th>Status</th><th>Result</th><th>Documents</th>
              </tr></thead>
              <tbody>
                {jobs.map(job => {
                  const status = findStatus(job.results)
                  return (
                    <tr key={job.job_id} className={selected?.job_id === job.job_id ? 'selected' : ''}>
                      <td className="nowrap">{formatDate(job.created_at)}</td>
                      <td className="standards-cell">{getStandardsLabel(job.standards)}</td>
                      <td><span className={`status-badge status-${job.status}`}>{job.status}</span></td>
                      <td><span className={`status-badge ${status === 'Certified' ? 'done' : status !== '—' ? 'warn' : 'muted'}`}>{status}</span></td>
                      <td>
                        {(() => {
                          const docCount = job.results && typeof job.results === 'object' ? Object.keys(job.results).length : 0
                          return docCount > 0 ? (
                            <div className="doc-links">
                              <span className="doc-count">{docCount} docs</span>
                              <a href={`${API}/download/${job.job_id}`} className="btn btn-small btn-primary no-underline">ZIP</a>
                              <button className="btn btn-small btn-secondary" onClick={() => setSelected(job)}>Details</button>
                            </div>
                          ) : <span className="muted">—</span>
                        })()}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          <div className="flex justify-center gap-2 mt-4">
            <button className="btn btn-small btn-secondary" disabled={page === 0} onClick={() => setPage(p => p - 1)}>Previous</button>
            <span className="px-3 py-1 text-xs" style={{ color: 'var(--text-secondary)' }}>Page {page + 1}</span>
            <button className="btn btn-small btn-secondary" disabled={!hasMore} onClick={() => setPage(p => p + 1)}>Next</button>
          </div>
        </div>
      )}

      {selected && (
        <div className="modal-overlay animate-scaleIn" onClick={() => setSelected(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Job Details</h3>
              <button className="modal-close" onClick={() => setSelected(null)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="field"><div className="field-label">Job ID</div><div className="field-value">{selected.job_id}</div></div>
              <div className="field"><div className="field-label">Created</div><div className="field-value">{formatDate(selected.created_at)}</div></div>
              <div className="field"><div className="field-label">Status</div><div className="field-value">{selected.status}</div></div>
              {selected.standards && (
                <div className="field"><div className="field-label">Standards</div><div className="field-value">{getStandardsLabel(selected.standards)}</div></div>
              )}
              {selected.error && (
                <div className="field"><div className="field-label">Error</div><div className="field-value"><span className="status-badge error">{selected.error}</span></div></div>
              )}
              {selected.results && typeof selected.results === 'object' && Object.keys(selected.results).length > 0 && (
                <div className="field">
                  <div className="field-label">Documents Generated</div>
                  <div className="field-value">
                    {Object.entries(selected.results).map(([docType, info]) => (
                      <div key={docType} className="mb-1.5">
                        <strong>{docType}</strong>
                        {info.client_name && <span className="muted ml-2">— {info.client_name}</span>}
                        {info.standard && <span className="muted ml-1">({info.standard})</span>}
                        <div className="doc-links mt-1">
                          <a href={`${API}/download_doc/${selected.job_id}/${docType}`} className="btn btn-small">DOCX</a>
                          {info.pdf_filename && (
                            <a href={`${API}/download_doc/${selected.job_id}/${docType}/pdf`} className="btn btn-small ml-2">PDF</a>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
            <div className="modal-footer">
              <a href={`${API}/download/${selected.job_id}`} className="btn btn-primary no-underline">Download All (ZIP)</a>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default History
