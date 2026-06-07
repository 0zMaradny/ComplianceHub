import { useState, useEffect } from 'react'

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

  useEffect(() => {
    let cancelled = false
    fetch(`${API}/jobs`)
      .then(r => r.json())
      .then(data => { if (!cancelled) { setJobs(data.jobs || []); setLoading(false) } })
      .catch(e => { if (!cancelled) { setError(e.message); setLoading(false) } })
    return () => { cancelled = true }
  }, [API])

  return (
    <div>
      <div className="page-header">
        <h2>Job History</h2>
        <p className="subtitle">All past audit generation jobs</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {loading ? (
        <div className="loading">Loading...</div>
      ) : jobs.length === 0 ? (
        <div className="empty-state">No jobs found. Generate your first audit documents from the Audit Generator page.</div>
      ) : (
        <div className="table-container">
          <table className="jobs-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Standards</th>
                <th>Status</th>
                <th>Result</th>
                <th>Documents</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map(job => {
                const status = findStatus(job.results)
                const standards = getStandardsLabel(job.standards)
                const docCount = job.results && typeof job.results === 'object'
                  ? Object.keys(job.results).length : 0
                return (
                  <tr key={job.job_id} className={selected?.job_id === job.job_id ? 'selected' : ''}>
                    <td className="nowrap">{formatDate(job.created_at)}</td>
                    <td className="standards-cell">{standards}</td>
                    <td>
                      <span className={`status-badge status-${job.status}`}>{job.status}</span>
                    </td>
                    <td>
                      <span className={`status-badge ${status === 'Certified' ? 'done' : status !== '—' ? 'warn' : 'muted'}`}>{status}</span>
                    </td>
                    <td>
                      {docCount > 0 ? (
                        <div className="doc-links">
                          <span className="doc-count">{docCount} docs</span>
                          <a href={`${API}/download/${job.job_id}`} className="btn btn-small btn-primary">ZIP</a>
                          <button className="btn btn-small btn-secondary" onClick={() => setSelected(job)}>Details</button>
                        </div>
                      ) : (
                        <span className="muted">—</span>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {selected && (
        <div className="modal-overlay" onClick={() => setSelected(null)}>
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
                      <div key={docType} style={{ marginBottom: 6 }}>
                        <strong>{docType}</strong>
                        {info.client_name && <span className="muted" style={{ marginLeft: 8 }}>— {info.client_name}</span>}
                        {info.standard && <span className="muted" style={{ marginLeft: 4 }}>({info.standard})</span>}
                        <div className="doc-links" style={{ marginTop: 4 }}>
                          <a href={`${API}/download_doc/${selected.job_id}/${docType}`} className="btn btn-small">DOCX</a>
                          {info.pdf_filename && (
                            <a href={`${API}/download_doc/${selected.job_id}/${docType}/pdf`} style={{ marginLeft: 8 }} className="btn btn-small">PDF</a>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
            <div className="modal-footer">
              <a href={`${API}/download/${selected.job_id}`} className="btn btn-primary">Download All (ZIP)</a>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default History
