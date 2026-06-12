import { useState, useEffect } from 'react'
import Skeleton from '../components/Skeleton'

const TUV_BLUE = '#003D7A'
const TUV_RED = '#C00000'

function formatDate(ts) {
  if (!ts) return '—'
  const d = new Date(ts * 1000)
  const now = new Date()
  const diff = (now - d) / 1000
  if (diff < 60) return 'just now'
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
  return d.toLocaleDateString()
}

function getStandardsLabel(standards) {
  if (!standards) return '—'
  const arr = Array.isArray(standards) ? standards : [standards]
  return arr.map(s => s.replace('iso_', 'ISO ').replace('_', ':')).join(', ')
}

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

function BarChart({ data, colors, labels, height = 120 }) {
  const { months, ...series } = data
  if (!months || months.length === 0) return <div className="text-center p-12 text-[var(--text-secondary)]">No trend data</div>

  const allValues = Object.values(series).flat()
  const maxVal = Math.max(...allValues, 1)

  return (
    <div className="mt-3">
      <div className="flex items-end gap-1 px-1" style={{ height }}>
        {months.map((m, i) => {
          const stacked = Object.entries(series).map(([key, vals]) => ({ key, val: vals[i] || 0 }))
          const total = stacked.reduce((s, d) => s + d.val, 0)
          return (
            <div key={m} className="flex-1 flex flex-col items-center gap-0.5">
              <div className="flex flex-col-reverse w-full items-center">
                {stacked.map(d => {
                  const h = d.val > 0 ? Math.max((d.val / maxVal) * (height - 20), 4) : 0
                  return h > 0 ? (
                    <div key={d.key} style={{ width: '80%', height: h, background: colors[d.key] || '#999', borderRadius: '2px 2px 0 0', minHeight: 2 }}
                      title={`${d.key}: ${d.val}`} />
                  ) : null
                })}
              </div>
              <span className="text-[9px] writing-mode-vertical" style={{ color: 'var(--text-secondary)', textOrientation: 'mixed', maxHeight: 40 }}>
                {m.slice(5)}
              </span>
            </div>
          )
        })}
      </div>
      <div className="flex gap-3 justify-center mt-2 flex-wrap">
        {Object.entries(colors).map(([key, color]) => (
          <div key={key} className="flex items-center gap-1 text-[11px]">
            <div className="w-2.5 h-2.5 rounded-[2px]" style={{ background: color }} />
            <span>{labels[key] || key}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function PieChart({ data, size = 100 }) {
  const entries = Object.entries(data).filter(([, v]) => v > 0)
  const total = entries.reduce((s, [, v]) => s + v, 0)
  if (total === 0) return <div className="text-center p-12 text-[var(--text-secondary)]">No data</div>

  const colors = ['#003D7A', '#C00000', '#27AE60', '#F39C12', '#8E44AD', '#3498DB', '#E67E22', '#1ABC9C']
  let cumAngle = 0

  return (
    <div className="flex items-center gap-4 mt-2">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {entries.map(([key, val], i) => {
          const angle = (val / total) * 360
          const startAngle = cumAngle
          cumAngle += angle
          const startRad = (startAngle - 90) * Math.PI / 180
          const endRad = (cumAngle - 90) * Math.PI / 180
          const largeArc = angle > 180 ? 1 : 0
          const r = size / 2 - 4
          const cx = size / 2, cy = size / 2
          const x1 = cx + r * Math.cos(startRad), y1 = cy + r * Math.sin(startRad)
          const x2 = cx + r * Math.cos(endRad), y2 = cy + r * Math.sin(endRad)
          const d = `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2} Z`
          return <path key={key} d={d} fill={colors[i % colors.length]} opacity={0.85} />
        })}
        <circle cx={size/2} cy={size/2} r={size/4} fill="var(--bg-primary)" />
        <text x={size/2} y={size/2} textAnchor="middle" dominantBaseline="central" fontSize="14" fontWeight="700" fill="var(--text-primary)">{total}</text>
      </svg>
      <div className="flex flex-col gap-1">
        {entries.map(([key, val], i) => (
          <div key={key} className="flex items-center gap-1.5 text-[11px]">
            <div className="w-2 h-2 rounded-[2px]" style={{ background: colors[i % colors.length] }} />
            <span>{key}: {val} ({Math.round(val/total*100)}%)</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function Dashboard({ API }) {
  const [stats, setStats] = useState(null)
  const [recentJobs, setRecentJobs] = useState([])
  const [standards, setStandards] = useState(null)
  const [ncTrends, setNcTrends] = useState(null)
  const [projectHealth, setProjectHealth] = useState(null)
  const [aiUsage, setAiUsage] = useState(null)
  const [capaMetrics, setCapaMetrics] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetch(`${API}/stats`).then(r => r.json()).catch(() => ({})),
      fetch(`${API}/jobs?limit=5`).then(r => r.json()).catch(() => ({ jobs: [] })),
      fetch(`${API}/standards`).then(r => r.json()).catch(() => null),
      fetch(`${API}/analytics/nc-trends?months=6`).then(r => r.json()).catch(() => null),
      fetch(`${API}/analytics/project-health`).then(r => r.json()).catch(() => null),
      fetch(`${API}/analytics/ai-usage`).then(r => r.json()).catch(() => null),
      fetch(`${API}/analytics/capa-metrics`).then(r => r.json()).catch(() => null),
    ]).then(([s, j, st, trends, health, ai, capa]) => {
      setStats(s)
      setRecentJobs(j.jobs || [])
      setStandards(st?.standards ? Object.values(st.standards) : null)
      setNcTrends(trends)
      setProjectHealth(health)
      setAiUsage(ai)
      setCapaMetrics(capa)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [API])

  if (loading) return (
    <div className="animate-fadeIn">
      <div className="mb-8"><Skeleton variant="title" width="200px" /><Skeleton variant="text" width="320px" className="mt-2" /></div>
      <div className="grid gap-5 mb-8 grid-cols-[repeat(auto-fit,minmax(220px,1fr))]">
        {[1,2,3,4,5].map(i => <Skeleton key={i} variant="stat-card" />)}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        <Skeleton variant="card" height="240px" />
        <Skeleton variant="card" height="240px" />
      </div>
      <Skeleton variant="card" height="160px" />
      <Skeleton variant="card" height="120px" />
    </div>
  )

  return (
    <div className="animate-fadeIn">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-[var(--text-primary)] m-0">Dashboard</h2>
        <p className="mt-1 text-[var(--text-secondary)]">Overview of your compliance and audit management system</p>
      </div>

      <div className="grid gap-5 mb-8 grid-cols-[repeat(auto-fit,minmax(220px,1fr))]">
        <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]">
          <h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">Total Jobs</h3>
          <div className="text-3xl font-bold text-[var(--primary)]">{stats?.total_jobs ?? 0}</div>
        </div>
        <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]">
          <h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">Success Rate</h3>
          <div className={`text-3xl font-bold ${(stats?.success_rate ?? 0) >= 80 ? 'text-green-600' : (stats?.success_rate ?? 0) >= 50 ? 'text-amber-600' : 'text-red-600'}`}>
            {stats?.success_rate ?? 0}%
          </div>
        </div>
        <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]">
          <h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">Open NCs</h3>
          <div className="text-3xl font-bold" style={{ color: (stats?.open_ncs ?? 0) > 0 ? TUV_RED : undefined }}>
            {stats?.open_ncs ?? 0}
          </div>
        </div>
        <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]">
          <h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">Pending CAPAs</h3>
          <div className="text-3xl font-bold" style={{ color: (stats?.pending_capas ?? 0) > 0 ? '#F39C12' : undefined }}>
            {stats?.pending_capas ?? 0}
          </div>
        </div>
        <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]">
          <h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">Avg CAPA Closure</h3>
          <div className="text-3xl font-bold text-[var(--primary)]">{capaMetrics?.avg_closure_days ?? '—'}d</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        <div className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)]">
          <div className="flex justify-between items-center">
            <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">NC Trends (6 months)</h3>
            <a href={`${API}/export/csv?dataset=nc_trends&months=6`}
               className="bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200 dark:bg-gray-200 dark:text-gray-800 rounded-lg font-semibold inline-flex items-center justify-center transition-all duration-150 cursor-pointer whitespace-nowrap no-underline text-[11px] px-2 py-1"
               download="nc_trends.csv">CSV</a>
          </div>
          {ncTrends ? (
            <BarChart
              data={ncTrends}
              colors={{ major_nc: TUV_RED, minor_nc: '#F39C12', ofi: '#3498DB', closed: '#27AE60' }}
              labels={{ major_nc: 'Major NC', minor_nc: 'Minor NC', ofi: 'OFI', closed: 'Closed' }}
            />
          ) : <div className="text-center p-12 text-[var(--text-secondary)]">No NC data yet</div>}
        </div>
        <div className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)]">
          <div className="flex justify-between items-center">
            <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">AI Usage</h3>
            <a href={`${API}/export/csv?dataset=ai_usage`}
               className="bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200 dark:bg-gray-200 dark:text-gray-800 rounded-lg font-semibold inline-flex items-center justify-center transition-all duration-150 cursor-pointer whitespace-nowrap no-underline text-[11px] px-2 py-1"
               download="ai_usage.csv">CSV</a>
          </div>
          {aiUsage?.by_provider && Object.keys(aiUsage.by_provider).length > 0 ? (
            <PieChart data={aiUsage.by_provider} />
          ) : <div className="text-center p-12 text-[var(--text-secondary)]">No AI usage data yet</div>}
          {aiUsage?.total_generations != null && (
            <div className="mt-2 text-xs text-[var(--text-secondary)]">
              {aiUsage.total_generations} generations · {aiUsage.cache_hit_rate ?? 0}% cache hit
            </div>
          )}
        </div>
      </div>

      <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)] mb-4">
        <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">Project Health</h3>
        {projectHealth?.projects && projectHealth.projects.length > 0 ? (
          <div className="flex flex-col gap-2 mt-2">
            {projectHealth.projects.map(p => (
              <div key={p.id} className="flex items-center gap-3 px-3 py-2 rounded-lg bg-[var(--bg-secondary,#f8f9fa)]">
                <div className="w-2 h-2 rounded-full shrink-0" style={{ background: healthColor(p.healthScore) }} />
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-semibold truncate">{p.title}</div>
                  <div className="text-[11px] text-[var(--text-secondary)]">
                    {p.client} · Gate {p.current_gate} · {p.days_in_gate}d in gate
                  </div>
                </div>
                <div className="w-[60px] h-1.5 rounded overflow-hidden bg-[var(--border-color)]">
                  <div className="h-full rounded transition-[width] duration-300" style={{ width: `${p.healthScore}%`, background: healthColor(p.healthScore) }} />
                </div>
                <span className="text-xs font-semibold min-w-[60px] text-right" style={{ color: healthColor(p.healthScore) }}>
                  {p.healthScore} — {healthLabel(p.healthScore)}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center p-12 text-[var(--text-secondary)]">No active projects</div>
        )}
      </div>

      {capaMetrics && (
        <div className="grid gap-5 grid-cols-2 lg:grid-cols-4 mb-4">
          <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]">
            <h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">Total CAPAs</h3>
            <div className="text-3xl font-bold text-[var(--primary)]">{capaMetrics.total_capas ?? 0}</div>
          </div>
          <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]">
            <h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">Closure Rate</h3>
            <div className="text-3xl font-bold text-green-600">{capaMetrics.closure_rate_pct ?? 0}%</div>
          </div>
          <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]">
            <h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">Avg Days</h3>
            <div className="text-3xl font-bold text-[var(--primary)]">{capaMetrics.avg_closure_days ?? '—'}</div>
          </div>
          <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]">
            <h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">Overdue</h3>
            <div className="text-3xl font-bold" style={{ color: (capaMetrics.overdue_count ?? 0) > 0 ? TUV_RED : undefined }}>
              {capaMetrics.overdue_count ?? 0}
            </div>
          </div>
        </div>
      )}

      <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)] mb-4">
        <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">Recent Jobs</h3>
        <div className="mt-2">
          {recentJobs.length > 0 ? recentJobs.map(j => (
            <div key={j.job_id} className="flex justify-between items-center py-1.5 text-xs border-b border-[var(--border-color)]">
              <div className="flex-1 truncate">{getStandardsLabel(j.standards)}</div>
              <div className="flex items-center gap-2">
                <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold ${{uploaded:'bg-blue-50 text-[var(--primary)]',generating:'bg-amber-50 text-amber-600',done:'bg-green-50 text-green-600',error:'bg-red-50 text-red-600'}[j.status] || ''}`} style={{ fontSize: 11 }}>{j.status}</span>
                <span className="text-[11px] text-[var(--text-secondary)]">{formatDate(j.created_at)}</span>
              </div>
            </div>
          )) : (
            <div className="text-xs text-[var(--text-secondary)]">No jobs yet</div>
          )}
        </div>
        {recentJobs.length > 0 && (
          <a href="#history" onClick={e => { e.preventDefault(); window.dispatchEvent(new CustomEvent('navigate', { detail: 'history' })) }}
             className="block mt-2 text-xs text-[var(--primary)]">
            View all jobs →
          </a>
        )}
      </div>

      <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)] mb-4">
        <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">Quick Actions</h3>
        <div className="flex gap-3 flex-wrap">
          <a href="#audit" onClick={e => { e.preventDefault(); window.dispatchEvent(new CustomEvent('navigate', { detail: 'audit' })) }}
             className="bg-[var(--primary)] text-white hover:bg-[var(--primary-dark)] px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center border-none transition-all duration-150 cursor-pointer no-underline">Generate Audit Documents</a>
          <a href="#history" onClick={e => { e.preventDefault(); window.dispatchEvent(new CustomEvent('navigate', { detail: 'history' })) }}
             className="bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200 dark:bg-gray-200 dark:text-gray-800 px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center transition-all duration-150 cursor-pointer whitespace-nowrap no-underline">View Job History</a>
          <a href="#compliance" onClick={e => { e.preventDefault(); window.dispatchEvent(new CustomEvent('navigate', { detail: 'compliance' })) }}
             className="bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200 dark:bg-gray-200 dark:text-gray-800 px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center transition-all duration-150 cursor-pointer whitespace-nowrap no-underline">Compliance Frameworks</a>
        </div>
      </div>

      <div className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)]">
        <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">Supported ISO Standards</h3>
        <div className="grid gap-2 grid-cols-[repeat(auto-fill,minmax(250px,1fr))]">
          {(standards || []).map(s => (
            <div key={s} className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs border border-[var(--border-color)] cursor-default">{s}</div>
          ))}
        </div>
      </div>
    </div>
  )
}
