import { useState, useEffect, useCallback } from 'react'

const TUV_BLUE = '#003D7A'
const TUV_RED = '#C00000'

function healthColor(score) {
  if (score >= 85) return '#27AE60'
  if (score >= 60) return '#2ECC71'
  if (score >= 40) return '#F39C12'
  return '#E74C3C'
}

function healthLabel(score) {
  if (score >= 85) return 'Excellent'
  if (score >= 60) return 'Good'
  if (score >= 40) return 'At Risk'
  return 'Critical'
}

function BarChart({ data, colors, labels, height = 160 }) {
  const { months, ...series } = data
  if (!months || months.length === 0) return <div className="empty-state">No trend data</div>
  const allValues = Object.values(series).flat()
  const maxVal = Math.max(...allValues, 1)

  return (
    <div style={{ marginTop: 16 }}>
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 6, height, padding: '0 8px' }}>
        {months.map((m, i) => {
          const stacked = Object.entries(series).map(([key, vals]) => ({ key, val: vals[i] || 0 }))
          return (
            <div key={m} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3 }}>
              <div style={{ display: 'flex', flexDirection: 'column-reverse', width: '100%', alignItems: 'center' }}>
                {stacked.map(d => {
                  const h = d.val > 0 ? Math.max((d.val / maxVal) * (height - 24), 4) : 0
                  return h > 0 ? (
                    <div key={d.key} style={{
                      width: '70%', height: h,
                      background: colors[d.key] || '#999',
                      borderRadius: '3px 3px 0 0', minHeight: 2,
                    }} title={`${labels[d.key] || d.key}: ${d.val}`} />
                  ) : null
                })}
              </div>
              <span style={{ fontSize: 10, color: 'var(--text-secondary)' }}>{m.slice(5)}</span>
            </div>
          )
        })}
      </div>
      <div style={{ display: 'flex', gap: 16, justifyContent: 'center', marginTop: 12, flexWrap: 'wrap' }}>
        {Object.entries(colors).map(([key, color]) => (
          <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 12 }}>
            <div style={{ width: 12, height: 12, background: color, borderRadius: 2 }} />
            <span>{labels[key] || key}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function exportCSV(filename, headers, rows) {
  const csv = [headers.join(','), ...rows.map(r => r.map(v => `"${String(v).replace(/"/g, '""')}"`).join(','))].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = filename; a.click()
  URL.revokeObjectURL(url)
}

export default function Analytics({ API }) {
  const [period, setPeriod] = useState('30d')
  const [ncTrends, setNcTrends] = useState(null)
  const [projectHealth, setProjectHealth] = useState(null)
  const [aiUsage, setAiUsage] = useState(null)
  const [capaMetrics, setCapaMetrics] = useState(null)
  const [aiModels, setAiModels] = useState(null)
  const [loading, setLoading] = useState(true)
  const [sortField, setSortField] = useState('health_score')
  const [sortDir, setSortDir] = useState('asc')

  const months = period === '7d' ? 1 : period === '30d' ? 3 : period === '90d' ? 6 : 12

  const loadData = useCallback(() => {
    setLoading(true)
    Promise.all([
      fetch(`${API}/analytics/nc-trends?months=${months}`).then(r => r.json()).catch(() => null),
      fetch(`${API}/analytics/project-health`).then(r => r.json()).catch(() => null),
      fetch(`${API}/analytics/ai-usage`).then(r => r.json()).catch(() => null),
      fetch(`${API}/analytics/capa-metrics`).then(r => r.json()).catch(() => null),
      fetch(`${API}/ai/models/status`).then(r => r.json()).catch(() => null),
    ]).then(([trends, health, ai, capa, models]) => {
      setNcTrends(trends)
      setProjectHealth(health)
      setAiUsage(ai)
      setCapaMetrics(capa)
      setAiModels(models)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [API, months])

  useEffect(() => { loadData() }, [loadData])

  const handleSort = (field) => {
    if (sortField === field) setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    else { setSortField(field); setSortDir('asc') }
  }

  const sortedProjects = projectHealth?.projects?.slice().sort((a, b) => {
    const av = a[sortField] ?? 0, bv = b[sortField] ?? 0
    return sortDir === 'asc' ? (av > bv ? 1 : -1) : (av < bv ? 1 : -1)
  }) || []

  const exportProjectCSV = () => {
    if (!sortedProjects.length) return
    const headers = ['Title', 'Client', 'Health Score', 'Health Label', 'Open NCs', 'Pending CAPAs', 'Current Gate', 'Days in Gate']
    const rows = sortedProjects.map(p => [p.title, p.client, p.healthScore, healthLabel(p.healthScore), p.open_ncs, p.pending_capas, p.current_gate, p.days_in_gate])
    exportCSV('project_health.csv', headers, rows)
  }

  const exportNCCSV = () => {
    if (!ncTrends) return
    const headers = ['Month', 'Major NC', 'Minor NC', 'OFI', 'Closed', 'Recurring Rate %']
    const rows = ncTrends.months.map((m, i) => [m, ncTrends.major_nc[i], ncTrends.minor_nc[i], ncTrends.ofi[i], ncTrends.closed[i], ncTrends.recurring_rate_pct[i]])
    exportCSV('nc_trends.csv', headers, rows)
  }

  if (loading) return <div className="loading">Loading analytics...</div>

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h2>📊 Analytics</h2>
          <p>Detailed insights into audit operations, quality metrics, and AI performance</p>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <select value={period} onChange={e => setPeriod(e.target.value)}
            style={{ padding: '6px 12px', borderRadius: 6, border: '1px solid var(--border-color)', fontSize: 13 }}>
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last 12 months</option>
          </select>
          <button className="btn btn-secondary" onClick={loadData}>↻ Refresh</button>
        </div>
      </div>

      {/* ── NC Trends ── */}
      <div className="card" style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3>Nonconformity Trends</h3>
          {ncTrends && <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: 11 }} onClick={exportNCCSV}>Export CSV</button>}
        </div>
        {ncTrends ? (
          <BarChart
            data={ncTrends}
            colors={{ major_nc: TUV_RED, minor_nc: '#F39C12', ofi: '#3498DB', closed: '#27AE60' }}
            labels={{ major_nc: 'Major NC', minor_nc: 'Minor NC', ofi: 'OFI', closed: 'Closed' }}
            height={180}
          />
        ) : <div className="empty-state">No NC data available</div>}
        {ncTrends && (
          <div style={{ marginTop: 12, overflowX: 'auto' }}>
            <table style={{ width: '100%', fontSize: 12, borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--border-color)' }}>
                  <th style={{ textAlign: 'left', padding: '6px 8px' }}>Month</th>
                  <th style={{ textAlign: 'center', padding: '6px 8px', color: TUV_RED }}>Major</th>
                  <th style={{ textAlign: 'center', padding: '6px 8px', color: '#F39C12' }}>Minor</th>
                  <th style={{ textAlign: 'center', padding: '6px 8px', color: '#3498DB' }}>OFI</th>
                  <th style={{ textAlign: 'center', padding: '6px 8px', color: '#27AE60' }}>Closed</th>
                  <th style={{ textAlign: 'center', padding: '6px 8px' }}>Recurring %</th>
                </tr>
              </thead>
              <tbody>
                {ncTrends.months.map((m, i) => (
                  <tr key={m} style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '6px 8px', fontWeight: 600 }}>{m}</td>
                    <td style={{ textAlign: 'center', padding: '6px 8px' }}>{ncTrends.major_nc[i]}</td>
                    <td style={{ textAlign: 'center', padding: '6px 8px' }}>{ncTrends.minor_nc[i]}</td>
                    <td style={{ textAlign: 'center', padding: '6px 8px' }}>{ncTrends.ofi[i]}</td>
                    <td style={{ textAlign: 'center', padding: '6px 8px' }}>{ncTrends.closed[i]}</td>
                    <td style={{ textAlign: 'center', padding: '6px 8px' }}>{ncTrends.recurring_rate_pct[i]}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ── Project Health Table ── */}
      <div className="card" style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3>Project Health</h3>
          {sortedProjects.length > 0 && (
            <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: 11 }} onClick={exportProjectCSV}>Export CSV</button>
          )}
        </div>
        {sortedProjects.length > 0 ? (
          <div style={{ marginTop: 8, overflowX: 'auto' }}>
            <table style={{ width: '100%', fontSize: 12, borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--border-color)' }}>
                  {[
                    { key: 'title', label: 'Project' },
                    { key: 'client', label: 'Client' },
                    { key: 'health_score', label: 'Health' },
                    { key: 'current_gate', label: 'Gate' },
                    { key: 'days_in_gate', label: 'Days' },
                    { key: 'open_ncs', label: 'NCs' },
                    { key: 'pending_capas', label: 'CAPAs' },
                  ].map(col => (
                    <th key={col.key} style={{ textAlign: 'left', padding: '6px 8px', cursor: 'pointer', userSelect: 'none' }}
                      onClick={() => handleSort(col.key)}>
                      {col.label} {sortField === col.key ? (sortDir === 'asc' ? '↑' : '↓') : ''}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {sortedProjects.map(p => (
                  <tr key={p.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '8px', fontWeight: 600 }}>{p.title}</td>
                    <td style={{ padding: '8px' }}>{p.client}</td>
                    <td style={{ padding: '8px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <div style={{ width: 40, height: 5, background: 'var(--border-color)', borderRadius: 3, overflow: 'hidden' }}>
                          <div style={{ width: `${p.healthScore}%`, height: '100%', background: healthColor(p.healthScore), borderRadius: 3 }} />
                        </div>
                        <span style={{ fontWeight: 600, color: healthColor(p.healthScore), fontSize: 11 }}>
                          {p.healthScore}
                        </span>
                      </div>
                    </td>
                    <td style={{ padding: '8px', textAlign: 'center' }}>G{p.current_gate}</td>
                    <td style={{ padding: '8px', textAlign: 'center' }}>{p.days_in_gate}</td>
                    <td style={{ padding: '8px', textAlign: 'center', color: p.open_ncs > 0 ? TUV_RED : undefined, fontWeight: 600 }}>{p.open_ncs}</td>
                    <td style={{ padding: '8px', textAlign: 'center', color: p.pending_capas > 0 ? '#F39C12' : undefined, fontWeight: 600 }}>{p.pending_capas}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <div className="empty-state">No active projects</div>}
      </div>

      {/* ── AI Models + CAPA Metrics ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
        <div className="card">
          <h3>AI Model Status</h3>
          {aiModels?.models ? (
            <div style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 6 }}>
              {aiModels.models.filter(m => m.total_uses > 0 || m.healthy).slice(0, 8).map(m => (
                <div key={m.name} style={{
                  display: 'flex', alignItems: 'center', gap: 8,
                  padding: '6px 8px', borderRadius: 6,
                  background: m.healthy ? 'transparent' : '#FEF2F2',
                  border: '1px solid ' + (m.healthy ? 'var(--border-color)' : '#FECACA'),
                }}>
                  <div style={{
                    width: 6, height: 6, borderRadius: '50%',
                    background: m.healthy ? '#27AE60' : TUV_RED,
                  }} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 12, fontWeight: 600 }}>{m.name}</div>
                    <div style={{ fontSize: 10, color: 'var(--text-secondary)' }}>
                      {m.tier_category} · {m.total_uses} uses
                      {m.avg_quality_score > 0 && ` · q=${m.avg_quality_score}`}
                      {m.avg_response_time_ms > 0 && ` · ${m.avg_response_time_ms}ms`}
                    </div>
                  </div>
                  {m.failure_rate_pct > 0 && (
                    <span style={{ fontSize: 10, color: m.failure_rate_pct > 20 ? TUV_RED : '#F39C12' }}>
                      {m.failure_rate_pct}% fail
                    </span>
                  )}
                </div>
              ))}
              {aiModels.recommended_for && Object.keys(aiModels.recommended_for).length > 0 && (
                <div style={{ marginTop: 8, padding: '8px', background: 'var(--bg-secondary, #f8f9fa)', borderRadius: 6 }}>
                  <div style={{ fontSize: 11, fontWeight: 600, marginBottom: 4, color: TUV_BLUE }}>Recommendations</div>
                  {Object.entries(aiModels.recommended_for).slice(0, 5).map(([task, model]) => (
                    <div key={task} style={{ fontSize: 10, color: 'var(--text-secondary)', padding: '2px 0' }}>
                      {task}: <strong>{model}</strong>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : <div className="empty-state">No AI usage data yet</div>}
        </div>

        <div className="card">
          <h3>CAPA Metrics</h3>
          {capaMetrics ? (
            <div style={{ marginTop: 8 }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                <div className="stat-card"><div className="stat-number">{capaMetrics.total_capas ?? 0}</div><h3>Total</h3></div>
                <div className="stat-card"><div className="stat-number green">{capaMetrics.closure_rate_pct ?? 0}%</div><h3>Closure Rate</h3></div>
                <div className="stat-card"><div className="stat-number">{capaMetrics.avg_closure_days ?? '—'}</div><h3>Avg Days</h3></div>
                <div className="stat-card"><div className="stat-number" style={{ color: (capaMetrics.overdue_count ?? 0) > 0 ? TUV_RED : undefined }}>{capaMetrics.overdue_count ?? 0}</div><h3>Overdue</h3></div>
              </div>
              {capaMetrics.by_status && Object.keys(capaMetrics.by_status).length > 0 && (
                <div style={{ marginTop: 12 }}>
                  <h4 style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 6 }}>By Status</h4>
                  {Object.entries(capaMetrics.by_status).map(([status, count]) => (
                    <div key={status} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid var(--border-color)', fontSize: 12 }}>
                      <span>{status}</span>
                      <span style={{ fontWeight: 700 }}>{count}</span>
                    </div>
                  ))}
                </div>
              )}
              {capaMetrics.avg_days_by_severity && Object.keys(capaMetrics.avg_days_by_severity).length > 0 && (
                <div style={{ marginTop: 12 }}>
                  <h4 style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 6 }}>Avg Days by Severity</h4>
                  {Object.entries(capaMetrics.avg_days_by_severity).map(([sev, days]) => (
                    <div key={sev} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid var(--border-color)', fontSize: 12 }}>
                      <span>{sev}</span>
                      <span style={{ fontWeight: 700 }}>{Number(days).toFixed(1)}d</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : <div className="empty-state">No CAPA data yet</div>}
        </div>
      </div>
    </div>
  )
}
