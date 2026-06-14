import { useState, useEffect, startTransition } from 'react'
import { useTranslation } from 'react-i18next'
import Skeleton from '../components/Skeleton'
import { useToast } from '../hooks/useToast'

export default function Templates({ API }) {
  const { t } = useTranslation()
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
  }, [API]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setUploading(true)
    const form = new FormData()
    form.append('file', file)
    try {
      const r = await fetch(`${API}/templates/upload`, { method: 'POST', body: form })
      const data = await r.json()
      if (!r.ok) { showToast(data.detail || t('templates.upload_failed'), 'error') }
      else { showToast(t('templates.uploaded'), 'success'); setLoading(true); loadTemplates() }
    } catch { showToast(t('templates.upload_failed'), 'error') }
    setUploading(false)
    e.target.value = ''
  }

  const handleDelete = async (filename) => {
    if (!confirm(`${t('templates.delete')} "${filename}"?`)) return
    try {
      const r = await fetch(`${API}/templates/${encodeURIComponent(filename)}`, { method: 'DELETE' })
      if (r.ok) { showToast(t('templates.deleted'), 'success'); setLoading(true); loadTemplates() }
      else { const d = await r.json(); showToast(d.detail || t('templates.delete_failed'), 'error') }
    } catch { showToast(t('templates.delete_failed'), 'error') }
  }

  const docTemplates = templates.filter(t => t.category === 'document')
  const checklistTemplates = templates.filter(t => t.category === 'checklist')

  return (
    <div className="animate-pageIn">
      <div className="page-header">
        <h2>{t('templates.title')}</h2>
        <p>{t('templates.subtitle')}</p>
      </div>

      <div className="mb-8 flex justify-end">
        <label className="btn btn-primary">
          {uploading ? t('templates.uploading') : t('templates.upload')}
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
        <div className="card">
          <div className="card-body text-center text-[var(--text-secondary)]">{t('templates.empty')}</div>
        </div>
      ) : (
        <div className="animate-slideIn">
          <div className="card mb-5">
            <div className="card-header">{t('templates.doc_templates')} ({docTemplates.length})</div>
            <div className="card-body grid gap-2 grid-cols-[repeat(auto-fill,minmax(280px,1fr))]">
              {docTemplates.map(tmpl => (
                <div key={tmpl.filename} className="flex items-center justify-between px-3 py-2 rounded-lg border border-[var(--border-color)] hover:border-[var(--primary)] transition-colors">
                  <div>
                    <div className="font-semibold text-sm">{tmpl.doc_type || tmpl.filename}</div>
                    <div className="text-xs text-[var(--text-secondary)]">{tmpl.filename}</div>
                  </div>
                  <button className="btn btn-ghost" style={{color: 'var(--red-600)'}} onClick={() => handleDelete(tmpl.filename)}>{t('templates.delete')}</button>
                </div>
              ))}
            </div>
          </div>

          <div className="card mb-5">
            <div className="card-header">{t('templates.checklist_templates')} ({checklistTemplates.length})</div>
            <div className="card-body grid gap-2 grid-cols-[repeat(auto-fill,minmax(280px,1fr))]">
              {checklistTemplates.map(tmpl => (
                <div key={tmpl.filename} className="flex items-center justify-between px-3 py-2 rounded-lg border border-[var(--border-color)] hover:border-[var(--primary)] transition-colors">
                  <div>
                    <div className="font-semibold text-sm">{tmpl.standard_key || tmpl.filename}</div>
                    <div className="text-xs text-[var(--text-secondary)]">{tmpl.filename}</div>
                  </div>
                  <button className="btn btn-ghost" style={{color: 'var(--red-600)'}} onClick={() => handleDelete(tmpl.filename)}>{t('templates.delete')}</button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
