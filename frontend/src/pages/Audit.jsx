import { useState, useRef, useEffect } from 'react'
import MandayForm from '../components/MandayForm'
import Skeleton from '../components/Skeleton'
import Spinner from '../components/Spinner'
import { useToast } from '../components/Toast'

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
  const label = (standards?.doc_labels && standards.doc_labels[docType]) || docType
  return (
    <div className="doc-result-item">
      <div>
        <div className="font-semibold text-xs">{label}</div>
        {result.error && (
          <div style={{ color: 'var(--red-600)' }} className="text-xs">{result.error}</div>
        )}
        {result.certification_decision && (
          <div className="text-[11px] mt-0.5" style={{ color: 'var(--gray-600)' }}>
            Decision: <strong>{result.certification_decision}</strong>
            {result.conditions?.length > 0 && (
              <span style={{ color: 'var(--amber-600)' }} className="ml-1">
                ({result.conditions.length} condition{result.conditions.length > 1 ? 's' : ''})
              </span>
            )}
          </div>
        )}
        {result.total_sections > 0 && (
          <div className="text-[11px]" style={{ color: 'var(--gray-600)' }}>
            {result.total_sections} clauses assessed
          </div>
        )}
        {result.findings_summary_preview && (
          <div className="text-[11px] mt-0.5 italic" style={{ color: 'var(--gray-500)' }}>
            {result.findings_summary_preview}...
          </div>
        )}
      </div>
      {result.filename && (
        <div className="flex gap-1.5">
          <button
            className="btn btn-secondary text-xs px-3 py-1.5"
            onClick={() => setPreview({ docType, label, result })}
          >Preview</button>
          <a href={`${API}/download_doc/${jobId}/${docType}`}
             className="btn btn-secondary text-xs px-3 py-1.5 no-underline">DOCX</a>
          {result.pdf_filename && (
            <a href={`${API}/download_doc/${jobId}/${docType}/pdf`}
               className="btn btn-secondary text-xs px-3 py-1.5 no-underline">PDF</a>
          )}
        </div>
      )}
    </div>
  )
}

export default function Audit({ API, standards }) {
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
    } catch {}
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
    setLoading(true); setError(null)
    const form = new FormData()
    form.append('audit_notes', files.audit_notes)
    form.append('manday', files.manday)
    if (files.template) form.append('checklist_template', files.template)
    form.append('api_key', apiKey)
    form.append('standards', JSON.stringify(selectedStandards))
    if (mandayConfig) form.append('manday_config', JSON.stringify(mandayConfig))
    try {
      const res = await fetch(`${API}/upload`, { method: 'POST', body: form })
      const data = await res.json()
      if (data.error) { setError(data.error); setLoading(false); return }
      setJobId(data.job_id)
      if (data.manday_extracted) setMandayExtracted(data.manday_extracted)
      if (data.async) { setStep('generating'); setElapsed(0); elapsedRef.current = setInterval(() => setElapsed(prev => prev + 1), 1000); startPolling(data.job_id) }
      else setStep('apikey')
    } catch (e) { setError('Upload failed: ' + e.message); showToast('Upload failed', 'error') }
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
    } catch (e) { setError('Generation failed: ' + e.message) }
    setLoading(false)
  }

  const startPolling = (jid) => {
    const evtSource = new EventSource(`${API}/progress/${jid}`)
    evtSource.onmessage = (e) => { try { const data = JSON.parse(e.data); setProgress(data) } catch {} }
    evtSource.addEventListener('complete', (e) => {
      try { const data = JSON.parse(e.data); if (data.results) setResults(data.results); setStep('done'); clearInterval(elapsedRef.current) } catch {}
      evtSource.close()
    })
    evtSource.onerror = () => {
      evtSource.close()
      pollRef.current = setInterval(async () => {
        try {
          const res = await fetch(`${API}/status/${jid}`)
          const data = await res.json()
          setProgress(data)
          if (data.status === 'done' || data.error) {
            clearInterval(pollRef.current)
            if (elapsedRef.current) clearInterval(elapsedRef.current)
            if (data.results) setResults(data.results)
            if (data.status === 'done') setStep('done')
            if (data.error) setError(data.error)
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
    <div className="animate-fadeIn">
      <div className="page-header">
        <h2>Audit Document Generator</h2>
        <p>Generate professional TÜV AUSTRIA audit documents from your audit notes</p>
      </div>

      {step === 'upload' && (
        <div className="card">
          <h3>Upload Audit Files</h3>
          {error && <div className="error-banner">{error}</div>}

          <div className="form-group">
            <label>Audit Notes (.docx or .txt) *</label>
            <input type="file" className="file-input" accept=".docx,.txt" onChange={e => handleFileSelect('audit_notes', e.target.files[0])} />
            {files.audit_notes && <span className="file-name">{files.audit_notes.name}</span>}
          </div>

          <div className="form-group">
            <label>Manday Calculation (.docx) *</label>
            <input type="file" className="file-input" accept=".docx" onChange={e => handleFileSelect('manday', e.target.files[0])} />
            {files.manday && <span className="file-name">{files.manday.name}</span>}
          </div>

          <MandayForm standards={standards.standards} selectedStandards={selectedStandards}
            mandayExtracted={mandayExtracted} onMandayConfigChange={setMandayConfig} />

          <div className="form-group">
            <label>Checklist Template (optional, .docx)</label>
            <input type="file" className="file-input" accept=".docx" onChange={e => handleFileSelect('template', e.target.files[0])} />
            {files.template && <span className="file-name">{files.template.name}</span>}
          </div>

          <div className="form-group">
            <label>ISO Standards *</label>
            <div className="checkbox-group">
              {Object.entries(standards.standards).map(([id, label]) => (
                <div key={id} className={`checkbox-item ${selectedStandards.includes(id) ? 'selected' : ''}`}
                  onClick={() => toggleStandard(id)}>
                  <input type="checkbox" checked={selectedStandards.includes(id)} onChange={() => {}} />
                  <span>{label}</span>
                </div>
              ))}
            </div>
            {selectedStandards.length === 0 && (
              <span className="text-xs mt-1 block" style={{ color: 'var(--red-600)' }}>Select at least one standard</span>
            )}
          </div>

          <div className="form-group">
            <label>AI Provider (optional — leave empty for offline mode)</label>
            <input type="password" placeholder="API key or leave empty for offline mode" value={apiKey}
              onChange={e => setApiKey(e.target.value)} />
            <div className="text-xs mt-1" style={{ color: 'var(--gray-500)' }}>
              {!apiKey ? '🔒 Offline mode — no API key needed, content generated locally'
                : apiKey.startsWith('hf_') ? '🤗 HuggingFace Free Tier — Llama-3-8B via API'
                : '☁️ AI-powered content generation'}
            </div>
          </div>

          <button className="btn btn-primary" onClick={handleUpload}
            disabled={loading || !files.audit_notes || !files.manday || selectedStandards.length === 0}>
            {loading ? <><Spinner size="sm" className="mr-1.5" />Uploading...</> : 'Upload & Generate'}
          </button>
        </div>
      )}

      {step === 'apikey' && (
        <div className="card animate-slideIn">
          <h3>API Key Required</h3>
          <p className="mb-4" style={{ color: 'var(--gray-600)' }}>
            Files uploaded successfully. Optionally enter an API key for AI-powered content, or leave empty for offline mode.
          </p>
          <div className="form-group">
            <label>API Key (optional for offline mode)</label>
            <input type="password" placeholder="Leave empty for offline mode" value={apiKey}
              onChange={e => setApiKey(e.target.value)} />
            <div className="text-xs mt-1" style={{ color: 'var(--gray-500)' }}>
              {!apiKey ? '🔒 Offline mode — no API key needed'
                : apiKey.startsWith('hf_') ? '🤗 HuggingFace Free Tier'
                : '☁️ AI-powered mode'}
            </div>
          </div>
          <button className="btn btn-primary" onClick={handleGenerate}>
            {apiKey ? 'Generate with AI' : 'Generate Offline'}
          </button>
          <button className="btn btn-secondary ml-2" onClick={handleReset}>Cancel</button>
        </div>
      )}

      {step === 'generating' && progress && (
        <div className="card animate-scaleIn">
          <h3>Generating Documents</h3>
          <div className="flex items-center gap-2 mb-4">
            <div className="animate-pulse w-3 h-3 rounded-full" style={{ background: 'var(--amber-600)' }} />
            <p className="text-xs" style={{ color: 'var(--gray-500)' }}>
              {Math.floor(elapsed / 60)}m {elapsed % 60}s elapsed
            </p>
          </div>
          <div className={`progress-bar ${progress.progress < 100 ? 'progress-bar-active' : ''}`}>
            <div className="progress-fill" style={{ width: `${progress.progress || 0}%` }} />
          </div>
          <p className="mb-3 text-sm" style={{ color: 'var(--gray-600)' }}>
            {progress.progress || 0}% — {progress.current_doc || 'Starting...'}
          </p>
          {progress.doc_progress && Object.keys(progress.doc_progress).length > 0 && (
            <div className="flex flex-col gap-1.5">
              {Object.keys(progress.doc_progress).map(doc => (
                <div key={doc} className="flex items-center gap-2 text-xs">
                  <span className={`status-badge ${progress.doc_progress[doc] || 'pending'}`}>
                    {progress.doc_progress[doc] === 'done' ? '✓'
                      : progress.doc_progress[doc] === 'error' ? '✗'
                      : progress.doc_progress[doc] === 'generating' ? '⟳' : '○'}
                  </span>
                  <span>{standards?.doc_labels?.[doc] || doc}</span>
                </div>
              ))}
            </div>
          )}
          {error && <div className="error-banner mt-3">{error}</div>}
        </div>
      )}

      {step === 'done' && (
        <div className="card animate-fadeIn">
          <h3>Documents Generated Successfully</h3>
          <p className="mb-4 text-xs" style={{ color: 'var(--gray-600)' }}>
            All audit documents have been created. Download individual documents or the full package.
          </p>
          {progress?.download_url && (
            <a href={`${API}/download/${jobId}`} className="btn btn-primary inline-block mb-5 no-underline">
              Download All (ZIP)
            </a>
          )}
          <div className="doc-results">
            {results && (() => {
              const auditPackage = standards.audit_package_docs || [
                'Audit_Plan_Stage_1','Audit_Plan_Stage_2','Participation_List',
                'Audit_Report','ISO_Checklist','Certificate_Text','TNL','Certificate'
              ]
              const standalone = standards.standalone_docs || []
              const auditItems = Object.entries(results).filter(([t]) => auditPackage.includes(t))
              const standaloneItems = Object.entries(results).filter(([t]) => !auditPackage.includes(t))
              return (<>
                {auditItems.length > 0 && (<>
                  <h4 className="mb-2.5 mt-0 text-xs font-semibold" style={{ color: 'var(--gray-700)' }}>
                    Audit Package ({auditItems.length})
                  </h4>
                  {auditItems.map(([docType, result]) => (
                    <DocResultItem key={docType} docType={docType} result={result}
                      standards={standards} API={API} jobId={jobId} setPreview={setPreview} />
                  ))}
                  <hr className="my-5 border-0" style={{ borderTop: '1px solid var(--gray-200)' }} />
                </>)}
                <h4 className="mb-2.5 mt-0 text-xs font-semibold" style={{ color: 'var(--gray-700)' }}>
                  Standalone Documents ({standaloneItems.length})
                </h4>
                {standaloneItems.map(([docType, result]) => (
                  <DocResultItem key={docType} docType={docType} result={result}
                    standards={standards} API={API} jobId={jobId} setPreview={setPreview} />
                ))}
              </>)
            })()}
          </div>
          <button className="btn btn-secondary mt-5" onClick={handleReset}>Generate New Documents</button>
        </div>
      )}

      {preview && (
        <div className="modal-overlay animate-scaleIn" onClick={() => setPreview(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{preview.label}</h3>
              <button className="modal-close" onClick={() => setPreview(null)}>✕</button>
            </div>
            <div className="modal-body">
              {(() => {
                const f = (label, field, val) => val && (
                  <div className="field">
                    <div className="field-label">{label}</div>
                    <div className="field-value" style={{ cursor: isEditable(field) ? 'pointer' : 'default' }}
                      onClick={() => isEditable(field) && startEdit(field, val)}>
                      {editingField === field ? (
                        <div onClick={e => e.stopPropagation()}>
                          <textarea value={editValue} onChange={e => setEditValue(e.target.value)} rows={3}
                            className="w-full p-1.5 text-xs rounded" style={{ border: '1px solid var(--blue-400)', resize: 'vertical' }} />
                          <div className="flex gap-1.5 mt-1">
                            <button className="btn btn-primary text-[11px] px-2.5 py-1" onClick={saveEdit} disabled={savingEdit}>{savingEdit ? <Spinner size="sm" /> : 'Save'}</button>
                            <button className="btn btn-secondary text-[11px] px-2.5 py-1" onClick={refineFromEdit}>Refine with AI</button>
                            <button className="text-[11px] px-2.5 py-1" onClick={cancelEdit}>Cancel</button>
                          </div>
                        </div>
                      ) : (
                        field === 'certification_decision' ? (
                          <span className={`status-badge ${val === 'Certified' ? 'done' : 'error'}`}>{val}</span>
                        ) : <span>{val}</span>
                      )}
                    </div>
                  </div>
                )
                return <>
                  {f('Client', 'client_name', preview.result.client_name)}
                  {f('Standard', 'standard', preview.result.standard)}
                  {f('Audit Date', 'audit_date', preview.result.audit_date)}
                  {f('Lead Auditor', 'lead_auditor', preview.result.lead_auditor)}
                  {f('Decision', 'certification_decision', preview.result.certification_decision)}
                  {f('Audit Type', 'audit_type', preview.result.audit_type)}
                  {f('Total Mandays', 'total_mandays', preview.result.total_mandays)}
                  {f('Employees', 'employee_count', preview.result.employee_count)}
                  {f('Findings Summary', 'findings_summary_preview', preview.result.findings_summary_preview)}
                  {preview.result.conditions?.length > 0 && (
                    <div className="field">
                      <div className="field-label">Conditions ({preview.result.conditions.length})</div>
                      <div className="field-value" style={{ cursor: isEditable('conditions') ? 'pointer' : 'default' }}
                        onClick={() => isEditable('conditions') && startEdit('conditions', preview.result.conditions.join('\n'))}>
                        {editingField === 'conditions' ? (
                          <div onClick={e => e.stopPropagation()}>
                            <textarea value={editValue} onChange={e => setEditValue(e.target.value)} rows={4}
                              className="w-full p-1.5 text-xs rounded" style={{ border: '1px solid var(--blue-400)', resize: 'vertical' }} />
                            <div className="flex gap-1.5 mt-1">
                              <button className="btn btn-primary text-[11px] px-2.5 py-1" onClick={saveEdit} disabled={savingEdit}>{savingEdit ? <Spinner size="sm" /> : 'Save'}</button>
                              <button className="btn btn-secondary text-[11px] px-2.5 py-1" onClick={refineFromEdit}>Refine with AI</button>
                              <button className="text-[11px] px-2.5 py-1" onClick={cancelEdit}>Cancel</button>
                            </div>
                          </div>
                        ) : preview.result.conditions.map((c, i) => <div key={i}>• {c}</div>)}
                      </div>
                    </div>
                  )}
                  {f('Sections Assessed', 'total_sections', preview.result.total_sections)}
                </>
              })()}

              <details className="mt-4">
                <summary className="cursor-pointer font-semibold text-xs" style={{ color: 'var(--blue-600)' }}>
                  ✨ Refine with AI
                </summary>
                <div className="pt-2 flex flex-col gap-2">
                  <select value={refineField} onChange={e => { setRefineField(e.target.value); setRefineResult(null) }}
                    className="p-1.5 text-xs rounded" style={{ border: '1px solid var(--gray-300)' }}>
                    <option value="">Select field to refine...</option>
                    {(REFINABLE_FIELDS[preview.docType] || []).map(f => (
                      <option key={f} value={f}>{f}</option>
                    ))}
                  </select>
                  <textarea placeholder="Describe the change..." value={refineInstruction}
                    onChange={e => setRefineInstruction(e.target.value)} rows={2}
                    className="p-1.5 text-xs rounded" style={{ border: '1px solid var(--gray-300)', resize: 'vertical' }} />
                  <div className="flex gap-2 items-center flex-wrap">
                    <button className="btn btn-primary text-xs px-3.5 py-1.5"
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
                        } catch { setRefineResult({ success: false, error: 'Network error' }) }
                        setRefining(false)
                      }}>{refining ? <><Spinner size="sm" className="mr-1" />Regenerating...</> : 'Regenerate'}</button>
                    <button className="btn btn-secondary text-xs px-3.5 py-1.5"
                      onClick={async () => {
                        setLoadingVersions(true); setVersions(null)
                        try { const res = await fetch(`${API}/refine/versions/${jobId}/${preview.docType}?field=${refineField}`); const data = await res.json(); setVersions(data.versions || []) }
                        catch { setVersions([]) }
                        setLoadingVersions(false)
                      }}>{loadingVersions ? 'Loading...' : 'History'}</button>
                    <button className="btn btn-secondary text-xs px-3.5 py-1.5"
                      disabled={bulkRefining || !refineInstruction}
                      onClick={async () => {
                        setBulkRefining(true); setBulkResult(null)
                        try { const res = await fetch(`${API}/refine/bulk/${jobId}/${preview.docType}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ instruction: refineInstruction, api_key: apiKey }) }); const data = await res.json(); setBulkResult(data) }
                        catch { setBulkResult({ error: 'Network error' }) }
                        setBulkRefining(false)
                      }}>{bulkRefining ? <><Spinner size="sm" className="mr-1" />Refining All...</> : 'Refine All'}</button>
                    {refineResult?.success && <span className="text-xs" style={{ color: 'var(--green-600)' }}>Done ✓</span>}
                    {refineResult && !refineResult.success && <span className="text-xs" style={{ color: 'var(--red-600)' }}>{refineResult.error}</span>}
                  </div>
                  {refineResult?.success && (
                    <div className="text-xs p-2 rounded max-h-[150px] overflow-auto" style={{ color: 'var(--gray-600)', background: 'var(--gray-100)' }}>
                      <strong>New value:</strong>
                      <pre className="whitespace-pre-wrap mt-1 text-[11px]" style={{ margin: 0 }}>{refineResult.value}</pre>
                      {diffView && diffView.field === refineField && (
                        <button className="btn btn-secondary text-[11px] px-2.5 py-1 mt-1.5"
                          onClick={() => setDiffView(prev => ({ ...prev, show: true }))}>View Diff</button>
                      )}
                    </div>
                  )}
                  {bulkResult && (
                    <div className="text-xs p-2 rounded" style={{ color: 'var(--gray-600)', background: 'var(--gray-100)' }}>
                      <strong>Bulk Refine:</strong> {bulkResult.succeeded}/{bulkResult.total} fields succeeded
                      {bulkResult.failed > 0 && <span style={{ color: 'var(--red-600)' }}>, {bulkResult.failed} failed</span>}
                      {bulkResult.results?.map((r, i) => (
                        <div key={i} className="mt-1 p-1 text-[11px] rounded-sm bg-white">
                          <strong>{r.field}</strong>: {r.error ? <span style={{ color: 'var(--red-600)' }}>{r.error}</span> : '✓ updated'}
                        </div>
                      ))}
                    </div>
                  )}
                  {versions && (
                    <details className="text-xs">
                      <summary className="cursor-pointer font-semibold" style={{ color: 'var(--gray-600)' }}>Version History ({versions.length})</summary>
                      <div className="max-h-[200px] overflow-auto mt-1">
                        {versions.length === 0 ? <div className="p-1" style={{ color: 'var(--gray-500)' }}>No version history for this field</div>
                          : [...versions].reverse().map((v, i) => (
                            <div key={i} className="p-1.5 mb-1 rounded text-[11px]" style={{
                              background: i === 0 ? 'var(--blue-50)' : 'transparent', border: '1px solid var(--gray-200)',
                            }}>
                              <div className="text-[10px] mb-0.5" style={{ color: 'var(--gray-500)' }}>
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
            <div className="modal-footer">
              <a href={`${API}/download_doc/${jobId}/${preview.docType}`} className="btn btn-primary text-xs px-4 py-2 no-underline">Download DOCX</a>
              {preview.result.pdf_filename && (
                <a href={`${API}/download_doc/${jobId}/${preview.docType}/pdf`} className="btn btn-secondary text-xs px-4 py-2 no-underline">Download PDF</a>
              )}
            </div>
          </div>
        </div>
      )}

      {diffView?.show && (
        <div className="modal-overlay animate-scaleIn" onClick={() => setDiffView(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Diff: {diffView.field}</h3>
              <button className="modal-close" onClick={() => setDiffView(null)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="text-xs font-semibold mb-2" style={{ color: 'var(--red-600)' }}>Before</h4>
                  <pre className="whitespace-pre-wrap text-xs leading-relaxed p-3 rounded-lg max-h-[400px] overflow-auto m-0"
                    style={{ background: '#fef2f2', border: '1px solid #fecaca' }}>{diffView.before || '(empty)'}</pre>
                </div>
                <div>
                  <h4 className="text-xs font-semibold mb-2" style={{ color: 'var(--green-600)' }}>After</h4>
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
