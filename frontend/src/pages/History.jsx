import { useState, useEffect, useCallback, startTransition } from 'react'
import { useTranslation } from 'react-i18next'
import Skeleton from '../components/Skeleton'
import EmptyState from '../components/EmptyState'
import DocPreview from '../components/DocPreview'

function formatDate(ts) {
  if (!ts) return '—'
  const d = new Date(ts * 1000)
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function findStatus(results, t) {
  if (!results || typeof results !== 'object') return '—'
  const decisions = Object.values(results)
    .filter(v => v && typeof v === 'object' && v.certification_decision)
    .map(v => v.certification_decision)
  if (decisions.length > 0) {
    const all = decisions.every(d => d === 'Certified')
    return all ? t('history.certified') : decisions.includes('Conditional') ? t('history.conditional') : t('history.non_certified')
  }
  return t('history.generated')
}

function getStandardsLabel(standards) {
  if (!standards) return '—'
  const arr = Array.isArray(standards) ? standards : [standards]
  return arr.map(s => s.replace('iso_', 'ISO ').replace('_', ':')).join(', ')
}

function getStatusClass(status) {
  const map = {
    uploaded: 'badge-info',
    generating: 'badge-warning',
    done: 'badge-success',
    error: 'badge-error',
  }
  return map[status] || 'badge-info'
}

function getResultClass(result) {
  if (result === 'Certified') return 'badge-success'
  if (result !== '—') return 'badge-warning'
  return 'badge-info'
}

function History({ API }) {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selected, setSelected] = useState(null)
  const [preview, setPreview] = useState(null)
  const [page, setPage] = useState(0)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [hasMore, setHasMore] = useState(false)
  const limit = 15
  const { t } = useTranslation()
  const badgeLabels = {
    uploaded: t('history.badge_uploaded'),
    generating: t('history.badge_generating'),
    done: t('history.badge_done'),
    error: t('history.badge_error'),
  }

  const fetchJobs = useCallback((pageNum, searchTerm, status) => {
    setLoading(true)
    const params = new URLSearchParams({ limit, offset: pageNum * limit })
    if (searchTerm) params.set('search', searchTerm)
    if (status) params.set('status', status)
    fetch(`${API}/jobs?${params}`)
      .then(r => r.json())
      .then(data => { setJobs(data.jobs || []); setHasMore((data.jobs || []).length >= limit); setLoading(false) })
      .catch(e => { setError(e.message); setLoading(false) })
  }, [API])

  useEffect(() => { startTransition(() => fetchJobs(page, search, statusFilter)) }, [fetchJobs, page, search, statusFilter])

  return (
    <div className="animate-fadeIn">
      <div className="page-header">
        <h2>{t('history.title')}</h2>
        <p>{t('history.subtitle')}</p>
      </div>

      {error && <div className="px-3.5 py-2.5 rounded-lg text-xs font-medium mb-4 bg-red-50 border border-red-600 text-red-600">{error}</div>}

      <div className="flex gap-3 mb-4 items-center">
        <input type="text" placeholder={t('history.search')} value={search}
          onChange={e => { setSearch(e.target.value); setPage(0) }}
          className="input max-w-xs" />
        <select value={statusFilter} onChange={e => { setStatusFilter(e.target.value); setPage(0) }}
          className="input max-w-[140px]">
          <option value="">{t('history.all_statuses')}</option>
          <option value="uploaded">{t('history.badge_uploaded')}</option>
          <option value="generating">{t('history.badge_generating')}</option>
          <option value="done">{t('history.badge_done')}</option>
          <option value="error">{t('history.badge_error')}</option>
        </select>
      </div>

      {loading ? (
        <div className="animate-fadeIn"><Skeleton variant="table-row" count={8} className="mb-2" /></div>
      ) : jobs.length === 0 ? (
        <EmptyState icon="history" title={t('dashboard.no_jobs_yet')} description={t('history.empty')} action={{ label: t('dashboard.generate_audit_docs'), onClick: () => window.dispatchEvent(new CustomEvent('navigate', { detail: 'audit' })) }} />
      ) : (
        <div className="animate-slideIn">
          <div className="table-container">
            <table>
              <thead><tr>
                <th className="text-left">{t('history.date')}</th>
                <th className="text-left">{t('history.standards')}</th>
                <th className="text-left">{t('history.status')}</th>
                <th className="text-left">{t('history.result')}</th>
                <th className="text-left">{t('history.documents')}</th>
              </tr></thead>
              <tbody>
                {jobs.map(job => {
                  const status = findStatus(job.results, t)
                  return (
                    <tr key={job.job_id} className={selected?.job_id === job.job_id ? 'selected' : ''}>
                      <td className="align-middle whitespace-nowrap">{formatDate(job.created_at)}</td>
                      <td className="align-middle max-w-[240px] truncate">{getStandardsLabel(job.standards)}</td>
                      <td className="align-middle"><span className={`badge ${getStatusClass(job.status)}`}>{badgeLabels[job.status] || job.status}</span></td>
                      <td className="align-middle"><span className={`badge ${getResultClass(status)}`}>{status}</span></td>
                      <td className="align-middle">
                        {(() => {
                          const docCount = job.results && typeof job.results === 'object' ? Object.keys(job.results).length : 0
                          return docCount > 0 ? (
                            <span className="flex items-center gap-2">
                              <span className="text-xs mr-1 text-[var(--text-secondary)]">{docCount} {t('history.docs_suffix')}</span>
                              <a href={`${API}/download/${job.job_id}`} className="btn btn-primary" style={{ fontSize: 11, padding: '4px 10px' }}>{t('history.zip')}</a>
                              <button className="btn btn-secondary" style={{ fontSize: 11, padding: '4px 10px' }} onClick={() => setSelected(job)}>{t('history.details')}</button>
                            </span>
                          ) : <span className="text-[var(--text-secondary)]">{t('history.fallback')}</span>
                        })()}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          <div className="flex justify-center gap-2 mt-4">
            <button className="btn btn-secondary" style={{ fontSize: 11, padding: '4px 10px' }} disabled={page === 0} onClick={() => setPage(p => p - 1)}>{t('history.previous')}</button>
            <span className="px-3 py-1 text-xs text-[var(--text-secondary)]">{t('history.page')}{page + 1}</span>
            <button className="btn btn-secondary" style={{ fontSize: 11, padding: '4px 10px' }} disabled={!hasMore} onClick={() => setPage(p => p + 1)}>{t('history.next')}</button>
          </div>
        </div>
      )}

      {preview && (
        <DocPreview API={API} jobId={preview.jobId} docType={preview.docType}
          label={preview.label} onClose={() => setPreview(null)} />
      )}

      {selected && (
        <div className="modal-overlay" onClick={() => setSelected(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3 style={{ margin: 0, fontSize: 16, fontWeight: 600 }}>{t('history.job_details')}</h3>
              <button className="btn btn-ghost" onClick={() => setSelected(null)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="text-xs leading-relaxed text-[var(--text-primary)]">
                <div className="mb-3 pb-3 border-b border-[var(--border-color)]"><div className="font-semibold text-[10px] uppercase tracking-wider mb-1 text-[var(--text-secondary)]">{t('history.job_id')}</div><div className="whitespace-pre-wrap break-words">{selected.job_id}</div></div>
                <div className="mb-3 pb-3 border-b border-[var(--border-color)]"><div className="font-semibold text-[10px] uppercase tracking-wider mb-1 text-[var(--text-secondary)]">{t('history.created')}</div><div className="whitespace-pre-wrap break-words">{formatDate(selected.created_at)}</div></div>
                <div className="mb-3 pb-3 border-b border-[var(--border-color)]"><div className="font-semibold text-[10px] uppercase tracking-wider mb-1 text-[var(--text-secondary)]">{t('history.status')}</div><div className="whitespace-pre-wrap break-words">{badgeLabels[selected.status] || selected.status}</div></div>
                {selected.standards && (
                  <div className="mb-3 pb-3 border-b border-[var(--border-color)]"><div className="font-semibold text-[10px] uppercase tracking-wider mb-1 text-[var(--text-secondary)]">{t('history.standards')}</div><div className="whitespace-pre-wrap break-words">{getStandardsLabel(selected.standards)}</div></div>
                )}
                {selected.error && (
                  <div className="mb-3 pb-3 border-b border-[var(--border-color)]"><div className="font-semibold text-[10px] uppercase tracking-wider mb-1 text-[var(--text-secondary)]">{t('history.error')}</div><div className="whitespace-pre-wrap break-words"><span className="badge badge-error">{selected.error}</span></div></div>
                )}
                {selected.results && typeof selected.results === 'object' && Object.keys(selected.results).length > 0 && (
                  <div className="mb-3 pb-3 border-b border-[var(--border-color)]">
                    <div className="font-semibold text-[10px] uppercase tracking-wider mb-1 text-[var(--text-secondary)]">{t('history.docs_generated')}</div>
                    <div className="whitespace-pre-wrap break-words">
                      {Object.entries(selected.results).map(([docType, info]) => (
                        <div key={docType} className="mb-1.5">
                          <strong>{docType}</strong>
                          {info.client_name && <span className="text-[var(--text-secondary)] ml-2">— {info.client_name}</span>}
                          {info.standard && <span className="text-[var(--text-secondary)] ml-1">({info.standard})</span>}
                          <div className="flex items-center gap-2 mt-1">
                            <button onClick={() => setPreview({ jobId: selected.job_id, docType, label: docType })} className="btn btn-primary" style={{ fontSize: 11, padding: '4px 10px' }}>{t('history.preview')}</button>
                            <a href={`${API}/download_doc/${selected.job_id}/${docType}`} className="btn btn-secondary" style={{ fontSize: 11, padding: '4px 10px' }}>{t('history.docx')}</a>
                            {info.pdf_filename && (
                              <a href={`${API}/download_doc/${selected.job_id}/${docType}/pdf`} className="btn btn-secondary" style={{ fontSize: 11, padding: '4px 10px' }}>{t('history.pdf')}</a>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
            <div className="modal-footer">
              <a href={`${API}/download/${selected.job_id}`} className="btn btn-primary">{t('history.download_all')}</a>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default History
