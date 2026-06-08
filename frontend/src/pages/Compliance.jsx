import { useState, useEffect } from 'react'

const STATUS_ORDER = ['compliant', 'partial', 'non_compliant', 'na']
const STATUS_LABELS = { compliant: 'Compliant', partial: 'Partial', non_compliant: 'Non-Compliant', na: 'N/A' }
const STATUS_COLORS = {
  compliant: { bg: 'var(--green-50)', color: 'var(--green-600)' },
  partial: { bg: 'var(--amber-50)', color: 'var(--amber-600)' },
  non_compliant: { bg: 'var(--red-50)', color: 'var(--red-600)' },
  na: { bg: 'var(--gray-100)', color: 'var(--gray-500)' },
}

function loadAssessments() {
  try {
    return JSON.parse(localStorage.getItem('compliance_assessments') || '{}')
  } catch { return {} }
}

function saveAssessments(assessments) {
  localStorage.setItem('compliance_assessments', JSON.stringify(assessments))
}

export default function Compliance({ API }) {
  const [selected, setSelected] = useState(null)
  const [allStandards, setAllStandards] = useState([])
  const [clauses, setClauses] = useState([])
  const [annex, setAnnex] = useState({})
  const [loading, setLoading] = useState(false)
  const [assessments, setAssessments] = useState(loadAssessments)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    fetch(`${API}/standards`)
      .then(r => r.json())
      .then(data => {
        if (data?.standards) {
          const list = Object.entries(data.standards).map(([id, label]) => {
            const parts = label.split(' — ')
            return { id, label: parts[0] || label, desc: parts[1] || '' }
          })
          setAllStandards(list)
        }
      })
      .catch(() => {})
  }, [API])

  const stdKey = selected || '__empty__'

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      if (!selected) { setClauses([]); setAnnex({}); return }
      setLoading(true)
      try {
        const r = await fetch(`${API}/compliance/standards/${selected}/clauses`)
        if (!r.ok) throw new Error('Failed')
        const data = await r.json()
        if (!cancelled) { setClauses(data.clauses || []); setAnnex(data.annex_a || {}) }
      } catch {
        if (!cancelled) { setClauses([]); setAnnex({}) }
      }
      if (!cancelled) setLoading(false)
    }
    load()
    return () => { cancelled = true }
  }, [selected, API])

  const getStatus = (clauseId) => assessments[stdKey]?.[clauseId] || 'untouched'
  const setStatus = (clauseId, status) => {
    setAssessments(prev => {
      const next = { ...prev }
      if (!next[stdKey]) next[stdKey] = {}
      if (status === 'untouched') delete next[stdKey][clauseId]
      else next[stdKey][clauseId] = status
      if (Object.keys(next[stdKey]).length === 0) delete next[stdKey]
      saveAssessments(next)
      return next
    })
  }

  const stdAssess = assessments[stdKey] || {}
  const assessed = Object.keys(stdAssess)
  const compliantCount = Object.values(stdAssess).filter(s => s === 'compliant').length
  const partialCount = Object.values(stdAssess).filter(s => s === 'partial').length
  const nonCompliantCount = Object.values(stdAssess).filter(s => s === 'non_compliant').length
  const totalClauses = clauses.length
  const scoredClauses = totalClauses > 0
    ? Math.round((compliantCount + partialCount * 0.5) / totalClauses * 100)
    : 0

  const visible = clauses.filter(c => {
    if (filter === 'all') return true
    if (filter === 'compliant') return getStatus(c.id) === 'compliant'
    if (filter === 'partial') return getStatus(c.id) === 'partial'
    if (filter === 'non_compliant') return getStatus(c.id) === 'non_compliant'
    if (filter === 'untouched') return getStatus(c.id) === 'untouched'
    return true
  })

  const annexKeys = typeof annex === 'object' && !Array.isArray(annex) ? Object.keys(annex) : []

  if (!selected) {
    return (
      <div>
        <div className="page-header">
          <h2>Compliance Assessment</h2>
          <p>Select a standard to begin clause-level compliance assessment</p>
        </div>
        <div className="card">
          <h3>ISO Standards</h3>
          <div className="checkbox-group">
            {allStandards.map(s => (
              <div key={s.id} className="checkbox-item" style={{ cursor: 'pointer', justifyContent: 'space-between' }}
                   onClick={() => setSelected(s.id)}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>{s.label}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{s.desc}</div>
                </div>
                <span style={{ fontSize: 20, color: 'var(--text-secondary)' }}>→</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  const currentStd = allStandards.find(s => s.id === selected)

  return (
    <div>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <button className="btn btn-secondary" onClick={() => setSelected(null)} style={{ fontSize: 12, marginBottom: 8 }}>
            ← Back to Standards
          </button>
          <h2>{currentStd?.label || selected}</h2>
          <p>{currentStd?.desc} — Clause-level compliance assessment</p>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Compliance Score</h3>
          <div className={`stat-number ${scoredClauses >= 80 ? 'green' : scoredClauses >= 50 ? 'amber' : 'red'}`}>
            {scoredClauses}%
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
            {compliantCount} compliant, {partialCount} partial, {nonCompliantCount} non-compliant
          </div>
        </div>
        <div className="stat-card">
          <h3>Clauses</h3>
          <div className="stat-number">{assessed.length}/{totalClauses}</div>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
            {totalClauses - assessed.length} remaining
          </div>
        </div>
        <div className="stat-card">
          <h3>Non-Compliant</h3>
          <div className="stat-number red">{nonCompliantCount}</div>
          {nonCompliantCount > 0 && (
            <div style={{ fontSize: 12, color: 'var(--red-600)', marginTop: 4 }}>
              Requires corrective action
            </div>
          )}
        </div>
        <div className="stat-card">
          <h3>Progress Bar</h3>
          <div className="progress-bar" style={{ marginTop: 8 }}>
            <div className="progress-fill" style={{
              width: `${scoredClauses}%`,
              background: scoredClauses >= 80 ? 'var(--green-600)' : scoredClauses >= 50 ? 'var(--amber-600)' : 'var(--red-600)',
            }} />
          </div>
        </div>
      </div>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h3 style={{ margin: 0 }}>Clause Checklist</h3>
          <div style={{ display: 'flex', gap: 8 }}>
            {['all', 'compliant', 'partial', 'non_compliant', 'untouched'].map(f => (
              <button key={f} onClick={() => setFilter(f)}
                className={`btn btn-small ${filter === f ? 'btn-primary' : 'btn-secondary'}`}
                style={{ fontSize: 11, padding: '4px 8px' }}>
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="loading">Loading clauses...</div>
        ) : visible.length === 0 ? (
          <div className="empty-state">No clauses match the selected filter.</div>
        ) : (
          <div>
            {visible.map(c => {
              const status = getStatus(c.id)
              return (
                <div key={c.id} className="clause-item" style={{
                  padding: 12, borderBottom: '1px solid var(--border-color)',
                  background: status !== 'untouched' ? STATUS_COLORS[status]?.bg : 'transparent',
                  borderRadius: status !== 'untouched' ? 8 : 0,
                  marginBottom: status !== 'untouched' ? 4 : 0,
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 600, fontSize: 14, color: 'var(--text-primary)' }}>
                        Clause {c.id}: {c.title}
                      </div>
                      {c.description && (
                        <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
                          {c.description.substring(0, 200)}
                        </div>
                      )}
                    </div>
                    <div style={{ display: 'flex', gap: 4, marginLeft: 12, flexWrap: 'wrap' }}>
                      {STATUS_ORDER.map(s => (
                        <button key={s} onClick={() => setStatus(c.id, status === s ? 'untouched' : s)}
                          className="btn btn-small"
                          style={{
                            fontSize: 10, padding: '3px 8px',
                            background: status === s ? STATUS_COLORS[s].bg : 'transparent',
                            color: status === s ? STATUS_COLORS[s].color : 'var(--text-secondary)',
                            border: `1px solid ${status === s ? STATUS_COLORS[s].color : 'var(--border-color)'}`,
                          }}>
                          {STATUS_LABELS[s]}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {annexKeys.length > 0 && (
        <div className="card">
          <h3>Annex A Controls</h3>
          <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 12 }}>
            {selected === 'iso_27001' ? `${annexKeys.length} control themes from Annex A (93 controls)` :
             selected === 'iso_42001' ? `${annexKeys.length} control objectives from Annex A` :
             `${annexKeys.length} annex sections`}
          </div>
          <div className="checkbox-group">
            {annexKeys.map(key => (
              <div key={key} className="checkbox-item" style={{ cursor: 'default' }}>
                {key}
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={{ textAlign: 'center', padding: 16, fontSize: 12, color: 'var(--text-secondary)' }}>
        Assessment data is saved locally in your browser.
      </div>
    </div>
  )
}
