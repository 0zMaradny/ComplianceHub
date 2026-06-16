import { useState } from 'react'
import { useTranslation } from 'react-i18next'

export default function DocPreview({ API, jobId, docType, label, onClose }) {
  const { t } = useTranslation()
  const [mode, setMode] = useState('pdf')

  const pdfUrl = `${API}/download_doc/${jobId}/${docType}/pdf`
  const docxUrl = `${API}/download_doc/${jobId}/${docType}`

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-fadeIn"
      onClick={onClose}>
      <div className="rounded-xl w-[90vw] h-[85vh] flex flex-col bg-[var(--bg-card)] shadow-xl animate-scaleIn"
        onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between px-5 py-3 border-b border-[var(--border-color)] shrink-0">
          <div className="flex items-center gap-3">
            <h3 className="m-0 text-sm font-semibold text-[var(--text-primary)]">{label}</h3>
            <div className="flex gap-1">
              <button onClick={() => setMode('pdf')}
                className={`px-3 py-1 text-xs font-medium rounded-md cursor-pointer border-none transition-all ${
                  mode === 'pdf'
                    ? 'bg-[var(--primary)] text-white'
                    : 'bg-[var(--gray-100)] text-[var(--text-secondary)]'
                }`}>
                PDF
              </button>
              <button onClick={() => setMode('docx')}
                className={`px-3 py-1 text-xs font-medium rounded-md cursor-pointer border-none transition-all ${
                  mode === 'docx'
                    ? 'bg-[var(--primary)] text-white'
                    : 'bg-[var(--gray-100)] text-[var(--text-secondary)]'
                }`}>
                DOCX
              </button>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <a href={pdfUrl} target="_blank" rel="noopener noreferrer" className="btn btn-secondary"
              style={{ fontSize: 11, padding: '4px 10px' }}>
              {t('history.open_tab')}
            </a>
            <button className="w-7 h-7 flex items-center justify-center rounded-md cursor-pointer border-none bg-transparent text-[var(--text-secondary)] hover:bg-[var(--gray-100)]"
              onClick={onClose}>✕</button>
          </div>
        </div>
        <div className="flex-1 min-h-0 bg-[var(--gray-50)]">
          {mode === 'pdf' ? (
            <iframe src={pdfUrl} className="w-full h-full border-none" title={label} />
          ) : (
            <iframe src={docxUrl} className="w-full h-full border-none" title={label} />
          )}
        </div>
      </div>
    </div>
  )
}
