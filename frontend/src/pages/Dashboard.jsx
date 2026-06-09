import { useState, useEffect } from 'react'

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

// ── Simple CSS Bar Chart ──
function BarChart({ data, colors, labels, height = 120 }) {
  const { months, ...series } = data
  if (!months || months.length === 0) return <div className="empty-state">No trend data</div>

  const allValues = Object.values(series).flat()
  const maxVal = Math.max(...allValues, 1)

  return (
    <div style={{ marginTop: 12 }}>
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 4, height, padding: '0 4px' }}>
        {months.map((m, i) => {
          const stacked = Object.entries(series).map(([key, vals]) => ({ key, val: vals[i] || 0 }))
          const total = stacked.reduce((s, d) => s + d.val, 0)
          return (
            <div key={m} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
              <div style={{ display: 'flex', flexDirection: 'column-reverse', width: '100%', alignItems: 'center' }}>
                {stacked.map(d => {
                  const h = d.val > 0 ? Math.max((d.val / maxVal) * (height - 20), 4) : 0
                  return h > 0 ? (
                    <div key={d.key} style={{
                      width: '80%', height: h,
                      background: colors[d.key] || '#999',
                      borderRadius: '2px 2px 0 0',
                      minHeight: 2,
                    }} title={`${d.key}: ${d.val}`} />
                  ) : null
                })}
              </div>
              <span style={{ fontSize: 9, color: 'var(--text-secondary)', writingMode: 'vertical-rl', textOrientation: 'mixed', maxHeight: 40 }}>
                {m.slice(5)}
              </span>
            </div>
          )
        })}
      </div>
      <div style={{ display: 'flex', gap: 12, justifyContent: 'center', marginTop: 8, flexWrap: 'wrap' }}>
        {Object.entries(colors).map(([key, color]) => (
          <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 11 }}>
            <div style={{ width: 10, height: 10, background: color, borderRadius: 2 }} />
            <span>{labels[key] || key}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

// ── CSS Pie Chart ──
function PieChart({ data, size = 100 }) {
  const entries = Object.entries(data).filter(([, v]) => v > 0)
  const total = entries.reduce((s, [, v]) => s + v, 0)
  if (total === 0) return <div className="empty-state">No data</div>

  const colors = ['#003D7A', '#C00000', '#27AE60', '#F39C12', '#8E44AD', '#3498DB', '#E67E22', '#1ABC9C']
  let cumAngle = 0

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginTop: 8 }}>
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
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {entries.map(([key, val], i) => (
          <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11 }}>
            <div style={{ width: 8, height: 8, background: colors[i % colors.length], borderRadius: 2 }} />
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

  if (loading) return <div className="loading">Loading dashboard...</div>

  return (
    <div>
      <div className="page-header">
        <h2>Dashboard</h2>
        <p>Overview of your compliance and audit management system</p>
      </div>

      {/* ── KPI Row ── */}
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Jobs</h3>
          <div className="stat-number">{stats?.total_jobs ?? 0}</div>
        </div>
        <div className="stat-card">
          <h3>Success Rate</h3>
          <div className={`stat-number ${(stats?.success_rate ?? 0) >= 80 ? 'green' : (stats?.success_rate ?? 0) >= 50 ? 'amber' : 'red'}`}>
            {stats?.success_rate ?? 0}%
          </div>
        </div>
        <div className="stat-card">
          <h3>Open NCs</h3>
          <div className="stat-number" style={{ color: (stats?.open_ncs ?? 0) > 0 ? TUV_RED : undefined }}>
            {stats?.open_ncs ?? 0}
          </div>
        </div>
        <div className="stat-card">
          <h3>Pending CAPAs</h3>
          <div className="stat-number" style={{ color: (stats?.pending_capas ?? 0) > 0 ? '#F39C12' : undefined }}>
            {stats?.pending_capas ?? 0}
          </div>
        </div>
        <div className="stat-card">
          <h3>Avg CAPA Closure</h3>
          <div className="stat-number">{capaMetrics?.avg_closure_days ?? '—'}d</div>
        </div>
      </div>

      {/* ── NC Trends + AI Usage ── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
        <div className="card">
          <h3>NC Trends (6 months)</h3>
          {ncTrends ? (
            <BarChart
              data={ncTrends}
              colors={{ major_nc: TUV_RED, minor_nc: '#F39C12', ofi: '#3498DB', closed: '#27AE60' }}
              labels={{ major_nc: 'Major NC', minor_nc: 'Minor NC', ofi: 'OFI', closed: 'Closed' }}
            />
          ) : <div className="empty-state">No NC data yet</div>}
        </div>
        <div className="card">
          <h3>AI Usage</h3>
          {aiUsage?.by_provider && Object.keys(aiUsage.by_provider).length > 0 ? (
            <PieChart data={aiUsage.by_provider} />
          ) : <div className="empty-state">No AI usage data yet</div>}
          {aiUsage?.total_generations != null && (
            <div style={{ marginTop: 8, fontSize: 12, color: 'var(--text-secondary)' }}>
              {aiUsage.total_generations} generations · {aiUsage.cache_hit_rate ?? 0}% cache hit
            </div>
          )}
        </div>
      </div>

      {/* ── Project Health ── */}
      <div className="card" style={{ marginBottom: 16 }}>
        <h3>Project Health</h3>
        {projectHealth?.projects && projectHealth.projects.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 8 }}>
            {projectHealth.projects.map(p => (
              <div key={p.id} style={{
                display: 'flex', alignItems: 'center', gap: 12,
                padding: '8px 12px', borderRadius: 8,
                background: 'var(--bg-secondary, #f8f9fa)',
              }}>
                <div style={{
                  width: 8, height: 8, borderRadius: '50%',
                  background: healthColor(p.healthScore),
                  flexShrink: 0,
                }} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 600, fontSize: 13, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {p.title}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
                    {p.client} · Gate {p.current_gate} · {p.days_in_gate}d in gate
                  </div>
                </div>
                <div style={{ width: 60, height: 6, background: 'var(--border-color)', borderRadius: 3, overflow: 'hidden' }}>
                  <div style={{
                    width: `${p.healthScore}%`, height: '100%',
                    background: healthColor(p.healthScore),
                    borderRadius: 3, transition: 'width 0.3s',
                  }} />
                </div>
                <span style={{ fontSize: 12, fontWeight: 600, color: healthColor(p.healthScore), minWidth: 60, textAlign: 'right' }}>
                  {p.healthScore} — {healthLabel(p.healthScore)}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">No active projects</div>
        )}
      </div>

      {/* ── CAPA Metrics ── */}
      {capaMetrics && (
        <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: 16 }}>
          <div className="stat-card">
            <h3>Total CAPAs</h3>
            <div className="stat-number">{capaMetrics.total_capas ?? 0}</div>
          </div>
          <div className="stat-card">
            <h3>Closure Rate</h3>
            <div className="stat-number green">{capaMetrics.closure_rate_pct ?? 0}%</div>
          </div>
          <div className="stat-card">
            <h3>Avg Days</h3>
            <div className="stat-number">{capaMetrics.avg_closure_days ?? '—'}</div>
          </div>
          <div className="stat-card">
            <h3>Overdue</h3>
            <div className="stat-number" style={{ color: (capaMetrics.overdue_count ?? 0) > 0 ? TUV_RED : undefined }}>
              {capaMetrics.overdue_count ?? 0}
            </div>
          </div>
        </div>
      )}

      {/* ── Recent Jobs ── */}
      <div className="card" style={{ marginBottom: 16 }}>
        <h3>Recent Jobs</h3>
        <div style={{ marginTop: 8 }}>
          {recentJobs.length > 0 ? recentJobs.map(j => (
            <div key={j.job_id} style={{
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              padding: '6px 0', borderBottom: '1px solid var(--border-color)', fontSize: 13,
            }}>
              <div style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {getStandardsLabel(j.standards)}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span className={`status-badge status-${j.status}`} style={{ fontSize: 11 }}>{j.status}</span>
                <span style={{ color: 'var(--text-secondary)', fontSize: 11 }}>{formatDate(j.created_at)}</span>
              </div>
            </div>
          )) : (
            <div style={{ color: 'var(--text-secondary)', fontSize: 13 }}>No jobs yet</div>
          )}
        </div>
        {recentJobs.length > 0 && (
          <a href="#history" onClick={e => { e.preventDefault(); window.dispatchEvent(new CustomEvent('navigate', { detail: 'history' })) }}
             style={{ display: 'block', marginTop: 8, fontSize: 12, color: 'var(--primary)' }}>
            View all jobs →
          </a>
        )}
      </div>

      {/* ── Quick Actions ── */}
      <div className="card" style={{ marginBottom: 16 }}>
        <h3>Quick Actions</h3>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <a href="#audit" onClick={e => { e.preventDefault(); window.dispatchEvent(new CustomEvent('navigate', { detail: 'audit' })) }}
             className="btn btn-primary">Generate Audit Documents</a>
          <a href="#history" onClick={e => { e.preventDefault(); window.dispatchEvent(new CustomEvent('navigate', { detail: 'history' })) }}
             className="btn btn-secondary">View Job History</a>
          <a href="#compliance" onClick={e => { e.preventDefault(); window.dispatchEvent(new CustomEvent('navigate', { detail: 'compliance' })) }}
             className="btn btn-secondary">Compliance Frameworks</a>
        </div>
      </div>

      {/* ── Standards ── */}
      <div className="card">
        <h3>Supported ISO Standards</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: 8 }}>
          {(standards || []).map(s => (
            <div key={s} className="checkbox-item" style={{ cursor: 'default' }}>{s}</div>
          ))}
        </div>
      </div>
    </div>
  )
}
