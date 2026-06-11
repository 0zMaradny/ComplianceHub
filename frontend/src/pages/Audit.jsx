import { useState, useRef, useEffect } from 'react'
import MandayForm from '../components/MandayForm'

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

// Maps cleaned result field names to _data field names for inline editing
const CLEANED_TO_DATA = {
  findings_summary_preview: 'findings_summary',
}

function DocResultItem({ docType, result, standards, API, jobId, setPreview }) {
  const label = (standards?.doc_labels && standards.doc_labels[docType]) || docType
  return (
    <div className="doc-result-item">
      <div>
        <div style={{ fontWeight: 600, fontSize: 13 }}>{label}</div>
        {result.error && (
          <div style={{ color: 'var(--red-600)', fontSize: 12 }}>{result.error}</div>
        )}
        {result.certification_decision && (
          <div style={{ fontSize: 11, color: 'var(--gray-600)', marginTop: 2 }}>
            Decision: <strong>{result.certification_decision}</strong>
            {result.conditions?.length > 0 && (
              <span style={{ color: 'var(--orange-600)' }}>
                {' '}({result.conditions.length} condition{result.conditions.length > 1 ? 's' : ''})
              </span>
            )}
          </div>
        )}
        {result.total_sections > 0 && (
          <div style={{ fontSize: 11, color: 'var(--gray-600)' }}>
            {result.total_sections} clauses assessed
          </div>
        )}
        {result.findings_summary_preview && (
          <div style={{ fontSize: 11, color: 'var(--gray-500)', marginTop: 2, fontStyle: 'italic' }}>
            {result.findings_summary_preview}...
          </div>
        )}
      </div>
      {result.filename && (
        <div style={{ display: 'flex', gap: 6 }}>
          <button
            className="btn btn-secondary"
            style={{ padding: '6px 12px', fontSize: 12 }}
            onClick={() => setPreview({ docType, label, result })}
          >
            Preview
          </button>
          <a
            href={`${API}/download_doc/${jobId}/${docType}`}
            className="btn btn-secondary"
            style={{ padding: '6px 12px', fontSize: 12 }}
          >
            DOCX
          </a>
          {result.pdf_filename && (
            <a
              href={`${API}/download_doc/${jobId}/${docType}/pdf`}
              className="btn btn-secondary"
              style={{ padding: '6px 12px', fontSize: 12 }}
            >
              PDF
            </a>
          )}
        </div>
      )}
    </div>
  )
}

export default function Audit({ API, standards }) {
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

  const cancelEdit = () => {
    setEditingField(null)
    setEditValue('')
  }

  const saveEdit = async () => {
    if (!editingField || !preview) return
    const beforeVal = preview.result[editingField]
    setSavingEdit(true)
    try {
      const res = await fetch(`${API}/edit-field`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_id: jobId,
          doc_type: preview.docType,
          field: dataFieldName(editingField),
          value: editValue,
        }),
      })
      const data = await res.json()
      if (data.success) {
        setPreview(prev => ({
          ...prev,
          result: { ...prev.result, [editingField]: editValue },
        }))
        if (String(beforeVal) !== String(editValue)) {
          setDiffView({ field: editingField, before: String(beforeVal || ''), after: editValue })
        }
        setEditingField(null)
        setEditValue('')
      }
    } catch {}
    setSavingEdit(false)
  }

  const refineFromEdit = () => {
    if (!editingField || !preview) return
    const df = dataFieldName(editingField)
    setRefineField(df)
    setRefineInstruction(`Replace the current value with exactly:\n${editValue}`)
    setEditingField(null)
    setEditValue('')
  }

  const isEditable = (cleanedField) => {
    if (!preview) return false
    return (REFINABLE_FIELDS[preview.docType] || []).includes(dataFieldName(cleanedField))
  }

  const handleFileSelect = (field, file) => {
    setFiles(prev => ({ ...prev, [field]: file }))
    setError(null)
  }

  const toggleStandard = (id) => {
    setSelectedStandards(prev =>
      prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id]
    )
    setError(null)
  }

  const handleUpload = async () => {
    if (!files.audit_notes || !files.manday) return
    if (selectedStandards.length === 0) return
    setLoading(true)
    setError(null)

    const form = new FormData()
    form.append('audit_notes', files.audit_notes)
    form.append('manday', files.manday)
    if (files.template) form.append('checklist_template', files.template)
    form.append('api_key', apiKey)
    form.append('standards', JSON.stringify(selectedStandards))
    if (mandayConfig) {
      form.append('manday_config', JSON.stringify(mandayConfig))
    }

    try {
      const res = await fetch(`${API}/upload`, { method: 'POST', body: form })
      const data = await res.json()
      if (data.error) { setError(data.error); setLoading(false); return }

      setJobId(data.job_id)
      if (data.manday_extracted) {
        setMandayExtracted(data.manday_extracted)
      }
      if (data.async) {
        setStep('generating')
        setElapsed(0)
        elapsedRef.current = setInterval(() => setElapsed(prev => prev + 1), 1000)
        startPolling(data.job_id)
      } else {
        setStep('apikey')
      }
    } catch (e) {
      setError('Upload failed: ' + e.message)
    }
    setLoading(false)
  }

  const handleGenerate = async () => {
    setLoading(true)
    setError(null)
    const form = new FormData()
    form.append('job_id', jobId)
    form.append('api_key', apiKey)
    form.append('standards', JSON.stringify(selectedStandards))
    if (mandayConfig) {
      form.append('manday_config', JSON.stringify(mandayConfig))
    }

    try {
      const res = await fetch(`${API}/generate`, { method: 'POST', body: form })
      const data = await res.json()
      if (data.error) { setError(data.error); setLoading(false); return }
      setStep('generating')
      setElapsed(0)
      elapsedRef.current = setInterval(() => setElapsed(prev => prev + 1), 1000)
      startPolling(data.job_id)
    } catch (e) {
      setError('Generation failed: ' + e.message)
    }
    setLoading(false)
  }

  const startPolling = (jid) => {
    const evtSource = new EventSource(`${API}/progress/${jid}`)
    evtSource.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data)
        setProgress(data)
      } catch (_) { void _ }
    }
    evtSource.addEventListener('complete', (e) => {
      try {
        const data = JSON.parse(e.data)
        if (data.results) setResults(data.results)
        setStep('done')
        clearInterval(elapsedRef.current)
      } catch (_) { void _ }
      evtSource.close()
    })
    evtSource.onerror = () => {
      // Fall back to polling if SSE fails
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

  useEffect(() => {
    return () => {
      if (pollRef.current) {
        if (typeof pollRef.current.close === 'function') pollRef.current.close()
        else clearInterval(pollRef.current)
      }
      if (elapsedRef.current) clearInterval(elapsedRef.current)
    }
  }, [])

  const handleReset = () => {
    setStep('upload')
    setFiles({ audit_notes: null, manday: null, template: null })
    setSelectedStandards([])
    setApiKey('')
    setJobId(null)
    setProgress(null)
    setResults(null)
    setMandayExtracted(null)
    setMandayConfig(null)
    setError(null)
    setLoading(false)
    setElapsed(0)
    if (pollRef.current) {
      if (typeof pollRef.current.close === 'function') pollRef.current.close()
      else clearInterval(pollRef.current)
    }
    if (elapsedRef.current) clearInterval(elapsedRef.current)
  }

  if (!standards) {
    return <div className="empty-state"><h3>Loading...</h3></div>
  }

  return (
    <div>
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
            <input
              type="file"
              className="file-input"
              accept=".docx,.txt"
              onChange={e => handleFileSelect('audit_notes', e.target.files[0])}
            />
            {files.audit_notes && <span className="file-name">{files.audit_notes.name}</span>}
          </div>

          <div className="form-group">
            <label>Manday Calculation (.docx) *</label>
            <input
              type="file"
              className="file-input"
              accept=".docx"
              onChange={e => handleFileSelect('manday', e.target.files[0])}
            />
            {files.manday && <span className="file-name">{files.manday.name}</span>}
          </div>

          <MandayForm
            standards={standards.standards}
            selectedStandards={selectedStandards}
            mandayExtracted={mandayExtracted}
            onMandayConfigChange={setMandayConfig}
          />

          <div className="form-group">
            <label>Checklist Template (optional, .docx)</label>
            <input
              type="file"
              className="file-input"
              accept=".docx"
              onChange={e => handleFileSelect('template', e.target.files[0])}
            />
            {files.template && <span className="file-name">{files.template.name}</span>}
          </div>

          <div className="form-group">
            <label>ISO Standards *</label>
            <div className="checkbox-group">
              {Object.entries(standards.standards).map(([id, label]) => (
                <div
                  key={id}
                  className={`checkbox-item ${selectedStandards.includes(id) ? 'selected' : ''}`}
                  onClick={() => toggleStandard(id)}
                >
                  <input
                    type="checkbox"
                    checked={selectedStandards.includes(id)}
                    onChange={() => {}}
                  />
                  <span>{label}</span>
                </div>
              ))}
            </div>
            {selectedStandards.length === 0 && (
              <span style={{ fontSize: 12, color: 'var(--red-600)', marginTop: 4, display: 'block' }}>
                Select at least one standard
              </span>
            )}
          </div>

          <div className="form-group">
            <label>AI Provider (optional — leave empty for local/offline mode)</label>
            <input
              type="password"
              placeholder="API key or leave empty for offline mode"
              value={apiKey}
              onChange={e => setApiKey(e.target.value)}
            />
            <div style={{ fontSize: 12, color: 'var(--gray-500)', marginTop: 4 }}>
              {!apiKey ? '🔒 Offline mode — no API key needed, content generated locally' :
               apiKey.startsWith('hf_') ? '🤗 HuggingFace Free Tier — Llama-3-8B via API' :
               '☁️ AI-powered content generation'}
            </div>
          </div>

          <button
            className="btn btn-primary"
            onClick={handleUpload}
            disabled={loading || !files.audit_notes || !files.manday || selectedStandards.length === 0}
          >
            {loading ? 'Uploading...' : 'Upload & Generate'}
          </button>
        </div>
      )}

      {step === 'apikey' && (
        <div className="card">
          <h3>API Key Required</h3>
          <p style={{ marginBottom: 16, color: 'var(--gray-600)' }}>
            Files uploaded successfully. Optionally enter an API key for AI-powered content, or leave empty for offline mode.
          </p>
          <div className="form-group">
            <label>API Key (optional for offline mode)</label>
            <input
              type="password"
              placeholder="Leave empty for local/offline mode"
              value={apiKey}
              onChange={e => setApiKey(e.target.value)}
            />
            <div style={{ fontSize: 12, color: 'var(--gray-500)', marginTop: 4 }}>
              {!apiKey ? '🔒 Offline mode — no API key needed' :
               apiKey.startsWith('hf_') ? '🤗 HuggingFace Free Tier' :
               '☁️ AI-powered mode'}
            </div>
          </div>
          <button className="btn btn-primary" onClick={handleGenerate}>
            {apiKey ? 'Generate with AI' : 'Generate Offline'}
          </button>
          <button className="btn btn-secondary" onClick={handleReset} style={{ marginLeft: 8 }}>
            Cancel
          </button>
        </div>
      )}

      {step === 'generating' && progress && (
        <div className="card">
          <h3>Generating Documents</h3>
          <p style={{ fontSize: 13, color: 'var(--gray-500)', marginBottom: 8 }}>
            {Math.floor(elapsed / 60)}m {elapsed % 60}s elapsed
          </p>
          <div className={`progress-bar ${progress.progress < 100 ? 'progress-bar-active' : ''}`}>
            <div className="progress-fill" style={{ width: `${progress.progress || 0}%` }} />
          </div>
          <p style={{ marginBottom: 12, color: 'var(--gray-600)', fontSize: 14 }}>
            {progress.progress || 0}% — {progress.current_doc || 'Starting...'}
          </p>
          {progress.doc_progress && Object.keys(progress.doc_progress).length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {Object.keys(progress.doc_progress).map(doc => (
                <div key={doc} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13 }}>
                  <span className={`status-badge ${progress.doc_progress[doc] || 'pending'}`}>
                    {progress.doc_progress[doc] === 'done' ? '✓' :
                     progress.doc_progress[doc] === 'error' ? '✗' :
                     progress.doc_progress[doc] === 'generating' ? '⟳' : '○'}
                  </span>
                  <span>{standards?.doc_labels?.[doc] || doc}</span>
                </div>
              ))}
            </div>
          )}
          {error && <div className="error-banner" style={{ marginTop: 12 }}>{error}</div>}
        </div>
      )}

      {step === 'done' && (
        <div className="card">
          <h3>Documents Generated Successfully</h3>
          <p style={{ marginBottom: 16, color: 'var(--gray-600)' }}>
            All audit documents have been created. Download individual documents or the full package.
          </p>

          {progress?.download_url && (
            <a
              href={`${API}/download/${jobId}`}
              className="btn btn-primary"
              style={{ display: 'inline-block', marginBottom: 20 }}
            >
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
                  <h4 style={{ marginBottom: 10, marginTop: 0, color: 'var(--gray-700)' }}>
                    Audit Package ({auditItems.length})
                  </h4>
                  {auditItems.map(([docType, result]) => (
                    <DocResultItem key={docType} docType={docType} result={result}
                      standards={standards} API={API} jobId={jobId} setPreview={setPreview} />
                  ))}
                  <hr style={{ margin: '20px 0', border: 'none', borderTop: '1px solid var(--gray-200)' }} />
                </>)}
                <h4 style={{ marginBottom: 10, marginTop: 0, color: 'var(--gray-700)' }}>
                  Standalone Documents ({standaloneItems.length})
                </h4>
                {standaloneItems.map(([docType, result]) => (
                  <DocResultItem key={docType} docType={docType} result={result}
                    standards={standards} API={API} jobId={jobId} setPreview={setPreview} />
                ))}
              </>)
            })()}
          </div>

          <button className="btn btn-secondary" onClick={handleReset} style={{ marginTop: 20 }}>
            Generate New Documents
          </button>
        </div>
      )}

      {preview && (
        <div className="modal-overlay" onClick={() => setPreview(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{preview.label}</h3>
              <button className="modal-close" onClick={() => setPreview(null)}>✕</button>
            </div>
            <div className="modal-body">
              {preview.result.client_name && (
                <div className="field">
                  <div className="field-label">Client</div>
                  <div className="field-value">{preview.result.client_name}</div>
                </div>
              )}
              {preview.result.standard && (
                <div className="field">
                  <div className="field-label">Standard</div>
                  <div className="field-value">{preview.result.standard}</div>
                </div>
              )}
              {preview.result.audit_date && (
                <div className="field">
                  <div className="field-label">Audit Date</div>
                  <div className="field-value">{preview.result.audit_date}</div>
                </div>
              )}
              {preview.result.lead_auditor && (
                <div className="field">
                  <div className="field-label">Lead Auditor</div>
                  <div className="field-value">{preview.result.lead_auditor}</div>
                </div>
              )}
              {preview.result.certification_decision && (
                <div className="field">
                  <div className="field-label">Decision</div>
                  <div className="field-value" style={{ cursor: isEditable('certification_decision') ? 'pointer' : 'default' }}
                    onClick={() => isEditable('certification_decision') && startEdit('certification_decision', preview.result.certification_decision)}>
                    {editingField === 'certification_decision' ? (
                      <div onClick={e => e.stopPropagation()}>
                        <textarea value={editValue} onChange={e => setEditValue(e.target.value)} rows={2}
                          style={{ width: '100%', padding: 6, fontSize: 13, border: '1px solid var(--blue-400)', borderRadius: 4 }} />
                        <div style={{ display: 'flex', gap: 6, marginTop: 4 }}>
                          <button className="btn btn-primary" style={{ padding: '4px 10px', fontSize: 11 }} onClick={saveEdit} disabled={savingEdit}>Save</button>
                          <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: 11 }} onClick={refineFromEdit}>Refine with AI</button>
                          <button style={{ padding: '4px 10px', fontSize: 11 }} onClick={cancelEdit}>Cancel</button>
                        </div>
                      </div>
                    ) : (
                      <span className={`status-badge ${preview.result.certification_decision === 'Certified' ? 'done' : 'error'}`}>
                        {preview.result.certification_decision}
                      </span>
                    )}
                  </div>
                </div>
              )}
              {preview.result.audit_type && (
                <div className="field">
                  <div className="field-label">Audit Type</div>
                  <div className="field-value">{preview.result.audit_type}</div>
                </div>
              )}
              {preview.result.total_mandays && (
                <div className="field">
                  <div className="field-label">Total Mandays</div>
                  <div className="field-value">{preview.result.total_mandays}</div>
                </div>
              )}
              {preview.result.employee_count && (
                <div className="field">
                  <div className="field-label">Employees</div>
                  <div className="field-value">{preview.result.employee_count}</div>
                </div>
              )}
              {preview.result.findings_summary_preview && (
                <div className="field">
                  <div className="field-label">Findings Summary</div>
                  <div className="field-value" style={{ cursor: isEditable('findings_summary_preview') ? 'pointer' : 'default' }}
                    onClick={() => isEditable('findings_summary_preview') && startEdit('findings_summary_preview', preview.result.findings_summary_preview)}>
                    {editingField === 'findings_summary_preview' ? (
                      <div onClick={e => e.stopPropagation()}>
                        <textarea value={editValue} onChange={e => setEditValue(e.target.value)} rows={4}
                          style={{ width: '100%', padding: 6, fontSize: 13, border: '1px solid var(--blue-400)', borderRadius: 4, resize: 'vertical' }} />
                        <div style={{ display: 'flex', gap: 6, marginTop: 4 }}>
                          <button className="btn btn-primary" style={{ padding: '4px 10px', fontSize: 11 }} onClick={saveEdit} disabled={savingEdit}>Save</button>
                          <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: 11 }} onClick={refineFromEdit}>Refine with AI</button>
                          <button style={{ padding: '4px 10px', fontSize: 11 }} onClick={cancelEdit}>Cancel</button>
                        </div>
                      </div>
                    ) : (
                      <span>{preview.result.findings_summary_preview}</span>
                    )}
                  </div>
                </div>
              )}
              {preview.result.conditions?.length > 0 && (
                <div className="field">
                  <div className="field-label">Conditions ({preview.result.conditions.length})</div>
                  <div className="field-value" style={{ cursor: isEditable('conditions') ? 'pointer' : 'default' }}
                    onClick={() => isEditable('conditions') && startEdit('conditions', preview.result.conditions.join('\n'))}>
                    {editingField === 'conditions' ? (
                      <div onClick={e => e.stopPropagation()}>
                        <textarea value={editValue} onChange={e => setEditValue(e.target.value)} rows={4}
                          style={{ width: '100%', padding: 6, fontSize: 13, border: '1px solid var(--blue-400)', borderRadius: 4, resize: 'vertical' }} />
                        <div style={{ display: 'flex', gap: 6, marginTop: 4 }}>
                          <button className="btn btn-primary" style={{ padding: '4px 10px', fontSize: 11 }} onClick={saveEdit} disabled={savingEdit}>Save</button>
                          <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: 11 }} onClick={refineFromEdit}>Refine with AI</button>
                          <button style={{ padding: '4px 10px', fontSize: 11 }} onClick={cancelEdit}>Cancel</button>
                        </div>
                      </div>
                    ) : (
                      preview.result.conditions.map((c, i) => <div key={i}>• {c}</div>)
                    )}
                  </div>
                </div>
              )}
              {preview.result.total_sections > 0 && (
                <div className="field">
                  <div className="field-label">Sections Assessed</div>
                  <div className="field-value">{preview.result.total_sections}</div>
                </div>
              )}

              <details className="refine-section" style={{ marginTop: 16 }}>
                <summary style={{ cursor: 'pointer', fontWeight: 600, fontSize: 13, color: 'var(--blue-600)' }}>
                  ✨ Refine with AI
                </summary>
                <div style={{ padding: '8px 0', display: 'flex', flexDirection: 'column', gap: 8 }}>
                  <select
                    value={refineField}
                    onChange={e => { setRefineField(e.target.value); setRefineResult(null) }}
                    style={{ padding: '6px 8px', fontSize: 13, border: '1px solid var(--gray-300)', borderRadius: 4 }}
                  >
                    <option value="">Select field to refine...</option>
                    {(REFINABLE_FIELDS[preview.docType] || []).map(f => (
                      <option key={f} value={f}>{f}</option>
                    ))}
                  </select>
                  <textarea
                    placeholder="Describe the change... (e.g. 'Make it more detailed', 'Use formal language')"
                    value={refineInstruction}
                    onChange={e => setRefineInstruction(e.target.value)}
                    rows={2}
                    style={{ padding: '6px 8px', fontSize: 13, border: '1px solid var(--gray-300)', borderRadius: 4, resize: 'vertical' }}
                  />
                  <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                    <button
                      className="btn btn-primary"
                      style={{ padding: '6px 14px', fontSize: 12 }}
                      disabled={refining || !refineField || !refineInstruction}
                      onClick={async () => {
                        setRefining(true)
                        setRefineResult(null)
                        try {
                          const res = await fetch(`${API}/refine`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                              job_id: jobId,
                              doc_type: preview.docType,
                              field: refineField,
                              instruction: refineInstruction,
                              api_key: apiKey,
                            }),
                          })
                          const data = await res.json()
                          if (data.new_value) {
                            setRefineResult({ success: true, value: data.new_value })
                            if (data.previous_value !== undefined) {
                              setDiffView({
                                field: refineField,
                                before: String(data.previous_value || ''),
                                after: data.new_value,
                              })
                            }
                          } else {
                            setRefineResult({ success: false, error: data.error || 'Refinement failed' })
                          }
                        } catch (e) {
                          setRefineResult({ success: false, error: 'Network error' })
                        }
                        setRefining(false)
                      }}
                    >
                      {refining ? 'Regenerating...' : 'Regenerate'}
                    </button>
                    <button
                      className="btn btn-secondary"
                      style={{ padding: '6px 14px', fontSize: 12 }}
                      onClick={async () => {
                        setLoadingVersions(true)
                        setVersions(null)
                        try {
                          const res = await fetch(`${API}/refine/versions/${jobId}/${preview.docType}?field=${refineField}`)
                          const data = await res.json()
                          setVersions(data.versions || [])
                        } catch {
                          setVersions([])
                        }
                        setLoadingVersions(false)
                      }}
                    >
                      {loadingVersions ? 'Loading...' : 'History'}
                    </button>
                    <button
                      className="btn btn-secondary"
                      style={{ padding: '6px 14px', fontSize: 12 }}
                      disabled={bulkRefining || !refineInstruction}
                      onClick={async () => {
                        setBulkRefining(true)
                        setBulkResult(null)
                        try {
                          const res = await fetch(`${API}/refine/bulk/${jobId}/${preview.docType}`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                              instruction: refineInstruction,
                              api_key: apiKey,
                            }),
                          })
                          const data = await res.json()
                          setBulkResult(data)
                        } catch {
                          setBulkResult({ error: 'Network error' })
                        }
                        setBulkRefining(false)
                      }}
                    >
                      {bulkRefining ? 'Refining All...' : 'Refine All'}
                    </button>
                    {refineResult?.success && (
                      <span style={{ fontSize: 12, color: 'var(--green-600)' }}>Done ✓</span>
                    )}
                    {refineResult && !refineResult.success && (
                      <span style={{ fontSize: 12, color: 'var(--red-600)' }}>{refineResult.error}</span>
                    )}
                  </div>
                  {refineResult?.success && (
                    <div style={{ fontSize: 12, color: 'var(--gray-600)', background: 'var(--gray-100)', padding: 8, borderRadius: 4, maxHeight: 150, overflow: 'auto' }}>
                      <strong>New value:</strong>
                      <pre style={{ whiteSpace: 'pre-wrap', margin: '4px 0 0', fontSize: 11 }}>{refineResult.value}</pre>
                      {diffView && diffView.field === refineField && (
                        <button className="btn btn-secondary"
                          style={{ padding: '4px 10px', fontSize: 11, marginTop: 6 }}
                          onClick={() => setDiffView(prev => ({ ...prev, show: true }))}>
                          View Diff
                        </button>
                      )}
                    </div>
                  )}
                  {bulkResult && (
                    <div style={{ fontSize: 12, color: 'var(--gray-600)', background: 'var(--gray-100)', padding: 8, borderRadius: 4 }}>
                      <strong>Bulk Refine:</strong> {bulkResult.succeeded}/{bulkResult.total} fields succeeded
                      {bulkResult.failed > 0 && <span style={{ color: 'var(--red-600)' }}>, {bulkResult.failed} failed</span>}
                      {bulkResult.results?.map((r, i) => (
                        <div key={i} style={{ marginTop: 4, padding: '4px 6px', background: '#fff', borderRadius: 3, fontSize: 11 }}>
                          <strong>{r.field}</strong>: {r.error ? <span style={{ color: 'var(--red-600)' }}>{r.error}</span> : '✓ updated'}
                        </div>
                      ))}
                    </div>
                  )}
                  {versions && (
                    <details style={{ fontSize: 12 }}>
                      <summary style={{ cursor: 'pointer', fontWeight: 600, color: 'var(--gray-600)' }}>
                        Version History ({versions.length})
                      </summary>
                      <div style={{ maxHeight: 200, overflow: 'auto', marginTop: 4 }}>
                        {versions.length === 0 ? (
                          <div style={{ color: 'var(--gray-500)', padding: 4 }}>No version history for this field</div>
                        ) : (
                          [...versions].reverse().map((v, i) => (
                            <div key={i} style={{
                              padding: '6px 8px',
                              marginBottom: 4,
                              background: i === 0 ? 'var(--blue-50, #eff6ff)' : 'transparent',
                              border: '1px solid var(--gray-200)',
                              borderRadius: 4,
                            }}>
                              <div style={{ color: 'var(--gray-500)', fontSize: 10, marginBottom: 2 }}>
                                v{versions.length - i} — {new Date(v.timestamp * 1000).toLocaleString()} — {v.instruction || 'generated'}
                              </div>
                              <pre style={{ margin: 0, whiteSpace: 'pre-wrap', fontSize: 11, maxHeight: 80, overflow: 'hidden' }}>
                                {typeof v.value === 'string' ? v.value.slice(0, 500) + (v.value.length > 500 ? '...' : '') : JSON.stringify(v.value).slice(0, 500)}
                              </pre>
                            </div>
                          ))
                        )}
                      </div>
                    </details>
                  )}
                </div>
              </details>
            </div>
            <div className="modal-footer">
              <a href={`${API}/download_doc/${jobId}/${preview.docType}`} className="btn btn-primary" style={{ fontSize: 13, padding: '8px 16px' }}>
                Download DOCX
              </a>
              {preview.result.pdf_filename && (
                <a href={`${API}/download_doc/${jobId}/${preview.docType}/pdf`} className="btn btn-secondary" style={{ fontSize: 13, padding: '8px 16px' }}>
                  Download PDF
                </a>
              )}
            </div>
          </div>
        </div>
      )}

      {diffView?.show && (
        <div className="modal-overlay" onClick={() => setDiffView(null)}>
          <div className="modal-content modal-diff" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Diff: {diffView.field}</h3>
              <button className="modal-close" onClick={() => setDiffView(null)}>✕</button>
            </div>
            <div className="modal-body">
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                <div>
                  <h4 style={{ color: 'var(--red-600)', margin: '0 0 8px', fontSize: 13 }}>Before</h4>
                  <pre style={{
                    whiteSpace: 'pre-wrap', fontSize: 12, lineHeight: 1.5,
                    background: '#fef2f2', border: '1px solid #fecaca',
                    padding: 12, borderRadius: 6, maxHeight: 400, overflow: 'auto',
                    margin: 0,
                  }}>{diffView.before || '(empty)'}</pre>
                </div>
                <div>
                  <h4 style={{ color: 'var(--green-600)', margin: '0 0 8px', fontSize: 13 }}>After</h4>
                  <pre style={{
                    whiteSpace: 'pre-wrap', fontSize: 12, lineHeight: 1.5,
                    background: '#f0fdf4', border: '1px solid #bbf7d0',
                    padding: 12, borderRadius: 6, maxHeight: 400, overflow: 'auto',
                    margin: 0,
                  }}>{diffView.after}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
