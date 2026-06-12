import { useState, useEffect, startTransition } from 'react'
import Skeleton from '../components/Skeleton'
import { useToast } from '../components/Toast'

export default function Templates({ API }) {
  const showToast = useToast()
  const [templates, setTemplates] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [uploading, setUploading] = useState(false)

  const loadTemplates = () => {
    fetch(`${API}/templates`)
      .then(r => r.json())
      .then(data => {
        const all = []
        for (const t of (data.document_templates || [])) all.push({ ...t, category: 'document' })
        for (const t of (data.checklist_templates || [])) all.push({ ...t, category: 'checklist' })
        setTemplates(all)
        setLoading(false)
      })
      .catch(e => { setError(e.message); setLoading(false) })
  }

  useEffect(() => {
    startTransition(() => setLoading(true))
    loadTemplates()
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
      if (!r.ok) { showToast(data.detail || 'Upload failed', 'error') }
      else { showToast('Template uploaded successfully', 'success'); setLoading(true); loadTemplates() }
    } catch { showToast('Upload failed', 'error') }
    setUploading(false)
    e.target.value = ''
  }

  const handleDelete = async (filename) => {
    if (!confirm(`Delete "${filename}"?`)) return
    try {
      const r = await fetch(`${API}/templates/${encodeURIComponent(filename)}`, { method: 'DELETE' })
      if (r.ok) { showToast('Template deleted', 'success'); setLoading(true); loadTemplates() }
      else { const d = await r.json(); showToast(d.detail || 'Delete failed', 'error') }
    } catch { showToast('Delete failed', 'error') }
  }

  const docTemplates = templates.filter(t => t.category === 'document')
  const checklistTemplates = templates.filter(t => t.category === 'checklist')

  return (
    <div className="animate-fadeIn">
      <div className="page-header flex justify-between items-start">
        <div>
          <h2>Template Manager</h2>
          <p>Manage TÜV Austria document and checklist templates</p>
        </div>
        <label className="btn btn-primary cursor-pointer text-sm">
          {uploading ? 'Uploading...' : 'Upload Template'}
          <input type="file" accept=".docx,.xlsx,.doc" onChange={handleUpload} className="hidden" disabled={uploading} />
        </label>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {loading ? (
        <div className="animate-fadeIn">
          <Skeleton variant="card" height="200px" className="mb-4" />
          <Skeleton variant="card" height="200px" />
        </div>
      ) : templates.length === 0 ? (
        <div className="empty-state">No templates found.</div>
      ) : (
        <div className="animate-slideIn">
          <div className="card">
            <h3>Document Templates ({docTemplates.length})</h3>
            <div className="checkbox-group">
              {docTemplates.map(t => (
                <div key={t.filename} className="checkbox-item justify-between">
                  <div>
                    <div className="font-semibold text-sm">{t.doc_type || t.filename}</div>
                    <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>{t.filename}</div>
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
                <div key={t.filename} className="checkbox-item justify-between">
                  <div>
                    <div className="font-semibold text-sm">{t.standard_key || t.filename}</div>
                    <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>{t.filename}</div>
                  </div>
                  <button className="btn btn-small btn-secondary" onClick={() => handleDelete(t.filename)}
                          style={{ color: 'var(--red-500)' }}>Delete</button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
