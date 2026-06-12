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
      <div className="mb-8 flex justify-between items-start">
        <div>
          <h2 className="text-3xl font-bold text-[var(--text-primary)] m-0">Template Manager</h2>
          <p className="mt-1 text-[var(--text-secondary)]">Manage TÜV Austria document and checklist templates</p>
        </div>
        <label className="bg-[var(--primary)] text-white hover:bg-[var(--primary-dark)] disabled:opacity-50 disabled:cursor-not-allowed px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center border-none transition-all duration-150 cursor-pointer whitespace-nowrap">
          {uploading ? 'Uploading...' : 'Upload Template'}
          <input type="file" accept=".docx,.xlsx,.doc" onChange={handleUpload} className="sr-only" disabled={uploading} />
        </label>
      </div>

      {error && <div className="px-3.5 py-2.5 rounded-lg text-xs font-medium mb-4 bg-red-50 border border-red-600 text-red-600">{error}</div>}

      {loading ? (
        <div className="animate-fadeIn">
          <Skeleton variant="card" height="200px" className="mb-4" />
          <Skeleton variant="card" height="200px" />
        </div>
      ) : templates.length === 0 ? (
        <div className="text-center p-12 text-[var(--text-secondary)]">No templates found.</div>
      ) : (
        <div className="animate-slideIn">
          <div className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)]">
            <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">Document Templates ({docTemplates.length})</h3>
            <div className="grid gap-2 grid-cols-[repeat(auto-fill,minmax(280px,1fr))]">
              {docTemplates.map(t => (
                <div key={t.filename} className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs border border-[var(--border-color)] justify-between">
                  <div>
                    <div className="font-semibold text-sm">{t.doc_type || t.filename}</div>
                    <div className="text-xs text-[var(--text-secondary)]">{t.filename}</div>
                  </div>
                  <button className="text-xs px-2.5 py-1 rounded-md bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200 dark:bg-gray-200 dark:text-gray-800 inline-flex items-center justify-center transition-all duration-150 cursor-pointer whitespace-nowrap text-red-500" onClick={() => handleDelete(t.filename)}>Delete</button>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)]">
            <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">Checklist Templates ({checklistTemplates.length})</h3>
            <div className="grid gap-2 grid-cols-[repeat(auto-fill,minmax(280px,1fr))]">
              {checklistTemplates.map(t => (
                <div key={t.filename} className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs border border-[var(--border-color)] justify-between">
                  <div>
                    <div className="font-semibold text-sm">{t.standard_key || t.filename}</div>
                    <div className="text-xs text-[var(--text-secondary)]">{t.filename}</div>
                  </div>
                  <button className="text-xs px-2.5 py-1 rounded-md bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200 dark:bg-gray-200 dark:text-gray-800 inline-flex items-center justify-center transition-all duration-150 cursor-pointer whitespace-nowrap text-red-500" onClick={() => handleDelete(t.filename)}>Delete</button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
