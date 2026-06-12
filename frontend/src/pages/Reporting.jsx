import { useState } from 'react'
import { useToast } from '../components/Toast'
import Spinner from '../components/Spinner'

function downloadBlob(url, filename) {
  const a = document.createElement('a')
  a.href = url; a.download = filename
  document.body.appendChild(a); a.click()
  document.body.removeChild(a)
}

export default function Reporting({ API }) {
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
      if (!resp.ok) { const err = await resp.text(); setMessage(`Error: ${err}`); showToast(err, 'error'); return }
      const blob = await resp.blob()
      const url = URL.createObjectURL(blob)
      downloadBlob(url, reportType === 'project_overview' ? 'project_overview.pdf' : 'compliance_summary.pdf')
      URL.revokeObjectURL(url)
      setMessage('PDF downloaded successfully'); showToast('PDF downloaded', 'success')
    } catch (e) { setMessage(`Error: ${e.message}`); showToast(e.message, 'error') }
    finally { setGenerating(false) }
  }

  const downloadCsv = async () => {
    setGenerating(true); setMessage('')
    try {
      const params = new URLSearchParams({ dataset: csvDataset, months: String(months) })
      if (projectId) params.set('project_id', projectId)
      const resp = await fetch(`${API}/export/csv?${params}`)
      if (!resp.ok) { const err = await resp.text(); setMessage(`Error: ${err}`); showToast(err, 'error'); return }
      const blob = await resp.blob()
      const url = URL.createObjectURL(blob)
      downloadBlob(url, `${csvDataset}.csv`)
      URL.revokeObjectURL(url)
      setMessage('CSV downloaded successfully'); showToast('CSV downloaded', 'success')
    } catch (e) { setMessage(`Error: ${e.message}`); showToast(e.message, 'error') }
    finally { setGenerating(false) }
  }

  return (
    <div className="animate-fadeIn">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-[var(--text-primary)]">Reporting</h2>
        <p className="mt-1 text-[var(--text-secondary)]">Generate and export compliance reports and data</p>
      </div>

      {message && (
        <div className={`px-3 py-2 mb-3 rounded-md text-sm ${message.startsWith('Error') ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}`}>
          {message}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* PDF Report */}
        <div className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)]">
          <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">PDF Summary Report</h3>
          <div className="mt-3">
            <label className="block mb-2 text-sm text-[var(--text-secondary)]">Report Type</label>
            <select value={reportType} onChange={e => setReportType(e.target.value)}
              className="w-full p-2 rounded-md text-sm mb-3 border border-[var(--border-color)]">
              <option value="compliance_summary">Compliance Summary</option>
              <option value="project_overview">Project Overview</option>
            </select>
            <label className="block mb-2 text-sm text-[var(--text-secondary)]">Project ID (optional)</label>
            <input type="text" value={projectId} onChange={e => setProjectId(e.target.value)}
              placeholder="Leave empty for all projects"
              className="w-full p-2 rounded-md text-sm mb-3 border border-[var(--border-color)]" />
            <button className="bg-[var(--primary)] text-white hover:bg-[var(--primary-dark)] disabled:opacity-50 disabled:cursor-not-allowed px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center border-none transition-all duration-150 cursor-pointer whitespace-nowrap w-full" onClick={generatePdf} disabled={generating}>
              {generating ? <><Spinner size="sm" className="mr-1.5" />Generating...</> : 'Download PDF Report'}
            </button>
          </div>
        </div>

        {/* CSV Export */}
        <div className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)]">
          <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">CSV Data Export</h3>
          <div className="mt-3">
            <label className="block mb-2 text-sm text-[var(--text-secondary)]">Dataset</label>
            <select value={csvDataset} onChange={e => setCsvDataset(e.target.value)}
              className="w-full p-2 rounded-md text-sm mb-3 border border-[var(--border-color)]">
              <option value="nc_trends">NC Trends</option>
              <option value="project_health">Project Health</option>
              <option value="capa_metrics">CAPA Metrics</option>
              <option value="ai_usage">AI Usage</option>
            </select>
            {csvDataset === 'nc_trends' && (
              <>
                <label className="block mb-2 text-sm text-[var(--text-secondary)]">Months</label>
                <input type="number" value={months} onChange={e => setMonths(Number(e.target.value))} min={1} max={24}
                  className="w-full p-2 rounded-md text-sm mb-3 border border-[var(--border-color)]" />
              </>
            )}
            <button className="bg-[var(--primary)] text-white hover:bg-[var(--primary-dark)] disabled:opacity-50 disabled:cursor-not-allowed px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center border-none transition-all duration-150 cursor-pointer whitespace-nowrap w-full" onClick={downloadCsv} disabled={generating}>
              {generating ? <><Spinner size="sm" className="mr-1.5" />Downloading...</> : 'Download CSV'}
            </button>
          </div>
        </div>
      </div>

      {/* Quick export buttons for Dashboard integration */}
      <div className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)] mt-4">
        <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">Quick Links</h3>
        <div className="flex gap-3 flex-wrap mt-2">
          {['dashboard', 'analytics', 'compliance'].map(page => (
            <a key={page} href={`#${page}`}
              onClick={e => { e.preventDefault(); window.dispatchEvent(new CustomEvent('navigate', { detail: page })) }}
              className="bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200 dark:bg-gray-200 dark:text-gray-800 px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center transition-all duration-150 cursor-pointer whitespace-nowrap capitalize">{page}</a>
          ))}
        </div>
      </div>
    </div>
  )
}
