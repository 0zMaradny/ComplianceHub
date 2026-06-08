import { useState, useEffect } from 'react'

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

export default function Dashboard({ API }) {
  const [stats, setStats] = useState(null)
  const [recentJobs, setRecentJobs] = useState([])
  const [standards, setStandards] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetch(`${API}/stats`).then(r => r.json()),
      fetch(`${API}/jobs?limit=5`).then(r => r.json()),
      fetch(`${API}/standards`).then(r => r.json()),
    ]).then(([s, j, st]) => {
      setStats(s)
      setRecentJobs(j.jobs || [])
      setStandards(st?.standards ? Object.values(st.standards) : null)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [API])

  return (
    <div>
      <div className="page-header">
        <h2>Dashboard</h2>
        <p>Overview of your compliance and audit management system</p>
      </div>

      {loading ? (
        <div className="loading">Loading...</div>
      ) : (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <h3>Total Jobs</h3>
              <div className="stat-number">{stats?.total_jobs ?? 0}</div>
            </div>
            <div className="stat-card">
              <h3>Completed</h3>
              <div className="stat-number green">{stats?.jobs_completed ?? 0}</div>
            </div>
            <div className="stat-card">
              <h3>Success Rate</h3>
              <div className={`stat-number ${(stats?.success_rate ?? 0) >= 80 ? 'green' : (stats?.success_rate ?? 0) >= 50 ? 'amber' : 'red'}`}>
                {stats?.success_rate ?? 0}%
              </div>
            </div>
            <div className="stat-card">
              <h3>Last 24h</h3>
              <div className="stat-number">{stats?.jobs_last_24h ?? 0}</div>
            </div>
          </div>

          <div className="card">
            <h3>Standards Used</h3>
            {stats?.standards_used && Object.keys(stats.standards_used).length > 0 ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 8 }}>
                {Object.entries(stats.standards_used)
                  .sort((a, b) => b[1] - a[1])
                  .map(([std, count]) => (
                    <div key={std} className="checkbox-item" style={{ cursor: 'default', justifyContent: 'space-between' }}>
                      <span>{std}</span>
                      <span className="stat-number" style={{ fontSize: 16 }}>{count}</span>
                    </div>
                  ))}
              </div>
            ) : (
              <div className="empty-state">No standards data yet</div>
            )}
          </div>

          <div className="stats-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
            <div className="stat-card">
              <h3>Certification Outcomes</h3>
              {stats?.certification_outcomes ? (
                <div style={{ marginTop: 12 }}>
                  {Object.entries(stats.certification_outcomes)
                    .filter(([, v]) => v > 0)
                    .map(([label, count]) => (
                      <div key={label} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--border-color)' }}>
                        <span style={{ fontSize: 13 }}>{label}</span>
                        <span style={{ fontWeight: 700, fontSize: 14 }}>{count}</span>
                      </div>
                    ))}
                </div>
              ) : (
                <div style={{ marginTop: 12, color: 'var(--text-secondary)', fontSize: 13 }}>No data yet</div>
              )}
            </div>
            <div className="stat-card">
              <h3>Recent Jobs</h3>
              <div style={{ marginTop: 12 }}>
                {recentJobs.length > 0 ? recentJobs.map(j => (
                  <div key={j.job_id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 0', borderBottom: '1px solid var(--border-color)', fontSize: 13 }}>
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
          </div>

          <div className="card">
            <h3>Quick Actions</h3>
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              <a href="#audit" onClick={e => { e.preventDefault(); window.dispatchEvent(new CustomEvent('navigate', { detail: 'audit' })) }}
                 className="btn btn-primary">
                Generate Audit Documents
              </a>
              <a href="#history" onClick={e => { e.preventDefault(); window.dispatchEvent(new CustomEvent('navigate', { detail: 'history' })) }}
                 className="btn btn-secondary">
                View Job History
              </a>
              <a href="#compliance" onClick={e => { e.preventDefault(); window.dispatchEvent(new CustomEvent('navigate', { detail: 'compliance' })) }}
                 className="btn btn-secondary">
                Compliance Frameworks
              </a>
            </div>
          </div>

          <div className="card">
            <h3>Supported ISO Standards</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: 8 }}>
              {(standards || []).map(s => (
                <div key={s} className="checkbox-item" style={{ cursor: 'default' }}>
                   {s}
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
