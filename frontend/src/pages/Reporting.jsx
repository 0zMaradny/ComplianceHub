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
      <div className="page-header">
        <h2>Reporting</h2>
        <p>Generate and export compliance reports and data</p>
      </div>

      {message && (
        <div className={`px-3 py-2 mb-3 rounded-md text-sm ${message.startsWith('Error') ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}`}>
          {message}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* PDF Report */}
        <div className="card">
          <h3>PDF Summary Report</h3>
          <div className="mt-3">
            <label className="block mb-2 text-sm" style={{ color: 'var(--text-secondary)' }}>Report Type</label>
            <select value={reportType} onChange={e => setReportType(e.target.value)}
              className="w-full p-2 rounded-md text-sm mb-3"
              style={{ border: '1px solid var(--border-color)' }}>
              <option value="compliance_summary">Compliance Summary</option>
              <option value="project_overview">Project Overview</option>
            </select>
            <label className="block mb-2 text-sm" style={{ color: 'var(--text-secondary)' }}>Project ID (optional)</label>
            <input type="text" value={projectId} onChange={e => setProjectId(e.target.value)}
              placeholder="Leave empty for all projects"
              className="w-full p-2 rounded-md text-sm mb-3"
              style={{ border: '1px solid var(--border-color)' }} />
            <button className="btn btn-primary w-full" onClick={generatePdf} disabled={generating}>
              {generating ? <><Spinner size="sm" className="mr-1.5" />Generating...</> : 'Download PDF Report'}
            </button>
          </div>
        </div>

        {/* CSV Export */}
        <div className="card">
          <h3>CSV Data Export</h3>
          <div className="mt-3">
            <label className="block mb-2 text-sm" style={{ color: 'var(--text-secondary)' }}>Dataset</label>
            <select value={csvDataset} onChange={e => setCsvDataset(e.target.value)}
              className="w-full p-2 rounded-md text-sm mb-3"
              style={{ border: '1px solid var(--border-color)' }}>
              <option value="nc_trends">NC Trends</option>
              <option value="project_health">Project Health</option>
              <option value="capa_metrics">CAPA Metrics</option>
              <option value="ai_usage">AI Usage</option>
            </select>
            {csvDataset === 'nc_trends' && (
              <>
                <label className="block mb-2 text-sm" style={{ color: 'var(--text-secondary)' }}>Months</label>
                <input type="number" value={months} onChange={e => setMonths(Number(e.target.value))} min={1} max={24}
                  className="w-full p-2 rounded-md text-sm mb-3"
                  style={{ border: '1px solid var(--border-color)' }} />
              </>
            )}
            <button className="btn btn-primary w-full" onClick={downloadCsv} disabled={generating}>
              {generating ? <><Spinner size="sm" className="mr-1.5" />Downloading...</> : 'Download CSV'}
            </button>
          </div>
        </div>
      </div>

      {/* Quick export buttons for Dashboard integration */}
      <div className="card mt-4">
        <h3>Quick Links</h3>
        <div className="flex gap-3 flex-wrap mt-2">
          {['dashboard', 'analytics', 'compliance'].map(page => (
            <a key={page} href={`#${page}`}
              onClick={e => { e.preventDefault(); window.dispatchEvent(new CustomEvent('navigate', { detail: page })) }}
              className="btn btn-secondary capitalize">{page}</a>
          ))}
        </div>
      </div>
    </div>
  )
}
