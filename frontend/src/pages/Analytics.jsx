import { useState, useEffect, useCallback } from 'react'
import Skeleton from '../components/Skeleton'
import { useTranslation } from 'react-i18next'

const TUV_BLUE = '#003D7A'
const TUV_RED = '#C00000'

function healthColor(score) {
  if (score >= 85) return '#27AE60'
  if (score >= 60) return '#2ECC71'
  if (score >= 40) return '#F39C12'
  return '#E74C3C'
}

function healthLabel(score, t) {
  if (score >= 85) return t('dashboard.excellent')
  if (score >= 60) return t('dashboard.good_label')
  if (score >= 40) return t('dashboard.at_risk')
  return t('dashboard.critical')
}

function BarChart({ data, colors, labels, height = 160 }) {
  const { t } = useTranslation()
  const { months, ...series } = data
  if (!months || months.length === 0) return <div className="text-center p-12 text-[var(--text-secondary)]">{t('dashboard.no_trend_data')}</div>
  const allValues = Object.values(series).flat()
  const maxVal = Math.max(...allValues, 1)

  return (
    <div className="mt-4">
      <div className="flex items-end gap-1.5 px-2" style={{ height }}>
        {months.map((m, i) => {
          const stacked = Object.entries(series).map(([key, vals]) => ({ key, val: vals[i] || 0 }))
          return (
            <div key={m} className="flex-1 flex flex-col items-center gap-0.5">
              <div className="flex flex-col-reverse w-full items-center">
                {stacked.map(d => {
                  const h = d.val > 0 ? Math.max((d.val / maxVal) * (height - 24), 4) : 0
                  return h > 0 ? (
                    <div key={d.key} style={{
                      width: '70%', height: h, background: colors[d.key] || '#999',
                      borderRadius: '3px 3px 0 0', minHeight: 2,
                    }} title={`${labels[d.key] || d.key}: ${d.val}`} />
                  ) : null
                })}
              </div>
              <span className="text-xs text-[var(--text-secondary)]">{m.slice(5)}</span>
            </div>
          )
        })}
      </div>
      <div className="flex gap-4 justify-center mt-3 flex-wrap">
        {Object.entries(colors).map(([key, color]) => (
          <div key={key} className="flex items-center gap-1 text-xs">
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
  const { t } = useTranslation()
  const [period, setPeriod] = useState('30d')
  const [ncTrends, setNcTrends] = useState(null)
  const [projectHealth, setProjectHealth] = useState(null)
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
    ]).then(([trends, health,, capa, models]) => {
      setNcTrends(trends); setProjectHealth(health); setCapaMetrics(capa); setAiModels(models)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [API, months])

  useEffect(() => { const id = setTimeout(() => loadData(), 0); return () => clearTimeout(id) }, [loadData])

  const handleSort = (field) => {
    if (sortField === field) setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    else { setSortField(field); setSortDir('asc') }
  }

  const sortedProjects = (projectHealth?.projects || []).slice().sort((a, b) => {
    const av = a[sortField] ?? 0, bv = b[sortField] ?? 0
    return sortDir === 'asc' ? (av > bv ? 1 : -1) : (av < bv ? 1 : -1)
  })

  const exportProjectCSV = () => {
    if (!sortedProjects.length) return
    const headers = [t('audit_program.program_title'), t('audit_program.client'), 'Health Score', 'Health Label', t('projects.open_ncs'), t('dashboard.pending_capas'), 'Current Gate', t('dashboard.d_in_gate')]
    const rows = sortedProjects.map(p => [p.title, p.client, p.healthScore, healthLabel(p.healthScore, t), p.open_ncs, p.pending_capas, p.current_gate, p.days_in_gate])
    exportCSV('project_health.csv', headers, rows)
  }

  const exportNCCSV = () => {
    if (!ncTrends) return
    const headers = [t('history.date'), t('dashboard.major_nc'), t('dashboard.minor_nc'), t('dashboard.ofi'), t('dashboard.closed'), 'Recurring Rate %']
    const rows = ncTrends.months.map((m, i) => [m, ncTrends.major_nc[i], ncTrends.minor_nc[i], ncTrends.ofi[i], ncTrends.closed[i], ncTrends.recurring_rate_pct[i]])
    exportCSV('nc_trends.csv', headers, rows)
  }

  if (loading) return (
    <div className="animate-fadeIn">
      <div className="mb-8"><Skeleton variant="title" width="200px" /><Skeleton variant="text" width="280px" className="mt-2" /></div>
      <div className="grid gap-5 mb-8 grid-cols-[repeat(auto-fit,minmax(220px,1fr))]">{[1,2,3,4].map(i => <Skeleton key={i} variant="stat-card" />)}</div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        <Skeleton variant="card" height="300px" /><Skeleton variant="card" height="300px" />
      </div>
      <Skeleton variant="card" height="200px" />
    </div>
  )

  return (
    <div className="animate-fadeIn">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2>{t('nav.analytics')}</h2>
          <p>{t('dashboard.title')}</p>
        </div>
        <div className="flex gap-2 items-center">
          <select value={period} onChange={e => setPeriod(e.target.value)} className="input" style={{ width: 'auto' }}>
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last 12 months</option>
          </select>
          <button className="btn btn-secondary" onClick={loadData}>↻ {t('error.refresh')}</button>
        </div>
      </div>

      <div className="card mb-5">
        <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>{t('reporting.nc_trends')}</span>
          {ncTrends && <button className="btn btn-ghost" style={{ fontSize: 11, padding: '4px 10px' }} onClick={exportNCCSV}>{t('reporting.csv_export')}</button>}
        </div>
        <div className="card-body">
          {ncTrends ? (
            <BarChart data={ncTrends}
              colors={{ major_nc: TUV_RED, minor_nc: '#F39C12', ofi: '#3498DB', closed: '#27AE60' }}
              labels={{ major_nc: t('dashboard.major_nc'), minor_nc: t('dashboard.minor_nc'), ofi: t('dashboard.ofi'), closed: t('dashboard.closed') }}
              height={180} />
          ) : <div className="text-center p-12 text-[var(--text-secondary)]">{t('dashboard.no_nc_data')}</div>}
          {ncTrends && (
            <div className="mt-3 overflow-x-auto">
              <table className="w-full text-xs border-collapse">
                <thead>
                  <tr className="border-b-2 border-[var(--border-color)]">
                    <th className="text-left px-2 py-1.5">{t('history.date')}</th>
                    <th className="text-center px-2 py-1.5" style={{ color: TUV_RED }}>{t('surveillance.severity_major')}</th>
                    <th className="text-center px-2 py-1.5" style={{ color: '#F39C12' }}>{t('surveillance.severity_minor')}</th>
                    <th className="text-center px-2 py-1.5" style={{ color: '#3498DB' }}>{t('dashboard.ofi')}</th>
                    <th className="text-center px-2 py-1.5" style={{ color: '#27AE60' }}>{t('dashboard.closed')}</th>
                    <th className="text-center px-2 py-1.5">Recurring %</th>
                  </tr>
                </thead>
                <tbody>
                  {ncTrends.months.map((m, i) => (
                    <tr key={m} className="border-b border-[var(--border-color)]">
                      <td className="px-2 py-1.5 font-semibold">{m}</td>
                      <td className="text-center px-2 py-1.5">{ncTrends.major_nc[i]}</td>
                      <td className="text-center px-2 py-1.5">{ncTrends.minor_nc[i]}</td>
                      <td className="text-center px-2 py-1.5">{ncTrends.ofi[i]}</td>
                      <td className="text-center px-2 py-1.5">{ncTrends.closed[i]}</td>
                      <td className="text-center px-2 py-1.5">{ncTrends.recurring_rate_pct[i]}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      <div className="card mb-5">
        <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>{t('dashboard.project_health')}</span>
          {sortedProjects.length > 0 && (
            <button className="btn btn-ghost" style={{ fontSize: 11, padding: '4px 10px' }} onClick={exportProjectCSV}>{t('reporting.csv_export')}</button>
          )}
        </div>
        <div className="card-body">
          {sortedProjects.length > 0 ? (
            <div className="mt-2 overflow-x-auto">
              <table className="w-full text-xs border-collapse">
                <thead>
                  <tr className="border-b-2 border-[var(--border-color)]">
                    {[
                      { key: 'title', label: t('audit_program.program_title') },
                      { key: 'client', label: t('audit_program.client') },
                      { key: 'health_score', label: t('dashboard.project_health') },
                      { key: 'current_gate', label: t('dashboard.gate') },
                      { key: 'days_in_gate', label: t('dashboard.d_in_gate') },
                      { key: 'open_ncs', label: t('projects.open_ncs') },
                      { key: 'pending_capas', label: t('dashboard.pending_capas') },
                    ].map(col => (
                      <th key={col.key} className="text-left px-2 py-1.5 cursor-pointer select-none"
                        onClick={() => handleSort(col.key)}>
                        {col.label} {sortField === col.key ? (sortDir === 'asc' ? '↑' : '↓') : ''}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {sortedProjects.map(p => (
                    <tr key={p.id} className="border-b border-[var(--border-color)]">
                      <td className="px-2 py-2 font-semibold">{p.title}</td>
                      <td className="px-2 py-2">{p.client}</td>
                      <td className="px-2 py-2">
                        <div className="flex items-center gap-1.5">
                          <div className="w-10 h-1 rounded overflow-hidden" style={{ background: 'var(--border-color)' }}>
                            <div style={{ width: `${p.healthScore}%`, height: '100%', background: healthColor(p.healthScore), borderRadius: 3 }} />
                          </div>
                          <span className="font-semibold text-xs" style={{ color: healthColor(p.healthScore) }}>{p.healthScore}</span>
                        </div>
                      </td>
                      <td className="px-2 py-2 text-center">G{p.current_gate}</td>
                      <td className="px-2 py-2 text-center">{p.days_in_gate}</td>
                      <td className="px-2 py-2 text-center font-semibold" style={{ color: p.open_ncs > 0 ? TUV_RED : undefined }}>{p.open_ncs}</td>
                      <td className="px-2 py-2 text-center font-semibold" style={{ color: p.pending_capas > 0 ? '#F39C12' : undefined }}>{p.pending_capas}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : <div className="text-center p-12 text-[var(--text-secondary)]">{t('dashboard.no_active_projects')}</div>}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        <div className="card">
          <div className="card-header">{t('dashboard.ai_usage')}</div>
          <div className="card-body">
            {aiModels?.models ? (
              <div className="mt-2 flex flex-col gap-1.5">
                {aiModels.models.filter(m => m.total_uses > 0 || m.healthy).slice(0, 8).map(m => (
                  <div key={m.name} className="flex items-center gap-2 px-2 py-1.5 rounded-md"
                    style={{
                      background: m.healthy ? 'transparent' : '#FEF2F2',
                      border: '1px solid ' + (m.healthy ? 'var(--border-color)' : '#FECACA'),
                    }}>
                    <div style={{
                      width: 6, height: 6, borderRadius: '50%',
                      background: m.healthy ? '#27AE60' : TUV_RED,
                    }} />
                    <div className="flex-1">
                      <div className="text-xs font-semibold">{m.name}</div>
                      <div className="text-xs text-[var(--text-secondary)]">
                        {m.tier_category} · {m.total_uses} {t('dashboard.generations')}
                        {m.avg_quality_score > 0 && ` · q=${m.avg_quality_score}`}
                        {m.avg_response_time_ms > 0 && ` · ${m.avg_response_time_ms}ms`}
                      </div>
                    </div>
                    {m.failure_rate_pct > 0 && (
                      <span className="text-xs" style={{ color: m.failure_rate_pct > 20 ? TUV_RED : '#F39C12' }}>
                        {m.failure_rate_pct}% {t('audit.failed_label')}
                      </span>
                    )}
                  </div>
                ))}
                {aiModels.recommended_for && Object.keys(aiModels.recommended_for).length > 0 && (
                  <div className="mt-2 p-2 rounded-md" style={{ background: 'var(--bg-secondary, #f8f9fa)' }}>
                    <div className="text-xs font-semibold mb-1" style={{ color: TUV_BLUE }}>{t('dashboard.project_health')}</div>
                    {Object.entries(aiModels.recommended_for).slice(0, 5).map(([task, model]) => (
                      <div key={task} className="text-xs py-0.5 text-[var(--text-secondary)]">
                        {task}: <strong>{model}</strong>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : <div className="text-center p-12 text-[var(--text-secondary)]">{t('dashboard.no_ai_data')}</div>}
          </div>
        </div>

        <div className="card">
          <div className="card-header">{t('reporting.capa_metrics')}</div>
          <div className="card-body">
            {capaMetrics ? (
              <div className="mt-2">
                <div className="grid grid-cols-2 gap-2">
                  <div className="stat-card"><div className="stat-card-value" style={{ color: 'var(--primary)' }}>{capaMetrics.total_capas ?? 0}</div><div className="stat-card-label">{t('dashboard.total_capas')}</div></div>
                  <div className="stat-card"><div className="stat-card-value" style={{ color: '#27AE60' }}>{capaMetrics.closure_rate_pct ?? 0}%</div><div className="stat-card-label">{t('dashboard.closure_rate')}</div></div>
                  <div className="stat-card"><div className="stat-card-value" style={{ color: 'var(--primary)' }}>{capaMetrics.avg_closure_days ?? '—'}</div><div className="stat-card-label">{t('dashboard.avg_days')}</div></div>
                  <div className="stat-card"><div className="stat-card-value" style={{ color: (capaMetrics.overdue_count ?? 0) > 0 ? TUV_RED : 'var(--primary)' }}>{capaMetrics.overdue_count ?? 0}</div><div className="stat-card-label">{t('dashboard.overdue')}</div></div>
                </div>
                {capaMetrics.by_status && Object.keys(capaMetrics.by_status).length > 0 && (
                  <div className="mt-3">
                    <h4 className="text-xs mb-1.5 text-[var(--text-secondary)]">{t('history.status')}</h4>
                    {Object.entries(capaMetrics.by_status).map(([status, count]) => (
                      <div key={status} className="flex justify-between py-1 text-xs border-b border-[var(--border-color)]">
                        <span>{status}</span>
                        <span className="font-bold">{count}</span>
                      </div>
                    ))}
                  </div>
                )}
                {capaMetrics.avg_days_by_severity && Object.keys(capaMetrics.avg_days_by_severity).length > 0 && (
                  <div className="mt-3">
                    <h4 className="text-xs mb-1.5 text-[var(--text-secondary)]">{t('dashboard.avg_days')} by {t('surveillance.severity')}</h4>
                    {Object.entries(capaMetrics.avg_days_by_severity).map(([sev, days]) => (
                      <div key={sev} className="flex justify-between py-1 text-xs border-b border-[var(--border-color)]">
                        <span>{sev}</span>
                        <span className="font-bold">{Number(days).toFixed(1)}d</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : <div className="text-center p-12 text-[var(--text-secondary)]">{t('dashboard.no_data')}</div>}
          </div>
        </div>
      </div>
    </div>
  )
}
