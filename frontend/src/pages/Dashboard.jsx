import { useState, useEffect } from 'react'

export default function Dashboard({ API }) {
  const [frameworks, setFrameworks] = useState(null)
  const [standards, setStandards] = useState(null)

  useEffect(() => {
    fetch(`${API}/compliance/frameworks`)
      .then(r => r.json())
      .then(data => setFrameworks(data.frameworks))
      .catch(() => {})
  }, [API])

  useEffect(() => {
    fetch(`${API}/standards`)
      .then(r => r.json())
      .then(data => setStandards(data))
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
          <div className="stat-number">{standards?.documents ? standards.documents.length : '—'}</div>
        </div>
        <div className="stat-card">
          <h3>ISO Standards</h3>
          <div className="stat-number">{standards?.standards ? Object.keys(standards.standards).length : '—'}</div>
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
          {standards?.standards ? Object.values(standards.standards).map(s => (
            <div key={s} className="checkbox-item" style={{ cursor: 'default' }}>
              <span>📋</span> {s}
            </div>
          )) : (
            <div style={{ color: 'var(--gray-500)' }}>Loading standards...</div>
          )}
        </div>
      </div>
    </div>
  )
}
