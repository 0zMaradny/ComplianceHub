import { useState, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import MandayForm from '../components/MandayForm'
import Skeleton from '../components/Skeleton'
import Spinner from '../components/Spinner'
import { useToast } from '../hooks/useToast'

const REFINABLE_FIELDS = {
  Audit_Report: ['findings_summary', 'conclusion', 'scope', 'methodology'],
  ISO_Checklist: ['sections', 'overall_assessment'],
  Certificate_Text: ['scope', 'certification_decision'],
  Certificate: ['scope', 'certification_decision', 'conditions'],
  TNL: ['summary'],
  Audit_Plan_Stage_1: ['audit_scope', 'audit_objectives', 'audit_criteria'],
  Audit_Plan_Stage_2: ['audit_scope', 'audit_objectives', 'audit_criteria'],
  Participation_List: ['notes'],
}

const CLEANED_TO_DATA = {
  findings_summary_preview: 'findings_summary',
}

function DocResultItem({ docType, result, standards, API, jobId, setPreview }) {
  const { t } = useTranslation()
  const label = (standards?.doc_labels && standards.doc_labels[docType]) || docType
  return (
    <div className="stat-card" style={{ padding: 14 }}>
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="text-sm font-semibold truncate">{label}</div>
          {result.error && (
            <div className="text-xs text-red-600 mt-1">{result.error}</div>
          )}
          {result.certification_decision && (
            <div className="text-[11px] mt-1 text-[var(--text-secondary)]">
              <strong>{t('audit.decision')}:</strong> <strong>{result.certification_decision}</strong>
              {result.conditions?.length > 0 && (
                <span className="ml-1 text-amber-600">
                  ({result.conditions.length} {result.conditions.length > 1 ? t('audit.conditions_plural') : t('audit.condition')})
                </span>
              )}
            </div>
          )}
          {result.total_sections > 0 && (
            <div className="text-[11px] mt-0.5 text-[var(--text-secondary)]">
              {result.total_sections} {t('audit.clauses_assessed')}
            </div>
          )}
          {result.findings_summary_preview && (
            <div className="text-[11px] mt-1 italic text-[var(--text-secondary)] line-clamp-2">
              {result.findings_summary_preview}
            </div>
          )}
        </div>
        {result.filename && (
          <div className="flex gap-1.5 shrink-0">
            <button className="btn btn-ghost" style={{ fontSize: 11, padding: '4px 10px' }}
              onClick={() => setPreview({ docType, label, result })}>Preview</button>
            <a href={`${API}/download_doc/${jobId}/${docType}`}
               className="btn btn-secondary" style={{ fontSize: 11, padding: '4px 10px' }}>DOCX</a>
            {result.pdf_filename && (
              <a href={`${API}/download_doc/${jobId}/${docType}/pdf`}
                 className="btn btn-secondary" style={{ fontSize: 11, padding: '4px 10px' }}>PDF</a>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default function Audit({ API, standards, hasApiKeys }) {
  const { t } = useTranslation()
  const showToast = useToast()
  const [step, setStep] = useState('upload')
  const [files, setFiles] = useState({ audit_notes: null, manday: null, template: null })
  const [selectedStandards, setSelectedStandards] = useState([])
  const [apiKey, setApiKey] = useState('')
  const [jobId, setJobId] = useState(null)
  const [progress, setProgress] = useState(null)
  const [results, setResults] = useState(null)
  const [mandayExtracted, setMandayExtracted] = useState(null)
  const [mandayConfig, setMandayConfig] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [elapsed, setElapsed] = useState(0)
  const [preview, setPreview] = useState(null)
  const [refineField, setRefineField] = useState('')
  const [refineInstruction, setRefineInstruction] = useState('')
  const [refining, setRefining] = useState(false)
  const [refineResult, setRefineResult] = useState(null)
  const [versions, setVersions] = useState(null)
  const [loadingVersions, setLoadingVersions] = useState(false)
  const [bulkRefining, setBulkRefining] = useState(false)
  const [bulkResult, setBulkResult] = useState(null)
  const [editingField, setEditingField] = useState(null)
  const [editValue, setEditValue] = useState('')
  const [savingEdit, setSavingEdit] = useState(false)
  const [diffView, setDiffView] = useState(null)
  const pollRef = useRef(null)
  const elapsedRef = useRef(null)

  const dataFieldName = (cleanedField) => CLEANED_TO_DATA[cleanedField] || cleanedField

  const startEdit = (cleanedField, currentValue) => {
    const val = typeof currentValue === 'string' ? currentValue : (Array.isArray(currentValue) ? currentValue.join('\n') : String(currentValue || ''))
    setEditValue(val)
    setEditingField(cleanedField)
  }

  const cancelEdit = () => { setEditingField(null); setEditValue('') }

  const saveEdit = async () => {
    if (!editingField || !preview) return
    const beforeVal = preview.result[editingField]
    setSavingEdit(true)
    try {
      const res = await fetch(`${API}/edit-field`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_id: jobId, doc_type: preview.docType, field: dataFieldName(editingField), value: editValue }),
      })
      const data = await res.json()
      if (data.success) {
        setPreview(prev => ({ ...prev, result: { ...prev.result, [editingField]: editValue } }))
        if (String(beforeVal) !== String(editValue)) setDiffView({ field: editingField, before: String(beforeVal || ''), after: editValue })
        setEditingField(null); setEditValue('')
      }
    } catch (e) { showToast('Failed to save: ' + e.message, 'error') }
    setSavingEdit(false)
  }

  const refineFromEdit = () => {
    if (!editingField || !preview) return
    setRefineField(dataFieldName(editingField))
    setRefineInstruction(`Replace the current value with exactly:\n${editValue}`)
    setEditingField(null); setEditValue('')
  }

  const isEditable = (cleanedField) => preview && (REFINABLE_FIELDS[preview.docType] || []).includes(dataFieldName(cleanedField))

  const handleFileSelect = (field, file) => { setFiles(prev => ({ ...prev, [field]: file })); setError(null) }
  const toggleStandard = (id) => { setSelectedStandards(prev => prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id]); setError(null) }

  const handleUpload = async () => {
    if (!files.audit_notes || !files.manday || selectedStandards.length === 0) return
    const MAX_SIZE = 50 * 1024 * 1024
    if (files.audit_notes.size > MAX_SIZE) { setError('Audit notes file exceeds 50 MB limit'); showToast('Audit notes file exceeds 50 MB limit', 'error'); return }
    if (files.manday.size > MAX_SIZE) { setError('Manday file exceeds 50 MB limit'); showToast('Manday file exceeds 50 MB limit', 'error'); return }
    if (files.template?.size > MAX_SIZE) { setError('Template file exceeds 50 MB limit'); showToast('Template file exceeds 50 MB limit', 'error'); return }
    setLoading(true); setError(null)
    const form = new FormData()
    form.append('audit_notes', files.audit_notes)
    form.append('manday', files.manday)
    if (files.template) form.append('checklist_template', files.template)
    form.append('api_key', apiKey)
    form.append('standards', JSON.stringify(selectedStandards))
    if (mandayConfig) form.append('manday_config', JSON.stringify(mandayConfig))
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 60000)
      const res = await fetch(`${API}/upload`, { method: 'POST', body: form, signal: controller.signal })
      clearTimeout(timeoutId)
      const data = await res.json()
      if (data.error) { setError(data.error); showToast(data.error, 'error'); setLoading(false); return }
      setJobId(data.job_id)
      if (data.manday_extracted) setMandayExtracted(data.manday_extracted)
      if (data.async) { setStep('generating'); setElapsed(0); elapsedRef.current = setInterval(() => setElapsed(prev => prev + 1), 1000); startPolling(data.job_id) }
      else setStep('apikey')
    } catch (e) {
      const msg = e.name === 'AbortError' ? t('audit.upload_timeout') : t('audit.upload_failed') + e.message
      setError(msg); showToast(msg, 'error')
    }
    setLoading(false)
  }

  const handleGenerate = async () => {
    setLoading(true); setError(null)
    const form = new FormData()
    form.append('job_id', jobId); form.append('api_key', apiKey)
    form.append('standards', JSON.stringify(selectedStandards))
    if (mandayConfig) form.append('manday_config', JSON.stringify(mandayConfig))
    try {
      const res = await fetch(`${API}/generate`, { method: 'POST', body: form })
      const data = await res.json()
      if (data.error) { setError(data.error); setLoading(false); return }
      setStep('generating'); setElapsed(0)
      elapsedRef.current = setInterval(() => setElapsed(prev => prev + 1), 1000)
      startPolling(data.job_id)
    } catch (e) { setError(t('audit.generation_failed') + e.message) }
    setLoading(false)
  }

  const startPolling = (jid) => {
    const evtSource = new EventSource(`${API}/progress/${jid}`)
    evtSource.onmessage = (e) => { try { const data = JSON.parse(e.data); setProgress(data) } catch (err) { console.error('SSE parse error:', err) } }
    evtSource.addEventListener('complete', (e) => {
      try { const data = JSON.parse(e.data); if (data.results) setResults(data.results); setStep('done'); clearInterval(elapsedRef.current); window.dispatchEvent(new CustomEvent('job-complete', { detail: { jobId: jid, standards: selectedStandards, status: 'done' } })) } catch (err) { console.error('SSE complete parse error:', err); setError('Connection error: failed to parse completion data') }
      evtSource.close()
    })
    evtSource.onerror = () => {
      evtSource.close()
      if (step === 'done') return
      pollRef.current = setInterval(async () => {
        try {
          const res = await fetch(`${API}/status/${jid}`)
          const data = await res.json()
          setProgress(data)
          if (data.status === 'done' || data.error) {
            clearInterval(pollRef.current)
            if (elapsedRef.current) clearInterval(elapsedRef.current)
            if (data.results) setResults(data.results)
            if (data.status === 'done') { setStep('done'); window.dispatchEvent(new CustomEvent('job-complete', { detail: { jobId: jid, standards: selectedStandards, status: 'done' } })) }
            if (data.error) { setError(data.error); window.dispatchEvent(new CustomEvent('job-complete', { detail: { jobId: jid, standards: selectedStandards, status: 'error' } })) }
          }
        } catch (e) { console.error('Poll error:', e) }
      }, 1500)
    }
    pollRef.current = { close: () => evtSource.close() }
  }

  useEffect(() => () => {
    if (pollRef.current) { if (typeof pollRef.current.close === 'function') pollRef.current.close(); else clearInterval(pollRef.current) }
    if (elapsedRef.current) clearInterval(elapsedRef.current)
  }, [])

  const handleReset = () => {
    setStep('upload'); setFiles({ audit_notes: null, manday: null, template: null })
    setSelectedStandards([]); setApiKey(''); setJobId(null)
    setProgress(null); setResults(null); setMandayExtracted(null); setMandayConfig(null)
    setError(null); setLoading(false); setElapsed(0)
    if (pollRef.current) { if (typeof pollRef.current.close === 'function') pollRef.current.close(); else clearInterval(pollRef.current) }
    if (elapsedRef.current) clearInterval(elapsedRef.current)
  }

  if (!standards) return <div className="animate-fadeIn p-8"><Skeleton variant="card" height="400px" /></div>

  return (
    <div className="animate-fadeIn mb-8">
      <h2 className="text-3xl font-bold text-[var(--text-primary)] m-0">{t('audit.title')}</h2>
      <p className="mt-1 text-[var(--text-secondary)]">{t('audit.subtitle')}</p>

      {step === 'upload' && (
        <div className="card mb-5 animate-pageIn">
          <div className="card-header">{t('audit.upload_files')}</div>
          {error && <div className="mx-6 mt-4 px-3.5 py-2.5 rounded-lg text-xs font-medium bg-red-50 border border-red-600 text-red-600">{error}</div>}

          <div className="card-body">
            <div className="mb-5">
              <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('audit.audit_notes')}</label>
              <div className="file-dropzone" onClick={() => document.getElementById('notes-input').click()}>
                {files.audit_notes ? (
                  <div>
                    <span style={{ fontSize: 24 }}>📄</span>
                    <div className="text-sm font-medium mt-1" style={{ color: 'var(--primary)' }}>{files.audit_notes.name}</div>
                    <div className="text-xs mt-0.5 text-[var(--text-secondary)]">{t('audit.click_to_change')}</div>
                  </div>
                ) : (
                  <div>
                    <span style={{ fontSize: 24 }}>📂</span>
                    <div className="text-sm font-medium mt-1" style={{ color: 'var(--text-secondary)' }}>{t('audit.drop_notes')}</div>
                    <div className="text-xs mt-0.5 text-[var(--text-secondary)]">{t('audit.supports_docx_txt')}</div>
                  </div>
                )}
              </div>
              <input id="notes-input" type="file" accept=".docx,.txt" onChange={e => handleFileSelect('audit_notes', e.target.files[0])} style={{ display: 'none' }} />
            </div>

            <div className="mb-5">
              <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('audit.manday_calc')}</label>
              <div className="file-dropzone" onClick={() => document.getElementById('manday-input').click()}>
                {files.manday ? (
                  <div>
                    <span style={{ fontSize: 24 }}>📊</span>
                    <div className="text-sm font-medium mt-1" style={{ color: 'var(--primary)' }}>{files.manday.name}</div>
                    <div className="text-xs mt-0.5 text-[var(--text-secondary)]">{t('audit.click_to_change')}</div>
                  </div>
                ) : (
                  <div>
                    <span style={{ fontSize: 24 }}>📂</span>
                    <div className="text-sm font-medium mt-1" style={{ color: 'var(--text-secondary)' }}>{t('audit.drop_manday')}</div>
                    <div className="text-xs mt-0.5 text-[var(--text-secondary)]">{t('audit.supports_docx')}</div>
                  </div>
                )}
              </div>
              <input id="manday-input" type="file" accept=".docx" onChange={e => handleFileSelect('manday', e.target.files[0])} style={{ display: 'none' }} />
            </div>

            <MandayForm standards={standards.standards} selectedStandards={selectedStandards}
              mandayExtracted={mandayExtracted} onMandayConfigChange={setMandayConfig} />

            <div className="mb-5">
              <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('audit.checklist_template')}</label>
              <div className="file-dropzone" onClick={() => document.getElementById('template-input').click()} style={{ padding: 12 }}>
                {files.template ? (
                  <div>
                    <span style={{ fontSize: 18 }}>📄</span>
                    <span className="text-sm font-medium ml-1" style={{ color: 'var(--primary)' }}>{files.template.name}</span>
                  </div>
                ) : (
                  <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>{t('audit.click_upload_template')}</div>
                )}
              </div>
              <input id="template-input" type="file" accept=".docx" onChange={e => handleFileSelect('template', e.target.files[0])} style={{ display: 'none' }} />
            </div>

            <div className="mb-5">
              <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('audit.standards')}</label>
              <div className="grid gap-2 grid-cols-[repeat(auto-fill,minmax(280px,1fr))]">
                {Object.entries(standards.standards).map(([id, label]) => (
                  <div key={id} className={`flex items-center gap-2 px-3 py-2.5 rounded-lg cursor-pointer text-sm border border-[var(--border-color)] hover:border-[var(--primary)] hover:bg-[var(--primary-light)] transition-all ${selectedStandards.includes(id) ? 'border-[var(--primary)] bg-[var(--primary-light)]' : ''}`}
                    onClick={() => toggleStandard(id)}>
                    <input type="checkbox" className="w-4 h-4 accent-[var(--primary)]" checked={selectedStandards.includes(id)} onChange={() => {}} />
                    <span>{label}</span>
                  </div>
                ))}
              </div>
              {selectedStandards.length === 0 && (
                <span className="text-xs mt-1 block text-red-600">{t('audit.select_standards')}</span>
              )}
            </div>

            <div className="mb-5">
              {hasApiKeys ? (
                <div className="flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm bg-green-50 border border-green-100 text-green-700">
                  <span>✓</span>
                  <span>{t('audit.ai_keys_configured')}</span>
                </div>
              ) : (
                <>
                  <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('audit.ai_provider_key')}</label>
                  <input type="password" placeholder={t('audit.enter_api_key')}
                    value={apiKey} onChange={e => setApiKey(e.target.value)} className="input" />
                  <div className="text-xs mt-1 text-[var(--text-secondary)]">
                    {!apiKey ? t('audit.offline_mode')
                      : apiKey.startsWith('hf_') ? t('audit.huggingface_free')
                      : t('audit.ai_powered')}
                  </div>
                </>
              )}
            </div>

            <button className="btn btn-primary" onClick={handleUpload}
              disabled={loading || !files.audit_notes || !files.manday || selectedStandards.length === 0}>
              {loading ? <><Spinner size="sm" className="mr-1.5" />{t('audit.uploading')}</> : t('audit.upload_generate')}
            </button>
          </div>
        </div>
      )}

      {step === 'apikey' && (
        <div className="card mb-5 animate-slideIn">
          <div className="card-header">{t('audit.confirm_generation')}</div>
          <div className="card-body">
            <p className="mb-4 text-sm text-[var(--text-secondary)]">
              {t('audit.files_uploaded')}
              {hasApiKeys
                ? ` ${t('audit.ai_keys_server')}`
                : ` ${t('audit.enter_api_key_optional')}`}
            </p>
            {!hasApiKeys && (
              <div className="mb-5">
                <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('audit.api_key_optional')}</label>
                <input type="password" placeholder={t('audit.leave_empty_offline')} value={apiKey}
                  onChange={e => setApiKey(e.target.value)} className="input" />
                <div className="text-xs mt-1 text-[var(--text-secondary)]">
                  {!apiKey ? t('audit.offline_no_key')
                    : apiKey.startsWith('hf_') ? t('audit.huggingface_free')
                    : t('audit.ai_powered')}
                </div>
              </div>
            )}
            {hasApiKeys && (
              <div className="flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm mb-5 bg-green-50 border border-green-100 text-green-700">
                <span>✓</span>
                <span>{t('audit.keys_ready')}</span>
              </div>
            )}
            <div className="flex gap-2">
              <button className="btn btn-primary" onClick={handleGenerate}>
                {apiKey || hasApiKeys ? t('audit.generate_with_ai') : t('audit.generate_offline')}
              </button>
              <button className="btn btn-secondary" onClick={handleReset}>{t('audit.cancel')}</button>
            </div>
          </div>
        </div>
      )}

      {step === 'generating' && progress && (
        <div className="card mb-5 animate-scaleIn">
          <div className="card-header">{t('audit.generating_docs')}</div>
          <div className="card-body">
            <div className="flex items-center gap-2 mb-4">
              <div className="animate-pulse w-3 h-3 rounded-full bg-[var(--amber-600)]" />
              <p className="text-xs text-[var(--text-secondary)]">
                {Math.floor(elapsed / 60)}{t('audit.m_elapsed')} {elapsed % 60}{t('audit.s_elapsed')}
                {progress.progress > 0 && progress.progress < 100 && (
                  <span className="ml-2">· {t('audit.eta')} {Math.floor((elapsed / progress.progress) * (100 - progress.progress) / 60)}m {Math.round((elapsed / progress.progress) * (100 - progress.progress) % 60)}s</span>
                )}
                {progress.provider_used && <span className="ml-2 px-1.5 py-0.5 rounded text-[10px] font-mono bg-[var(--primary-light)] text-[var(--primary)]">{progress.provider_used}</span>}
              </p>
            </div>
            <div className={`progress-bar mb-3 ${progress.progress < 100 ? 'progress-bar-active' : ''}`}>
              <div className="progress-bar-fill" style={{ width: `${progress.progress || 0}%` }} />
            </div>
            <p className="mb-3 text-sm text-[var(--text-secondary)]">
              {progress.progress || 0}% — {progress.current_doc || t('audit.starting')}
            </p>
            {progress.doc_progress && Object.keys(progress.doc_progress).length > 0 && (
              <div className="flex flex-col gap-1.5">
                {Object.keys(progress.doc_progress).map(doc => (
                  <div key={doc} className="flex items-center gap-2 text-sm">
                    <div className={`doc-progress-dot ${progress.doc_progress[doc]}`} />
                    <span className={`text-sm ${
                      progress.doc_progress[doc] === 'done' ? 'text-[var(--green-700)]' :
                      progress.doc_progress[doc] === 'error' ? 'text-[var(--red-600)]' :
                      progress.doc_progress[doc] === 'generating' ? 'text-[var(--amber-700)]' :
                      'text-[var(--text-secondary)]'
                    }`}>
                      {progress.doc_progress[doc] === 'done' ? t('audit.done')
                        : progress.doc_progress[doc] === 'error' ? t('audit.failed')
                        : progress.doc_progress[doc] === 'generating' ? t('audit.generating') : t('audit.pending')}
                    </span>
                    <span className="text-[var(--text-primary)]">{standards?.doc_labels?.[doc] || doc}</span>
                  </div>
                ))}
              </div>
            )}
            {error && <div className="px-3.5 py-2.5 rounded-lg text-xs font-medium mt-4 bg-red-50 border border-red-600 text-red-600">{error}</div>}
          </div>
        </div>
      )}

      {step === 'done' && (
        <div className="card mb-5 animate-pageIn">
          <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>{t('audit.documents_generated')}</span>
            {progress?.download_url && (
              <a href={`${API}/download/${jobId}`} className="btn btn-primary" style={{ fontSize: 12, padding: '6px 14px' }}>
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                {t('audit.download_all_zip')}
              </a>
            )}
          </div>
          <div className="card-body">
            <p className="mb-4 text-sm text-[var(--text-secondary)]">
              {t('audit.all_docs_created')}
            </p>
            <div className="grid gap-3 grid-cols-[repeat(auto-fill,minmax(220px,1fr))]">
              {results && (() => {
                const auditPackage = standards.audit_package_docs || [
                  'Audit_Plan_Stage_1','Audit_Plan_Stage_2','Participation_List',
                  'Audit_Report','ISO_Checklist','Certificate_Text','TNL','Certificate'
                ]
                const auditItems = Object.entries(results).filter(([t]) => auditPackage.includes(t))
                const standaloneItems = Object.entries(results).filter(([t]) => !auditPackage.includes(t))
                return (<>
                  {auditItems.length > 0 && (<>
                    <h4 className="mb-2.5 mt-0 text-xs font-semibold text-[var(--text-secondary)] col-span-full">
                      {t('audit.audit_package')} ({auditItems.length})
                    </h4>
                    {auditItems.map(([docType, result]) => (
                      <DocResultItem key={docType} docType={docType} result={result}
                        standards={standards} API={API} jobId={jobId} setPreview={setPreview} />
                    ))}
                  </>)}
                  {standaloneItems.length > 0 && (<>
                    <hr className="my-3 col-span-full border-t border-[var(--border-color)]" />
                    <h4 className="mb-2.5 mt-0 text-xs font-semibold text-[var(--text-secondary)] col-span-full">
                      {t('audit.standalone_docs')} ({standaloneItems.length})
                    </h4>
                    {standaloneItems.map(([docType, result]) => (
                      <DocResultItem key={docType} docType={docType} result={result}
                        standards={standards} API={API} jobId={jobId} setPreview={setPreview} />
                    ))}
                  </>)}
                </>)
              })()}
            </div>
            <button className="btn btn-secondary mt-5" onClick={handleReset}>{t('audit.generate_new')}</button>
          </div>
        </div>
      )}

      {preview && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/50 animate-scaleIn" onClick={() => setPreview(null)}>
          <div className="rounded-xl w-full max-w-2xl max-h-[80vh] overflow-y-auto p-6 bg-[var(--bg-card)]" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="m-0 text-lg font-semibold text-[var(--text-primary)]">{preview.label}</h3>
              <button className="p-1.5 rounded-md text-base cursor-pointer border-none bg-gray-100 text-[var(--text-primary)]" onClick={() => setPreview(null)}>✕</button>
            </div>
            <div className="text-xs leading-relaxed text-[var(--text-primary)]">
              {(() => {
                const f = (label, field, val) => val && (
                  <div className="mb-3 pb-3 border-b border-[var(--border-color)]">
                    <div className="font-semibold text-[10px] uppercase tracking-wider mb-1 text-[var(--text-secondary)]">{label}</div>
                    <div className={`whitespace-pre-wrap break-words ${isEditable(field) ? 'cursor-pointer' : 'cursor-default'}`}
                      onClick={() => isEditable(field) && startEdit(field, val)}>
                      {editingField === field ? (
                        <div onClick={e => e.stopPropagation()}>
                          <textarea value={editValue} onChange={e => setEditValue(e.target.value)} rows={3}
                            className="w-full p-1.5 text-xs rounded border border-[var(--primary)] resize-y" />
                          <div className="flex gap-1.5 mt-1">
                            <button className="bg-[var(--primary)] text-white hover:bg-[var(--primary-dark)] disabled:opacity-50 disabled:cursor-not-allowed px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center border-none transition-all duration-150 cursor-pointer text-[11px] px-2.5 py-1" onClick={saveEdit} disabled={savingEdit}>{savingEdit ? <Spinner size="sm" /> : t('audit.save')}</button>
                            <button className="bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200 dark:bg-gray-200 dark:text-gray-800 px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center transition-all duration-150 cursor-pointer text-[11px] px-2.5 py-1" onClick={refineFromEdit}>{t('audit.refine_with_ai')}</button>
                            <button className="text-[11px] px-2.5 py-1" onClick={cancelEdit}>{t('audit.cancel')}</button>
                          </div>
                        </div>
                      ) : (
                        field === 'certification_decision' ? (
                          <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold ${val === 'Certified' ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'}`}>{val}</span>
                        ) : <span>{val}</span>
                      )}
                    </div>
                  </div>
                )
                return <>
                  {f(t('audit.client'), 'client_name', preview.result.client_name)}
                  {f(t('audit.standard'), 'standard', preview.result.standard)}
                  {f(t('audit.audit_date'), 'audit_date', preview.result.audit_date)}
                  {f(t('audit.lead_auditor'), 'lead_auditor', preview.result.lead_auditor)}
                  {f(t('audit.decision'), 'certification_decision', preview.result.certification_decision)}
                  {f(t('audit.audit_type'), 'audit_type', preview.result.audit_type)}
                  {f(t('audit.total_mandays'), 'total_mandays', preview.result.total_mandays)}
                  {f(t('audit.employees'), 'employee_count', preview.result.employee_count)}
                  {f(t('audit.findings_summary'), 'findings_summary_preview', preview.result.findings_summary_preview)}
                  {preview.result.conditions?.length > 0 && (
                    <div className="mb-3 pb-3 border-b border-[var(--border-color)]">
                      <div className="font-semibold text-[10px] uppercase tracking-wider mb-1 text-[var(--text-secondary)]">{t('audit.conditions')} ({preview.result.conditions.length})</div>
                      <div className={`whitespace-pre-wrap break-words ${isEditable('conditions') ? 'cursor-pointer' : 'cursor-default'}`}
                        onClick={() => isEditable('conditions') && startEdit('conditions', preview.result.conditions.join('\n'))}>
                        {editingField === 'conditions' ? (
                          <div onClick={e => e.stopPropagation()}>
                            <textarea value={editValue} onChange={e => setEditValue(e.target.value)} rows={4}
                              className="w-full p-1.5 text-xs rounded border border-[var(--primary)] resize-y" />
                            <div className="flex gap-1.5 mt-1">
                              <button className="bg-[var(--primary)] text-white hover:bg-[var(--primary-dark)] disabled:opacity-50 disabled:cursor-not-allowed px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center border-none transition-all duration-150 cursor-pointer text-[11px] px-2.5 py-1" onClick={saveEdit} disabled={savingEdit}>{savingEdit ? <Spinner size="sm" /> : t('audit.save')}</button>
                              <button className="bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200 dark:bg-gray-200 dark:text-gray-800 px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center transition-all duration-150 cursor-pointer text-[11px] px-2.5 py-1" onClick={refineFromEdit}>{t('audit.refine_with_ai')}</button>
                              <button className="text-[11px] px-2.5 py-1" onClick={cancelEdit}>{t('audit.cancel')}</button>
                            </div>
                          </div>
                        ) : preview.result.conditions.map((c, i) => <div key={i}>• {c}</div>)}
                      </div>
                    </div>
                  )}
                  {f(t('audit.sections_assessed'), 'total_sections', preview.result.total_sections)}
                </>
              })()}

              <details className="mt-4">
                <summary className="cursor-pointer font-semibold text-xs text-[var(--primary)]">
                  ✨ {t('audit.refine_with_ai')}
                </summary>
                <div className="pt-2 flex flex-col gap-2">
                  <select value={refineField} onChange={e => { setRefineField(e.target.value); setRefineResult(null) }}
                    className="p-1.5 text-xs rounded border border-[var(--gray-300)]">
                    <option value="">{t('audit.select_field')}</option>
                    {(REFINABLE_FIELDS[preview.docType] || []).map(f => (
                      <option key={f} value={f}>{f}</option>
                    ))}
                  </select>
                  <textarea placeholder={t('audit.describe_change')} value={refineInstruction}
                    onChange={e => setRefineInstruction(e.target.value)} rows={2}
                    className="p-1.5 text-xs rounded border border-[var(--gray-300)] resize-y" />
                  <div className="flex gap-2 items-center flex-wrap">
                    <button className="bg-[var(--primary)] text-white hover:bg-[var(--primary-dark)] disabled:opacity-50 disabled:cursor-not-allowed px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center border-none transition-all duration-150 cursor-pointer text-xs px-3.5 py-1.5"
                      disabled={refining || !refineField || !refineInstruction}
                      onClick={async () => {
                        setRefining(true); setRefineResult(null)
                        try {
                          const res = await fetch(`${API}/refine`, {
                            method: 'POST', headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ job_id: jobId, doc_type: preview.docType, field: refineField, instruction: refineInstruction, api_key: apiKey }),
                          })
                          const data = await res.json()
                          if (data.new_value) {
                            setRefineResult({ success: true, value: data.new_value })
                            if (data.previous_value !== undefined) setDiffView({ field: refineField, before: String(data.previous_value || ''), after: data.new_value })
                          } else setRefineResult({ success: false, error: data.error || 'Refinement failed' })
                        } catch { setRefineResult({ success: false, error: t('audit.network_error') }) }
                        setRefining(false)
                      }}>{refining ? <><Spinner size="sm" className="mr-1" />{t('audit.regenerating')}</> : t('audit.regenerate')}</button>
                    <button className="bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200 dark:bg-gray-200 dark:text-gray-800 px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center transition-all duration-150 cursor-pointer text-xs px-3.5 py-1.5"
                      onClick={async () => {
                        setLoadingVersions(true); setVersions(null)
                        try { const res = await fetch(`${API}/refine/versions/${jobId}/${preview.docType}?field=${refineField}`); const data = await res.json(); setVersions(data.versions || []) }
                        catch { setVersions([]) }
                        setLoadingVersions(false)
                      }}>{loadingVersions ? t('audit.loading') : t('audit.history')}</button>
                    <button className="bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200 dark:bg-gray-200 dark:text-gray-800 px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center transition-all duration-150 cursor-pointer text-xs px-3.5 py-1.5"
                      disabled={bulkRefining || !refineInstruction}
                      onClick={async () => {
                        setBulkRefining(true); setBulkResult(null)
                        try { const res = await fetch(`${API}/refine/bulk/${jobId}/${preview.docType}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ instruction: refineInstruction, api_key: apiKey }) }); const data = await res.json(); setBulkResult(data) }
                        catch { setBulkResult({ error: 'Network error' }) }
                        setBulkRefining(false)
                      }}>{bulkRefining ? <><Spinner size="sm" className="mr-1" />{t('audit.refining_all')}</> : t('audit.refine_all')}</button>
                    {refineResult?.success && <span className="text-xs text-green-600">{t('audit.done_check')}</span>}
                    {refineResult && !refineResult.success && <span className="text-xs text-red-600">{refineResult.error}</span>}
                  </div>
                  {refineResult?.success && (
                    <div className="text-xs p-2 rounded max-h-[150px] overflow-auto text-[var(--gray-600)] bg-[var(--gray-100)]">
                      <strong>{t('audit.new_value')}</strong>
                      <pre className="whitespace-pre-wrap mt-1 text-[11px] m-0">{refineResult.value}</pre>
                      {diffView && diffView.field === refineField && (
                        <button className="bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200 dark:bg-gray-200 dark:text-gray-800 px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center transition-all duration-150 cursor-pointer text-[11px] px-2.5 py-1 mt-1.5"
                          onClick={() => setDiffView(prev => ({ ...prev, show: true }))}>{t('audit.view_diff')}</button>
                      )}
                    </div>
                  )}
                  {bulkResult && (
                    <div className="text-xs p-2 rounded text-[var(--gray-600)] bg-[var(--gray-100)]">
                      <strong>{t('audit.refine_all')}:</strong> {bulkResult.succeeded}/{bulkResult.total} {t('audit.fields_succeeded')}
                      {bulkResult.failed > 0 && <span className="text-red-600">, {bulkResult.failed} {t('audit.failed_label')}</span>}
                      {bulkResult.results?.map((r, i) => (
                        <div key={i} className="mt-1 p-1 text-[11px] rounded-sm bg-white">
                          <strong>{r.field}</strong>: {r.error ? <span className="text-red-600">{r.error}</span> : t('audit.updated')}
                        </div>
                      ))}
                    </div>
                  )}
                  {versions && (
                    <details className="text-xs">
                      <summary className="cursor-pointer font-semibold text-[var(--gray-600)]">{t('audit.version_history')} ({versions.length})</summary>
                      <div className="max-h-[200px] overflow-auto mt-1">
                        {versions.length === 0 ? <div className="p-1 text-[var(--gray-500)]">{t('audit.no_version_history')}</div>
                          : [...versions].reverse().map((v, i) => (
                            <div key={i} className="p-1.5 mb-1 rounded text-[11px] bg-[var(--blue-50)] border border-[var(--gray-200)]">
                              <div className="text-[10px] mb-0.5 text-[var(--gray-500)]">
                                v{versions.length - i} — {new Date(v.timestamp * 1000).toLocaleString()} — {v.instruction || 'generated'}
                              </div>
                              <pre className="m-0 whitespace-pre-wrap text-[11px] max-h-[80px] overflow-hidden">
                                {typeof v.value === 'string' ? v.value.slice(0, 500) + (v.value.length > 500 ? '...' : '') : JSON.stringify(v.value).slice(0, 500)}
                              </pre>
                            </div>
                          ))}
                      </div>
                    </details>
                  )}
                </div>
              </details>
            </div>
            <div className="mt-4 pt-4 flex gap-2 border-t border-[var(--border-color)]">
              <a href={`${API}/download_doc/${jobId}/${preview.docType}`} className="bg-[var(--primary)] text-white hover:bg-[var(--primary-dark)] disabled:opacity-50 disabled:cursor-not-allowed px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center border-none transition-all duration-150 cursor-pointer no-underline text-xs px-4 py-2">{t('audit.download_docx')}</a>
              {preview.result.pdf_filename && (
                <a href={`${API}/download_doc/${jobId}/${preview.docType}/pdf`} className="bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200 dark:bg-gray-200 dark:text-gray-800 px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center transition-all duration-150 cursor-pointer no-underline text-xs px-4 py-2">{t('audit.download_pdf')}</a>
              )}
            </div>
          </div>
        </div>
      )}

      {diffView?.show && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/50 animate-scaleIn" onClick={() => setDiffView(null)}>
          <div className="rounded-xl w-full max-w-2xl max-h-[80vh] overflow-y-auto p-6 bg-[var(--bg-card)]" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="m-0 text-lg font-semibold text-[var(--text-primary)]">{t('audit.diff_label')} {diffView.field}</h3>
              <button className="p-1.5 rounded-md text-base cursor-pointer border-none bg-gray-100 text-[var(--text-primary)]" onClick={() => setDiffView(null)}>✕</button>
            </div>
            <div className="text-xs leading-relaxed text-[var(--text-primary)]">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="text-xs font-semibold mb-2 text-red-600">{t('audit.before')}</h4>
                  <pre className="whitespace-pre-wrap text-xs leading-relaxed p-3 rounded-lg max-h-[400px] overflow-auto m-0"
                    style={{ background: '#fef2f2', border: '1px solid #fecaca' }}>{diffView.before || t('audit.empty_value')}</pre>
                </div>
                <div>
                  <h4 className="text-xs font-semibold mb-2 text-green-600">{t('audit.after')}</h4>
                  <pre className="whitespace-pre-wrap text-xs leading-relaxed p-3 rounded-lg max-h-[400px] overflow-auto m-0"
                    style={{ background: '#f0fdf4', border: '1px solid #bbf7d0' }}>{diffView.after}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
