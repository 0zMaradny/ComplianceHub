import { useState, useEffect } from 'react'

const FRAMEWORK_NAMES = {
  'iso_37301': 'ISO 37301:2021 — Compliance Management',
  'iso_31000': 'ISO 31000:2018 — Risk Management',
}

export default function Compliance({ API }) {
  const [frameworks, setFrameworks] = useState(null)
  const [selected, setSelected] = useState(null)
  const [checklist, setChecklist] = useState(null)

  useEffect(() => {
    fetch(`${API}/compliance/frameworks`)
      .then(r => r.json())
      .then(data => setFrameworks(data.frameworks))
      .catch(() => {})
  }, [API])

  const loadChecklist = async (id) => {
    setSelected(id)
    try {
      const res = await fetch(`${API}/compliance/checklist/${id}`)
      const data = await res.json()
      setChecklist(data)
    } catch {}
  }

  if (!frameworks) {
    return <div className="empty-state"><h3>Loading frameworks...</h3></div>
  }

  return (
    <div>
      <div className="page-header">
        <h2>Compliance Frameworks</h2>
        <p>Track compliance across management system standards</p>
      </div>

      <div className="stats-grid">
        {Object.entries(frameworks).map(([id, fw]) => (
          <div
            key={id}
            className="stat-card"
            style={{ cursor: 'pointer', border: selected === id ? '2px solid var(--primary)' : '' }}
            onClick={() => loadChecklist(id)}
          >
            <h3>{FRAMEWORK_NAMES[id] || id}</h3>
            <div className="stat-number" style={{ fontSize: 24 }}>{fw.pillars.length} pillars</div>
          </div>
        ))}
      </div>

      {checklist && (
        <div className="card">
          <h3>{checklist.framework.name} — Checklist</h3>
          {checklist.checklist_items.map(pillar => (
            <div key={pillar.pillar} style={{ marginBottom: 24 }}>
              <div style={{
                fontSize: 14,
                fontWeight: 700,
                color: 'var(--primary)',
                marginBottom: 8,
                padding: '8px 12px',
                background: 'var(--primary-light)',
                borderRadius: 8,
              }}>
                {pillar.pillar_label}
              </div>
              {pillar.items.map((item, i) => (
                <div key={i} className="checkbox-item" style={{ marginBottom: 4 }}>
                  <input type="checkbox" />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}

      {!checklist && (
        <div className="empty-state">
          <h3>Select a framework</h3>
          <p>Click on a framework above to view its compliance checklist</p>
        </div>
      )}
    </div>
  )
}
