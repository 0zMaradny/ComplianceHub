import { useState, useRef, useEffect } from 'react'

export default function Audit({ API, standards }) {
  const [step, setStep] = useState('upload')
  const [files, setFiles] = useState({ audit_notes: null, manday: null, template: null })
  const [selectedStandards, setSelectedStandards] = useState([])
  const [apiKey, setApiKey] = useState('')
  const [jobId, setJobId] = useState(null)
  const [progress, setProgress] = useState(null)
  const [results, setResults] = useState(null)
  const pollRef = useRef(null)

  const handleFileSelect = (field, file) => {
    setFiles(prev => ({ ...prev, [field]: file }))
  }

  const toggleStandard = (id) => {
    setSelectedStandards(prev =>
      prev.includes(id) ? prev.filter(s => s !== id) : [...prev, id]
    )
  }

  const handleUpload = async () => {
    if (!files.audit_notes || !files.manday) return
    if (selectedStandards.length === 0) return

    const form = new FormData()
    form.append('audit_notes', files.audit_notes)
    form.append('manday', files.manday)
    if (files.template) form.append('checklist_template', files.template)
    form.append('api_key', apiKey)
    form.append('standards', JSON.stringify(selectedStandards))

    try {
      const res = await fetch(`${API}/upload`, { method: 'POST', body: form })
      const data = await res.json()
      if (data.error) { alert(data.error); return }

      setJobId(data.job_id)
      if (data.async) {
        setStep('generating')
        startPolling(data.job_id)
      } else {
        setStep('apikey')
      }
    } catch (e) {
      alert('Upload failed: ' + e.message)
    }
  }

  const handleGenerate = async () => {
    const form = new FormData()
    form.append('job_id', jobId)
    form.append('api_key', apiKey)
    form.append('standards', JSON.stringify(selectedStandards))

    try {
      const res = await fetch(`${API}/generate`, { method: 'POST', body: form })
      const data = await res.json()
      if (data.error) { alert(data.error); return }
      setStep('generating')
      startPolling(data.job_id)
    } catch (e) {
      alert('Generation failed: ' + e.message)
    }
  }

  const startPolling = (jid) => {
    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${API}/status/${jid}`)
        const data = await res.json()
        setProgress(data)
        if (data.status === 'done' || data.error) {
          clearInterval(pollRef.current)
          if (data.results) setResults(data.results)
          if (data.status === 'done') setStep('done')
        }
      } catch (e) { console.error('Poll error:', e) }
    }, 1500)
  }

  useEffect(() => {
    return () => { if (pollRef.current) clearInterval(pollRef.current) }
  }, [])

  const handleReset = () => {
    setStep('upload')
    setFiles({ audit_notes: null, manday: null, template: null })
    setSelectedStandards([])
    setApiKey('')
    setJobId(null)
    setProgress(null)
    setResults(null)
    if (pollRef.current) clearInterval(pollRef.current)
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

          <div className="form-group">
            <label>Audit Notes (.docx or .txt) *</label>
            <input
              type="file"
              className="file-input"
              accept=".docx,.txt"
              onChange={e => handleFileSelect('audit_notes', e.target.files[0])}
            />
          </div>

          <div className="form-group">
            <label>Manday Calculation (.docx) *</label>
            <input
              type="file"
              className="file-input"
              accept=".docx"
              onChange={e => handleFileSelect('manday', e.target.files[0])}
            />
          </div>

          <div className="form-group">
            <label>Checklist Template (optional, .docx)</label>
            <input
              type="file"
              className="file-input"
              accept=".docx"
              onChange={e => handleFileSelect('template', e.target.files[0])}
            />
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
            disabled={!files.audit_notes || !files.manday || selectedStandards.length === 0}
          >
            Upload & Generate
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
          <div className="progress-bar">
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
            {results && Object.entries(results).map(([docType, result]) => (
              <div key={docType} className="doc-result-item">
                <div>
                  <div style={{ fontWeight: 600, fontSize: 13 }}>
                    {standards.doc_labels[docType] || docType}
                  </div>
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
                  <a
                    href={`${API}/download_doc/${jobId}/${docType}`}
                    className="btn btn-secondary"
                    style={{ padding: '6px 12px', fontSize: 12 }}
                  >
                    Download
                  </a>
                )}
              </div>
            ))}
          </div>

          <button className="btn btn-secondary" onClick={handleReset} style={{ marginTop: 20 }}>
            Generate New Documents
          </button>
        </div>
      )}
    </div>
  )
}
