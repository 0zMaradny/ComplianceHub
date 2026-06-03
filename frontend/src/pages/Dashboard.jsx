import { useState, useEffect } from 'react'

export default function Dashboard({ API }) {
  const [frameworks, setFrameworks] = useState(null)

  useEffect(() => {
    fetch(`${API}/compliance/frameworks`)
      .then(r => r.json())
      .then(data => setFrameworks(data.frameworks))
      .catch(() => {})
  }, [API])

  const frameworkCount = frameworks ? Object.keys(frameworks).length : 0
  const pillarCount = frameworks
    ? Object.values(frameworks).reduce((sum, f) => sum + f.pillars.length, 0)
    : 0

  return (
    <div>
      <div className="page-header">
        <h2>Dashboard</h2>
        <p>Overview of your compliance and audit management system</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Frameworks</h3>
          <div className="stat-number">{frameworkCount}</div>
        </div>
        <div className="stat-card">
          <h3>Compliance Pillars</h3>
          <div className="stat-number">{pillarCount}</div>
        </div>
        <div className="stat-card">
          <h3>Audit Documents</h3>
          <div className="stat-number">6</div>
        </div>
        <div className="stat-card">
          <h3>ISO Standards</h3>
          <div className="stat-number">11</div>
        </div>
      </div>

      <div className="card">
        <h3>Quick Actions</h3>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <a href="#audit" onClick={e => { e.preventDefault(); window.dispatchEvent(new CustomEvent('navigate', { detail: 'audit' })) }}
             className="btn btn-primary">
            Generate Audit Documents
          </a>
          <a href="#compliance" onClick={e => { e.preventDefault(); window.dispatchEvent(new CustomEvent('navigate', { detail: 'compliance' })) }}
             className="btn btn-secondary">
            View Compliance Frameworks
          </a>
        </div>
      </div>

      <div className="card">
        <h3>Supported ISO Standards</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: 8 }}>
          {['ISO 9001:2015 — Quality Management',
            'ISO 14001:2015 — Environmental Management',
            'ISO 45001:2018 — Occupational Health & Safety',
            'ISO 27001:2022 — Information Security',
            'ISO 22301:2019 — Business Continuity',
            'ISO 37301:2021 — Compliance Management',
            'ISO 31000:2018 — Risk Management',
            'ISO 50001:2018 — Energy Management',
            'ISO 20000:2018 — Service Management',
            'ISO 42001:2023 — AI Management',
            'ISO 30401:2018 — Knowledge Management',
          ].map(s => (
            <div key={s} className="checkbox-item" style={{ cursor: 'default' }}>
              <span>📋</span> {s}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
