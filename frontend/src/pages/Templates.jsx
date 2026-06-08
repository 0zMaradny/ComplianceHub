
import { useState, useEffect, startTransition } from 'react'

export default function Templates({ API }) {
  const [templates, setTemplates] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    startTransition(() => setLoading(true))
    fetch(`${API}/templates`)
      .then(r => r.json())
      .then(data => {
        const all = []
        for (const t of (data.document_templates || [])) {
          all.push({ ...t, category: 'document' })
        }
        for (const t of (data.checklist_templates || [])) {
          all.push({ ...t, category: 'checklist' })
        }
        setTemplates(all)
        setLoading(false)
      })
      .catch(e => { setError(e.message); setLoading(false) })
  }, [API])

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setUploading(true)
    const form = new FormData()
    form.append('file', file)
    try {
      const r = await fetch(`${API}/templates/upload`, { method: 'POST', body: form })
      const data = await r.json()
      if (!r.ok) { alert(data.detail || 'Upload failed') }
      else {
        setLoading(true)
        fetch(`${API}/templates`)
          .then(r => r.json())
          .then(data => {
            const all = []
            for (const t of (data.document_templates || [])) {
              all.push({ ...t, category: 'document' })
            }
            for (const t of (data.checklist_templates || [])) {
              all.push({ ...t, category: 'checklist' })
            }
            setTemplates(all)
            setLoading(false)
          })
          .catch(e => { setError(e.message); setLoading(false) })
      }
    } catch { alert('Upload failed') }
    setUploading(false)
    e.target.value = ''
  }

  const handleDelete = async (filename) => {
    if (!confirm(`Delete "${filename}"?`)) return
    try {
      const r = await fetch(`${API}/templates/${encodeURIComponent(filename)}`, { method: 'DELETE' })
      if (r.ok) {
        setLoading(true)
        fetch(`${API}/templates`)
          .then(r => r.json())
          .then(data => {
            const all = []
            for (const t of (data.document_templates || [])) {
              all.push({ ...t, category: 'document' })
            }
            for (const t of (data.checklist_templates || [])) {
              all.push({ ...t, category: 'checklist' })
            }
            setTemplates(all)
            setLoading(false)
          })
          .catch(e => { setError(e.message); setLoading(false) })
      } else { const d = await r.json(); alert(d.detail || 'Delete failed') }
    } catch { alert('Delete failed') }
  }

  const docTemplates = templates.filter(t => t.category === 'document')
  const checklistTemplates = templates.filter(t => t.category === 'checklist')

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2>Template Manager</h2>
          <p>Manage TÜV Austria document and checklist templates</p>
        </div>
        <label className="btn btn-primary" style={{ cursor: 'pointer', fontSize: 13 }}>
          {uploading ? 'Uploading...' : 'Upload Template'}
          <input type="file" accept=".docx,.xlsx,.doc" onChange={handleUpload} style={{ display: 'none' }} disabled={uploading} />
        </label>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {loading ? (
        <div className="loading">Loading...</div>
      ) : templates.length === 0 ? (
        <div className="empty-state">No templates found.</div>
      ) : (
        <>
          <div className="card">
            <h3>Document Templates ({docTemplates.length})</h3>
            <div className="checkbox-group">
              {docTemplates.map(t => (
                <div key={t.filename} className="checkbox-item" style={{ justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 13 }}>{t.doc_type || t.filename}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>{t.filename}</div>
                  </div>
                  <button className="btn btn-small btn-secondary" onClick={() => handleDelete(t.filename)}
                          style={{ color: 'var(--red-500)' }}>Delete</button>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <h3>Checklist Templates ({checklistTemplates.length})</h3>
            <div className="checkbox-group">
              {checklistTemplates.map(t => (
                <div key={t.filename} className="checkbox-item" style={{ justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 13 }}>{t.standard_key || t.filename}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>{t.filename}</div>
                  </div>
                  <button className="btn btn-small btn-secondary" onClick={() => handleDelete(t.filename)}
                          style={{ color: 'var(--red-500)' }}>Delete</button>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
