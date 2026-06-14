import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useToast } from '../hooks/useToast'
import Spinner from '../components/Spinner'

function downloadBlob(url, filename) {
  const a = document.createElement('a')
  a.href = url; a.download = filename
  document.body.appendChild(a); a.click()
  document.body.removeChild(a)
}

export default function Reporting({ API }) {
  const { t } = useTranslation()
  const showToast = useToast()
  const [reportType, setReportType] = useState('compliance_summary')
  const [projectId, setProjectId] = useState('')
  const [csvDataset, setCsvDataset] = useState('nc_trends')
  const [months, setMonths] = useState(6)
  const [generating, setGenerating] = useState(false)
  const [message, setMessage] = useState('')

  const generatePdf = async () => {
    setGenerating(true); setMessage('')
    try {
      const params = new URLSearchParams({ report_type: reportType })
      if (projectId) params.set('project_id', projectId)
      const resp = await fetch(`${API}/export/report?${params}`)
      if (!resp.ok) { const err = await resp.text(); setMessage(t('reporting.error') + err); showToast(err, 'error'); return }
      const blob = await resp.blob()
      const url = URL.createObjectURL(blob)
      downloadBlob(url, reportType === 'project_overview' ? 'project_overview.pdf' : 'compliance_summary.pdf')
      URL.revokeObjectURL(url)
      setMessage(t('reporting.pdf_success')); showToast(t('reporting.pdf_success'), 'success')
    } catch (e) { setMessage(t('reporting.error') + e.message); showToast(e.message, 'error') }
    finally { setGenerating(false) }
  }

  const downloadCsv = async () => {
    setGenerating(true); setMessage('')
    try {
      const params = new URLSearchParams({ dataset: csvDataset, months: String(months) })
      if (projectId) params.set('project_id', projectId)
      const resp = await fetch(`${API}/export/csv?${params}`)
      if (!resp.ok) { const err = await resp.text(); setMessage(t('reporting.error') + err); showToast(err, 'error'); return }
      const blob = await resp.blob()
      const url = URL.createObjectURL(blob)
      downloadBlob(url, `${csvDataset}.csv`)
      URL.revokeObjectURL(url)
      setMessage(t('reporting.csv_success')); showToast(t('reporting.csv_success'), 'success')
    } catch (e) { setMessage(t('reporting.error') + e.message); showToast(e.message, 'error') }
    finally { setGenerating(false) }
  }

  return (
    <div className="animate-fadeIn">
      <div className="page-header">
        <h2>{t('reporting.title')}</h2>
        <p>{t('reporting.subtitle')}</p>
      </div>

      {message && (
        <div className={`px-3 py-2 mb-3 rounded-md text-sm ${message.startsWith('Error') ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}`}>
          {message}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* PDF Report */}
        <div className="card">
          <h3 className="card-header">{t('reporting.pdf_report')}</h3>
          <div className="card-body">
            <label className="block mb-2 text-sm text-[var(--text-secondary)]">{t('reporting.report_type')}</label>
            <select value={reportType} onChange={e => setReportType(e.target.value)}
              className="input mb-3">
              <option value="compliance_summary">{t('reporting.compliance_summary')}</option>
              <option value="project_overview">{t('reporting.project_overview')}</option>
            </select>
            <label className="block mb-2 text-sm text-[var(--text-secondary)]">{t('reporting.project_id')}</label>
            <input type="text" value={projectId} onChange={e => setProjectId(e.target.value)}
              placeholder={t('reporting.project_id_hint')}
              className="input mb-3" />
            <button className="btn btn-primary w-full" onClick={generatePdf} disabled={generating}>
              {generating ? <><Spinner size="sm" className="mr-1.5" />{t('reporting.generating')}</> : t('reporting.download_pdf')}
            </button>
          </div>
        </div>

        {/* CSV Export */}
        <div className="card">
          <h3 className="card-header">{t('reporting.csv_export')}</h3>
          <div className="card-body">
            <label className="block mb-2 text-sm text-[var(--text-secondary)]">{t('reporting.dataset')}</label>
            <select value={csvDataset} onChange={e => setCsvDataset(e.target.value)}
              className="input mb-3">
              <option value="nc_trends">{t('reporting.nc_trends')}</option>
              <option value="project_health">{t('reporting.project_health')}</option>
              <option value="capa_metrics">{t('reporting.capa_metrics')}</option>
              <option value="ai_usage">{t('reporting.ai_usage')}</option>
            </select>
            {csvDataset === 'nc_trends' && (
              <>
                <label className="block mb-2 text-sm text-[var(--text-secondary)]">{t('reporting.months')}</label>
                <input type="number" value={months} onChange={e => setMonths(Number(e.target.value))} min={1} max={24}
                  className="input mb-3" />
              </>
            )}
            <button className="btn btn-primary w-full" onClick={downloadCsv} disabled={generating}>
              {generating ? <><Spinner size="sm" className="mr-1.5" />{t('reporting.downloading')}</> : t('reporting.download_csv')}
            </button>
          </div>
        </div>
      </div>

      {/* Quick export buttons for Dashboard integration */}
      <div className="card mt-4">
        <h3 className="card-header">{t('reporting.quick_links')}</h3>
        <div className="card-body">
          <div className="flex gap-3 flex-wrap">
            {['dashboard', 'analytics', 'compliance'].map(page => (
              <a key={page} href={`#${page}`}
                onClick={e => { e.preventDefault(); window.dispatchEvent(new CustomEvent('navigate', { detail: page })) }}
                className="btn btn-secondary capitalize">{t('reporting.link_' + page)}</a>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
