import { useState, useEffect } from 'react'

const TUV_BLUE = '#003D7A'
const TUV_RED = '#C00000'

const STATUS_COLORS = {
  scheduled: '#3498DB',
  in_progress: '#F39C12',
  completed: '#27AE60',
  overdue: TUV_RED,
}

const CYCLE_LABELS = {
  1: 'Year 1 Surveillance',
  2: 'Year 2 Surveillance',
  3: 'Year 3 Recertification',
}

const FINDING_TYPE_COLORS = {
  recurring_nc: TUV_RED,
  new_nc: '#E67E22',
  ofi: '#3498DB',
  observation: '#95A5A6',
}

export default function Surveillance({ API }) {
  const [cycles, setCycles] = useState([])
  const [projects, setProjects] = useState([])
  const [stats, setStats] = useState(null)
  const [selectedCycle, setSelectedCycle] = useState(null)
  const [findings, setFindings] = useState([])
  const [scope, setScope] = useState(null)
  const [showCreate, setShowCreate] = useState(false)
  const [showAddFinding, setShowAddFinding] = useState(false)
  const [form, setForm] = useState({ project_id: '', cycle_number: 1, scheduled_date: '', notes: '' })
  const [findingForm, setFindingForm] = useState({
    clause: '', finding_type: 'new_nc', severity: 'Minor', description: '', previous_nc_id: '',
  })
  const [autoScheduleProj, setAutoScheduleProj] = useState('')
  const [autoScheduleDate, setAutoScheduleDate] = useState('')

  const loadData = () => {
    Promise.all([
      fetch(`${API}/surveillance/cycles`).then(r => r.json()).catch(() => ({ cycles: [] })),
      fetch(`${API}/projects`).then(r => r.json()).catch(() => ({ projects: [] })),
      fetch(`${API}/surveillance/dashboard`).then(r => r.json()).catch(() => ({})),
    ]).then(([c, p, s]) => {
      setCycles(c.cycles || [])
      setProjects(p.projects || [])
      setStats(s)
    })
  }

  useEffect(() => { loadData() }, [API])

  const loadFindings = async (cycleId) => {
    const r = await fetch(`${API}/surveillance/cycles/${cycleId}/findings`)
    const d = await r.json().catch(() => ({ findings: [] }))
    setFindings(d.findings || [])
  }

  const loadScope = async (cycleId) => {
    const r = await fetch(`${API}/surveillance/cycles/${cycleId}/scope`, { method: 'POST' })
    const d = await r.json().catch(() => null)
    setScope(d)
  }

  const openCycle = async (cycle) => {
    setSelectedCycle(cycle)
    setScope(null)
    await loadFindings(cycle.id)
  }

  const handleCreate = async () => {
    if (!form.project_id || !form.scheduled_date) return
    const body = new URLSearchParams()
    body.append('project_id', form.project_id)
    body.append('cycle_number', form.cycle_number)
    body.append('scheduled_date', form.scheduled_date)
    if (form.notes) body.append('notes', form.notes)
    const r = await fetch(`${API}/surveillance/cycles`, {
      method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body,
    })
    if (r.ok) {
      setShowCreate(false)
      setForm({ project_id: '', cycle_number: 1, scheduled_date: '', notes: '' })
      loadData()
    }
  }

  const handleAddFinding = async () => {
    if (!findingForm.clause || !findingForm.description || !selectedCycle) return
    const body = new URLSearchParams()
    body.append('clause', findingForm.clause)
    body.append('finding_type', findingForm.finding_type)
    body.append('severity', findingForm.severity)
    body.append('description', findingForm.description)
    if (findingForm.previous_nc_id) body.append('previous_nc_id', findingForm.previous_nc_id)
    const r = await fetch(`${API}/surveillance/cycles/${selectedCycle.id}/findings`, {
      method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body,
    })
    if (r.ok) {
      setShowAddFinding(false)
      setFindingForm({ clause: '', finding_type: 'new_nc', severity: 'Minor', description: '', previous_nc_id: '' })
      loadFindings(selectedCycle.id)
    }
  }

  const handleAutoSchedule = async () => {
    if (!autoScheduleProj || !autoScheduleDate) return
    const body = new URLSearchParams()
    body.append('cert_date', autoScheduleDate)
    await fetch(`${API}/projects/${autoScheduleProj}/auto-schedule`, {
      method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body,
    })
    loadData()
  }

  const handleCheckOverdue = async () => {
    await fetch(`${API}/surveillance/check-overdue`, { method: 'POST' })
    loadData()
  }

  const handleUpdateStatus = async (cycleId, status) => {
    await fetch(`${API}/surveillance/cycles/${cycleId}`, {
      method: 'PUT', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    })
    loadData()
    if (selectedCycle?.id === cycleId) {
      setSelectedCycle({ ...selectedCycle, status })
    }
  }

  // ── Detail View ──
  if (selectedCycle) {
    const project = projects.find(p => p.id === selectedCycle.project_id)
    return (
      <div>
        <button className="btn btn-secondary" onClick={() => { setSelectedCycle(null); setScope(null) }} style={{ marginBottom: 16 }}>
          ← Back to Surveillance
        </button>

        <div className="card" style={{ marginBottom: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <h2 style={{ margin: '0 0 4px' }}>
                Cycle {selectedCycle.cycle_number}: {CYCLE_LABELS[selectedCycle.cycle_number] || 'Surveillance'}
              </h2>
              <div style={{ color: 'var(--text-secondary)', fontSize: 13 }}>
                {project?.title || selectedCycle.project_id} · Scheduled: {selectedCycle.scheduled_date}
              </div>
            </div>
            <span className="badge" style={{
              background: STATUS_COLORS[selectedCycle.status] + '20',
              color: STATUS_COLORS[selectedCycle.status],
              fontSize: 13, padding: '5px 12px',
            }}>
              {selectedCycle.status}
            </span>
          </div>
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
          <button className="btn btn-secondary" onClick={() => loadScope(selectedCycle.id)}>
            🔍 Generate Scope
          </button>
          <button className="btn btn-secondary" onClick={() => setShowAddFinding(!showAddFinding)}>
            + Add Finding
          </button>
          {selectedCycle.status === 'scheduled' && (
            <button className="btn btn-primary" onClick={() => handleUpdateStatus(selectedCycle.id, 'in_progress')}>
              ▶ Start Audit
            </button>
          )}
          {selectedCycle.status === 'in_progress' && (
            <button className="btn btn-primary" onClick={() => handleUpdateStatus(selectedCycle.id, 'completed')}>
              ✓ Complete
            </button>
          )}
        </div>

        {/* Scope */}
        {scope && (
          <div className="card" style={{ marginBottom: 16 }}>
            <h3>Reduced Scope</h3>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{scope.rationale}</p>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 8 }}>
              <div>
                <h4 style={{ fontSize: 12, color: '#27AE60' }}>Included Clauses ({scope.included_clauses?.length || 0})</h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 4 }}>
                  {(scope.included_clauses || []).map(c => (
                    <span key={c} style={{ fontSize: 10, padding: '2px 6px', background: '#E8F8F0', borderRadius: 4 }}>{c}</span>
                  ))}
                </div>
              </div>
              <div>
                <h4 style={{ fontSize: 12, color: TUV_RED }}>Excluded Clauses ({scope.excluded_clauses?.length || 0})</h4>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 4 }}>
                  {(scope.excluded_clauses || []).map(c => (
                    <span key={c} style={{ fontSize: 10, padding: '2px 6px', background: '#FEF2F2', borderRadius: 4 }}>{c}</span>
                  ))}
                </div>
              </div>
            </div>
            {scope.manday_reduction_pct > 0 && (
              <div style={{ marginTop: 8, fontSize: 12, color: 'var(--text-secondary)' }}>
                Manday reduction: {scope.manday_reduction_pct}%
              </div>
            )}
          </div>
        )}

        {/* Add Finding Form */}
        {showAddFinding && (
          <div className="card" style={{ marginBottom: 16 }}>
            <h3 style={{ marginBottom: 12 }}>Add Finding</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div className="form-group">
                <label>Clause *</label>
                <input type="text" value={findingForm.clause} placeholder="e.g. 4.1"
                  onChange={e => setFindingForm({ ...findingForm, clause: e.target.value })}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-color)' }} />
              </div>
              <div className="form-group">
                <label>Type</label>
                <select value={findingForm.finding_type} onChange={e => setFindingForm({ ...findingForm, finding_type: e.target.value })}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-color)' }}>
                  <option value="new_nc">New NC</option>
                  <option value="recurring_nc">Recurring NC</option>
                  <option value="ofi">OFI</option>
                  <option value="observation">Observation</option>
                </select>
              </div>
              <div className="form-group">
                <label>Severity</label>
                <select value={findingForm.severity} onChange={e => setFindingForm({ ...findingForm, severity: e.target.value })}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-color)' }}>
                  <option value="Major">Major</option>
                  <option value="Minor">Minor</option>
                  <option value="OFI">OFI</option>
                </select>
              </div>
              <div className="form-group">
                <label>Previous NC ID (if recurring)</label>
                <input type="text" value={findingForm.previous_nc_id} placeholder="NC-XXXXXXXX"
                  onChange={e => setFindingForm({ ...findingForm, previous_nc_id: e.target.value })}
                  style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-color)' }} />
              </div>
            </div>
            <div className="form-group" style={{ marginTop: 8 }}>
              <label>Description *</label>
              <textarea value={findingForm.description} rows={3} placeholder="Detailed finding description..."
                onChange={e => setFindingForm({ ...findingForm, description: e.target.value })}
                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-color)', resize: 'vertical' }} />
            </div>
            <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
              <button className="btn btn-primary" onClick={handleAddFinding}>Add Finding</button>
              <button className="btn btn-secondary" onClick={() => setShowAddFinding(false)}>Cancel</button>
            </div>
          </div>
        )}

        {/* Findings */}
        <div className="card">
          <h3>Findings ({findings.length})</h3>
          {findings.length === 0 ? (
            <div className="empty-state">No findings recorded yet</div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 8 }}>
              {findings.map(f => (
                <div key={f.id} style={{
                  padding: '10px 12px', borderRadius: 8,
                  border: '1px solid var(--border-color)',
                  borderLeft: `4px solid ${FINDING_TYPE_COLORS[f.finding_type] || '#999'}`,
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: 600, fontSize: 13 }}>{f.clause}</span>
                    <div style={{ display: 'flex', gap: 6 }}>
                      <span className="badge" style={{
                        background: FINDING_TYPE_COLORS[f.finding_type] + '20',
                        color: FINDING_TYPE_COLORS[f.finding_type],
                        fontSize: 10, padding: '2px 8px',
                      }}>{f.finding_type.replace('_', ' ')}</span>
                      <span className="badge" style={{
                        background: f.severity === 'Major' ? TUV_RED + '20' : '#F39C12' + '20',
                        color: f.severity === 'Major' ? TUV_RED : '#F39C12',
                        fontSize: 10, padding: '2px 8px',
                      }}>{f.severity}</span>
                    </div>
                  </div>
                  <p style={{ fontSize: 12, color: 'var(--text-secondary)', margin: '4px 0 0' }}>{f.description}</p>
                  {f.previous_nc_id && (
                    <div style={{ fontSize: 10, color: TUV_RED, marginTop: 4 }}>↳ Recurring from {f.previous_nc_id}</div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    )
  }

  // ── List View ──
  return (
    <div>
      <div className="page-header">
        <h2>🔄 Surveillance & Recertification</h2>
        <p>Manage post-certification surveillance audit cycles and recertification</p>
      </div>

      {/* Stats */}
      {stats && (
        <div className="stats-grid" style={{ marginBottom: 16 }}>
          <div className="stat-card">
            <div className="stat-number">{stats.total_cycles ?? 0}</div>
            <h3>Total Cycles</h3>
          </div>
          <div className="stat-card">
            <div className="stat-number" style={{ color: '#3498DB' }}>{stats.upcoming_30d ?? 0}</div>
            <h3>Upcoming (30d)</h3>
          </div>
          <div className="stat-card">
            <div className="stat-number" style={{ color: TUV_RED }}>{stats.overdue ?? 0}</div>
            <h3>Overdue</h3>
          </div>
          <div className="stat-card">
            <div className="stat-number" style={{ color: '#27AE60' }}>{stats.completed ?? 0}</div>
            <h3>Completed</h3>
          </div>
        </div>
      )}

      {/* Actions */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap', alignItems: 'center' }}>
        <button className="btn btn-primary" onClick={() => setShowCreate(!showCreate)}>
          {showCreate ? '✕ Cancel' : '+ New Cycle'}
        </button>
        <button className="btn btn-secondary" onClick={handleCheckOverdue}>
          ⚠ Check Overdue
        </button>
      </div>

      {/* Auto-Schedule */}
      <div className="card" style={{ marginBottom: 16 }}>
        <h3>Auto-Schedule Surveillance</h3>
        <p style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Create 3 cycles (Y1, Y2 surveillance + Y3 recert) from certification date</p>
        <div style={{ display: 'flex', gap: 8, marginTop: 8, flexWrap: 'wrap' }}>
          <select value={autoScheduleProj} onChange={e => setAutoScheduleProj(e.target.value)}
            style={{ padding: '6px 12px', borderRadius: 6, border: '1px solid var(--border-color)', minWidth: 180 }}>
            <option value="">-- Select Project --</option>
            {projects.map(p => <option key={p.id} value={p.id}>{p.title}</option>)}
          </select>
          <input type="date" value={autoScheduleDate} onChange={e => setAutoScheduleDate(e.target.value)}
            style={{ padding: '6px 12px', borderRadius: 6, border: '1px solid var(--border-color)' }} />
          <button className="btn btn-primary" onClick={handleAutoSchedule}
            disabled={!autoScheduleProj || !autoScheduleDate}>
            Auto-Schedule
          </button>
        </div>
      </div>

      {/* Create Form */}
      {showCreate && (
        <div className="card" style={{ marginBottom: 16 }}>
          <h3 style={{ marginBottom: 12 }}>Create Surveillance Cycle</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div className="form-group">
              <label>Project *</label>
              <select value={form.project_id} onChange={e => setForm({ ...form, project_id: e.target.value })}
                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-color)' }}>
                <option value="">-- Select --</option>
                {projects.map(p => <option key={p.id} value={p.id}>{p.title}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Cycle *</label>
              <select value={form.cycle_number} onChange={e => setForm({ ...form, cycle_number: parseInt(e.target.value) })}
                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-color)' }}>
                <option value={1}>Year 1 — Surveillance</option>
                <option value={2}>Year 2 — Surveillance</option>
                <option value={3}>Year 3 — Recertification</option>
              </select>
            </div>
            <div className="form-group">
              <label>Scheduled Date *</label>
              <input type="date" value={form.scheduled_date}
                onChange={e => setForm({ ...form, scheduled_date: e.target.value })}
                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-color)' }} />
            </div>
            <div className="form-group">
              <label>Notes</label>
              <input type="text" value={form.notes} placeholder="Optional notes..."
                onChange={e => setForm({ ...form, notes: e.target.value })}
                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-color)' }} />
            </div>
          </div>
          <button className="btn btn-primary" onClick={handleCreate} style={{ marginTop: 12 }}>Create Cycle</button>
        </div>
      )}

      {/* Cycle List */}
      {cycles.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 40 }}>
          <div style={{ fontSize: 48, marginBottom: 12 }}>🔄</div>
          <h3>No surveillance cycles yet</h3>
          <p style={{ color: 'var(--text-secondary)' }}>Create a cycle manually or auto-schedule from a certified project</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {cycles.map(c => {
            const project = projects.find(p => p.id === c.project_id)
            return (
              <div key={c.id} className="card" style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                cursor: 'pointer', padding: '12px 16px',
                borderLeft: `4px solid ${STATUS_COLORS[c.status] || '#999'}`,
              }} onClick={() => openCycle(c)}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>
                    C{c.cycle_number} — {CYCLE_LABELS[c.cycle_number] || 'Surveillance'}
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 2 }}>
                    {project?.title || c.project_id} · {c.scheduled_date}
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span className="badge" style={{
                    background: STATUS_COLORS[c.status] + '20',
                    color: STATUS_COLORS[c.status],
                    fontSize: 11, padding: '4px 10px',
                  }}>
                    {c.status}
                  </span>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
