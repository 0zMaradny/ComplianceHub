import { useState } from 'react'

function downloadBlob(url, filename) {
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

export default function Reporting({ API }) {
  const [reportType, setReportType] = useState('compliance_summary')
  const [projectId, setProjectId] = useState('')
  const [csvDataset, setCsvDataset] = useState('nc_trends')
  const [months, setMonths] = useState(6)
  const [generating, setGenerating] = useState(false)
  const [message, setMessage] = useState('')

  const generatePdf = async () => {
    setGenerating(true)
    setMessage('')
    try {
      const params = new URLSearchParams({ report_type: reportType })
      if (projectId) params.set('project_id', projectId)
      const resp = await fetch(`${API}/export/report?${params}`)
      if (!resp.ok) {
        const err = await resp.text()
        setMessage(`Error: ${err}`)
        return
      }
      const blob = await resp.blob()
      const url = URL.createObjectURL(blob)
      const filename = reportType === 'project_overview' ? 'project_overview.pdf' : 'compliance_summary.pdf'
      downloadBlob(url, filename)
      URL.revokeObjectURL(url)
      setMessage('PDF downloaded successfully')
    } catch (e) {
      setMessage(`Error: ${e.message}`)
    } finally {
      setGenerating(false)
    }
  }

  const downloadCsv = async () => {
    setGenerating(true)
    setMessage('')
    try {
      const params = new URLSearchParams({ dataset: csvDataset, months: String(months) })
      if (projectId) params.set('project_id', projectId)
      const resp = await fetch(`${API}/export/csv?${params}`)
      if (!resp.ok) {
        const err = await resp.text()
        setMessage(`Error: ${err}`)
        return
      }
      const blob = await resp.blob()
      const url = URL.createObjectURL(blob)
      const filename = `${csvDataset}.csv`
      downloadBlob(url, filename)
      URL.revokeObjectURL(url)
      setMessage('CSV downloaded successfully')
    } catch (e) {
      setMessage(`Error: ${e.message}`)
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div>
      <div className="page-header">
        <h2>Reporting</h2>
        <p>Generate and export compliance reports and data</p>
      </div>

      {message && (
        <div style={{ padding: '8px 12px', marginBottom: 12, borderRadius: 6, background: message.startsWith('Error') ? '#fdecea' : '#e8f5e9', color: message.startsWith('Error') ? '#c62828' : '#2e7d32', fontSize: 13 }}>
          {message}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        {/* PDF Report */}
        <div className="card">
          <h3>PDF Summary Report</h3>
          <div style={{ marginTop: 12 }}>
            <label style={{ display: 'block', marginBottom: 8, fontSize: 13, color: 'var(--text-secondary)' }}>Report Type</label>
            <select value={reportType} onChange={e => setReportType(e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid var(--border-color)', fontSize: 13, marginBottom: 12 }}>
              <option value="compliance_summary">Compliance Summary</option>
              <option value="project_overview">Project Overview</option>
            </select>
            <label style={{ display: 'block', marginBottom: 8, fontSize: 13, color: 'var(--text-secondary)' }}>Project ID (optional)</label>
            <input type="text" value={projectId} onChange={e => setProjectId(e.target.value)}
                   placeholder="Leave empty for all projects"
                   style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid var(--border-color)', fontSize: 13, marginBottom: 12 }} />
            <button className="btn btn-primary" onClick={generatePdf} disabled={generating}
                    style={{ width: '100%' }}>
              {generating ? 'Generating...' : 'Download PDF Report'}
            </button>
          </div>
        </div>

        {/* CSV Export */}
        <div className="card">
          <h3>CSV Data Export</h3>
          <div style={{ marginTop: 12 }}>
            <label style={{ display: 'block', marginBottom: 8, fontSize: 13, color: 'var(--text-secondary)' }}>Dataset</label>
            <select value={csvDataset} onChange={e => setCsvDataset(e.target.value)}
                    style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid var(--border-color)', fontSize: 13, marginBottom: 12 }}>
              <option value="nc_trends">NC Trends</option>
              <option value="project_health">Project Health</option>
              <option value="capa_metrics">CAPA Metrics</option>
              <option value="ai_usage">AI Usage</option>
            </select>
            {csvDataset === 'nc_trends' && (
              <>
                <label style={{ display: 'block', marginBottom: 8, fontSize: 13, color: 'var(--text-secondary)' }}>Months</label>
                <input type="number" value={months} onChange={e => setMonths(Number(e.target.value))} min={1} max={24}
                       style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid var(--border-color)', fontSize: 13, marginBottom: 12 }} />
              </>
            )}
            <button className="btn btn-primary" onClick={downloadCsv} disabled={generating}
                    style={{ width: '100%' }}>
              {generating ? 'Downloading...' : 'Download CSV'}
            </button>
          </div>
        </div>
      </div>

      {/* Quick export buttons for Dashboard integration */}
      <div className="card" style={{ marginTop: 16 }}>
        <h3>Quick Links</h3>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginTop: 8 }}>
          <a href="#dashboard" onClick={e => { e.preventDefault(); window.dispatchEvent(new CustomEvent('navigate', { detail: 'dashboard' })) }}
             className="btn btn-secondary">Dashboard</a>
          <a href="#analytics" onClick={e => { e.preventDefault(); window.dispatchEvent(new CustomEvent('navigate', { detail: 'analytics' })) }}
             className="btn btn-secondary">Analytics</a>
          <a href="#compliance" onClick={e => { e.preventDefault(); window.dispatchEvent(new CustomEvent('navigate', { detail: 'compliance' })) }}
             className="btn btn-secondary">Compliance</a>
        </div>
      </div>
    </div>
  )
}
