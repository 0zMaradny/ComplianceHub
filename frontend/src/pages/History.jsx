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

const statusBadgeBase = 'inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold'

function getStatusClass(status) {
  const map = {
    uploaded: 'bg-blue-50 text-[var(--primary)]',
    generating: 'bg-amber-50 text-amber-600',
    done: 'bg-green-50 text-green-600',
    error: 'bg-red-50 text-red-600',
  }
  return map[status] || 'bg-gray-100 text-gray-600'
}

function getResultClass(result) {
  if (result === 'Certified') return 'bg-green-50 text-green-600'
  if (result !== '—') return 'bg-amber-50 text-amber-600'
  return 'bg-gray-100 text-gray-600'
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
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-[var(--text-primary)]">Job History</h2>
        <p className="mt-1 text-[var(--text-secondary)]">All past audit generation jobs</p>
      </div>

      {error && <div className="px-3.5 py-2.5 rounded-lg text-xs font-medium mb-4 bg-red-50 border border-red-600 text-red-600">{error}</div>}

      <div className="mb-4">
        <input type="text" placeholder="Search jobs..." value={search}
          onChange={e => { setSearch(e.target.value); setPage(0) }}
          className="w-full max-w-xs px-3 py-2 rounded-md text-sm border border-[var(--border)] bg-[var(--bg-card)] text-[var(--text)]" />
      </div>

      {loading ? (
        <div className="animate-fadeIn"><Skeleton variant="table-row" count={8} className="mb-2" /></div>
      ) : jobs.length === 0 ? (
        <div className="text-center p-12 text-[var(--text-secondary)]">No jobs found. Generate your first audit documents from the Audit Generator page.</div>
      ) : (
        <div className="animate-slideIn">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-xs">
              <thead><tr>
                <th className="text-left px-3 py-2.5 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)] border-b-2 border-[var(--border-color)]">Date</th>
                <th className="text-left px-3 py-2.5 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)] border-b-2 border-[var(--border-color)]">Standards</th>
                <th className="text-left px-3 py-2.5 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)] border-b-2 border-[var(--border-color)]">Status</th>
                <th className="text-left px-3 py-2.5 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)] border-b-2 border-[var(--border-color)]">Result</th>
                <th className="text-left px-3 py-2.5 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)] border-b-2 border-[var(--border-color)]">Documents</th>
              </tr></thead>
              <tbody>
                {jobs.map(job => {
                  const status = findStatus(job.results)
                  return (
                    <tr key={job.job_id} className={selected?.job_id === job.job_id ? 'selected' : ''}>
                      <td className="px-3 py-3 border-b border-[var(--border-color)] align-middle whitespace-nowrap">{formatDate(job.created_at)}</td>
                      <td className="px-3 py-3 border-b border-[var(--border-color)] align-middle max-w-[240px] truncate">{getStandardsLabel(job.standards)}</td>
                      <td className="px-3 py-3 border-b border-[var(--border-color)] align-middle"><span className={`${statusBadgeBase} ${getStatusClass(job.status)}`}>{job.status}</span></td>
                      <td className="px-3 py-3 border-b border-[var(--border-color)] align-middle"><span className={`${statusBadgeBase} ${getResultClass(status)}`}>{status}</span></td>
                      <td className="px-3 py-3 border-b border-[var(--border-color)] align-middle">
                        {(() => {
                          const docCount = job.results && typeof job.results === 'object' ? Object.keys(job.results).length : 0
                          return docCount > 0 ? (
                            <span className="flex items-center gap-2">
                              <span className="text-xs mr-1 text-[var(--text-secondary)]">{docCount} docs</span>
                              <a href={`${API}/download/${job.job_id}`} className="text-xs px-2.5 py-1 rounded-md bg-[var(--primary)] text-white hover:bg-[var(--primary-dark)] disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center justify-center border-none transition-all duration-150 cursor-pointer no-underline">ZIP</a>
                              <button className="text-xs px-2.5 py-1 rounded-md bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200 dark:bg-gray-200 dark:text-gray-800 inline-flex items-center justify-center transition-all duration-150 cursor-pointer whitespace-nowrap" onClick={() => setSelected(job)}>Details</button>
                            </span>
                          ) : <span className="text-[var(--text-secondary)]">—</span>
                        })()}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          <div className="flex justify-center gap-2 mt-4">
            <button className="text-xs px-2.5 py-1 rounded-md bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200 dark:bg-gray-200 dark:text-gray-800 inline-flex items-center justify-center transition-all duration-150 cursor-pointer whitespace-nowrap" disabled={page === 0} onClick={() => setPage(p => p - 1)}>Previous</button>
            <span className="px-3 py-1 text-xs text-[var(--text-secondary)]">Page {page + 1}</span>
            <button className="text-xs px-2.5 py-1 rounded-md bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200 dark:bg-gray-200 dark:text-gray-800 inline-flex items-center justify-center transition-all duration-150 cursor-pointer whitespace-nowrap" disabled={!hasMore} onClick={() => setPage(p => p + 1)}>Next</button>
          </div>
        </div>
      )}

      {selected && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/50 animate-scaleIn" onClick={() => setSelected(null)}>
          <div className="rounded-xl w-full max-w-2xl max-h-[80vh] overflow-y-auto p-6 bg-[var(--bg-card)]" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="m-0 text-lg font-semibold text-[var(--text-primary)]">Job Details</h3>
              <button className="p-1.5 rounded-md text-base cursor-pointer border-none bg-gray-100 text-[var(--text-primary)]" onClick={() => setSelected(null)}>✕</button>
            </div>
            <div className="text-xs leading-relaxed text-[var(--text-primary)]">
              <div className="mb-3 pb-3 border-b border-[var(--border-color)]"><div className="font-semibold text-[10px] uppercase tracking-wider mb-1 text-[var(--text-secondary)]">Job ID</div><div className="whitespace-pre-wrap break-words">{selected.job_id}</div></div>
              <div className="mb-3 pb-3 border-b border-[var(--border-color)]"><div className="font-semibold text-[10px] uppercase tracking-wider mb-1 text-[var(--text-secondary)]">Created</div><div className="whitespace-pre-wrap break-words">{formatDate(selected.created_at)}</div></div>
              <div className="mb-3 pb-3 border-b border-[var(--border-color)]"><div className="font-semibold text-[10px] uppercase tracking-wider mb-1 text-[var(--text-secondary)]">Status</div><div className="whitespace-pre-wrap break-words">{selected.status}</div></div>
              {selected.standards && (
                <div className="mb-3 pb-3 border-b border-[var(--border-color)]"><div className="font-semibold text-[10px] uppercase tracking-wider mb-1 text-[var(--text-secondary)]">Standards</div><div className="whitespace-pre-wrap break-words">{getStandardsLabel(selected.standards)}</div></div>
              )}
              {selected.error && (
                <div className="mb-3 pb-3 border-b border-[var(--border-color)]"><div className="font-semibold text-[10px] uppercase tracking-wider mb-1 text-[var(--text-secondary)]">Error</div><div className="whitespace-pre-wrap break-words"><span className={`${statusBadgeBase} bg-red-50 text-red-600`}>{selected.error}</span></div></div>
              )}
              {selected.results && typeof selected.results === 'object' && Object.keys(selected.results).length > 0 && (
                <div className="mb-3 pb-3 border-b border-[var(--border-color)]">
                  <div className="font-semibold text-[10px] uppercase tracking-wider mb-1 text-[var(--text-secondary)]">Documents Generated</div>
                  <div className="whitespace-pre-wrap break-words">
                    {Object.entries(selected.results).map(([docType, info]) => (
                      <div key={docType} className="mb-1.5">
                        <strong>{docType}</strong>
                        {info.client_name && <span className="text-[var(--text-secondary)] ml-2">— {info.client_name}</span>}
                        {info.standard && <span className="text-[var(--text-secondary)] ml-1">({info.standard})</span>}
                        <div className="flex items-center gap-2 mt-1">
                          <a href={`${API}/download_doc/${selected.job_id}/${docType}`} className="text-xs px-2.5 py-1 rounded-md inline-flex items-center justify-center border border-gray-300 bg-gray-100 text-gray-700 hover:bg-gray-200 transition-all duration-150 cursor-pointer no-underline">DOCX</a>
                          {info.pdf_filename && (
                            <a href={`${API}/download_doc/${selected.job_id}/${docType}/pdf`} className="text-xs px-2.5 py-1 rounded-md inline-flex items-center justify-center border border-gray-300 bg-gray-100 text-gray-700 hover:bg-gray-200 transition-all duration-150 cursor-pointer no-underline ml-2">PDF</a>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
            <div className="mt-4 pt-4 flex gap-2 border-t border-[var(--border-color)]">
              <a href={`${API}/download/${selected.job_id}`} className="bg-[var(--primary)] text-white hover:bg-[var(--primary-dark)] disabled:opacity-50 disabled:cursor-not-allowed px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center border-none transition-all duration-150 cursor-pointer no-underline">Download All (ZIP)</a>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default History
