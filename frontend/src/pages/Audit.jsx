import { useState, useRef, useEffect } from 'react'
import MandayForm from '../components/MandayForm'

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
  const pollRef = useRef(null)
  const elapsedRef = useRef(null)

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
                  <div className="field-value">
                    <span className={`status-badge ${preview.result.certification_decision === 'Certified' ? 'done' : 'error'}`}>
                      {preview.result.certification_decision}
                    </span>
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
                  <div className="field-value">{preview.result.findings_summary_preview}</div>
                </div>
              )}
              {preview.result.conditions?.length > 0 && (
                <div className="field">
                  <div className="field-label">Conditions ({preview.result.conditions.length})</div>
                  <div className="field-value">
                    {preview.result.conditions.map((c, i) => (
                      <div key={i}>• {c}</div>
                    ))}
                  </div>
                </div>
              )}
              {preview.result.total_sections > 0 && (
                <div className="field">
                  <div className="field-label">Sections Assessed</div>
                  <div className="field-value">{preview.result.total_sections}</div>
                </div>
              )}
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
    </div>
  )
}
