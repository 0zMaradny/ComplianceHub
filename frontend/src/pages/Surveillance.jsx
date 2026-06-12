import { useState, useEffect } from 'react'

const TUV_BLUE = '#003D7A'
const TUV_RED = '#C00000'

const STATUS_COLORS = {
  scheduled: '#3498DB', in_progress: '#F39C12', completed: '#27AE60', overdue: TUV_RED,
}

const CYCLE_LABELS = {
  1: 'Year 1 Surveillance', 2: 'Year 2 Surveillance', 3: 'Year 3 Recertification',
}

const FINDING_TYPE_COLORS = {
  recurring_nc: TUV_RED, new_nc: '#E67E22', ofi: '#3498DB', observation: '#95A5A6',
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
  const [findingForm, setFindingForm] = useState({ clause: '', finding_type: 'new_nc', severity: 'Minor', description: '', previous_nc_id: '' })
  const [autoScheduleProj, setAutoScheduleProj] = useState('')
  const [autoScheduleDate, setAutoScheduleDate] = useState('')

  const loadData = () => {
    Promise.all([
      fetch(`${API}/surveillance/cycles`).then(r => r.json()).catch(() => ({ cycles: [] })),
      fetch(`${API}/projects`).then(r => r.json()).catch(() => ({ projects: [] })),
      fetch(`${API}/surveillance/dashboard`).then(r => r.json()).catch(() => ({})),
    ]).then(([c, p, s]) => { setCycles(c.cycles || []); setProjects(p.projects || []); setStats(s) })
  }

  useEffect(() => { loadData() }, [API])

  const loadFindings = async (cycleId) => {
    const r = await fetch(`${API}/surveillance/cycles/${cycleId}/findings`)
    setFindings((await r.json().catch(() => ({ findings: [] }))).findings || [])
  }

  const loadScope = async (cycleId) => {
    const r = await fetch(`${API}/surveillance/cycles/${cycleId}/scope`, { method: 'POST' })
    setScope(await r.json().catch(() => null))
  }

  const openCycle = async (cycle) => { setSelectedCycle(cycle); setScope(null); await loadFindings(cycle.id) }

  const handleCreate = async () => {
    if (!form.project_id || !form.scheduled_date) return
    const body = new URLSearchParams()
    Object.entries(form).forEach(([k, v]) => body.append(k, v))
    const r = await fetch(`${API}/surveillance/cycles`, {
      method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body,
    })
    if (r.ok) { setShowCreate(false); setForm({ project_id: '', cycle_number: 1, scheduled_date: '', notes: '' }); loadData() }
  }

  const handleAddFinding = async () => {
    if (!findingForm.clause || !findingForm.description || !selectedCycle) return
    const body = new URLSearchParams()
    Object.entries(findingForm).forEach(([k, v]) => body.append(k, v))
    const r = await fetch(`${API}/surveillance/cycles/${selectedCycle.id}/findings`, {
      method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body,
    })
    if (r.ok) { setShowAddFinding(false); setFindingForm({ clause: '', finding_type: 'new_nc', severity: 'Minor', description: '', previous_nc_id: '' }); loadFindings(selectedCycle.id) }
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

  const handleUpdateStatus = async (cycleId, status) => {
    await fetch(`${API}/surveillance/cycles/${cycleId}`, {
      method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status }),
    })
    loadData()
    if (selectedCycle?.id === cycleId) setSelectedCycle({ ...selectedCycle, status })
  }

  // Detail View
  if (selectedCycle) {
    const project = projects.find(p => p.id === selectedCycle.project_id)
    return (
      <div className="animate-fadeIn">
        <button className="btn btn-secondary mb-4" onClick={() => { setSelectedCycle(null); setScope(null) }}>
          ← Back to Surveillance
        </button>

        <div className="card mb-4">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="m-0 mb-1">Cycle {selectedCycle.cycle_number}: {CYCLE_LABELS[selectedCycle.cycle_number] || 'Surveillance'}</h2>
              <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                {project?.title || selectedCycle.project_id} · Scheduled: {selectedCycle.scheduled_date}
              </div>
            </div>
            <span className="badge" style={{ background: STATUS_COLORS[selectedCycle.status] + '20', color: STATUS_COLORS[selectedCycle.status], fontSize: 13, padding: '5px 12px' }}>
              {selectedCycle.status}
            </span>
          </div>
        </div>

        <div className="flex gap-2 mb-4 flex-wrap">
          <button className="btn btn-secondary" onClick={() => loadScope(selectedCycle.id)}>🔍 Generate Scope</button>
          <button className="btn btn-secondary" onClick={() => setShowAddFinding(!showAddFinding)}>+ Add Finding</button>
          {selectedCycle.status === 'scheduled' && (
            <button className="btn btn-primary" onClick={() => handleUpdateStatus(selectedCycle.id, 'in_progress')}>▶ Start Audit</button>
          )}
          {selectedCycle.status === 'in_progress' && (
            <button className="btn btn-primary" onClick={() => handleUpdateStatus(selectedCycle.id, 'completed')}>✓ Complete</button>
          )}
        </div>

        {scope && (
          <div className="card mb-4">
            <h3>Reduced Scope</h3>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{scope.rationale}</p>
            <div className="grid grid-cols-2 gap-3 mt-2">
              <div>
                <h4 className="text-xs" style={{ color: '#27AE60' }}>Included Clauses ({scope.included_clauses?.length || 0})</h4>
                <div className="flex flex-wrap gap-1 mt-1">
                  {(scope.included_clauses || []).map(c => (
                    <span key={c} className="text-xs px-1.5 py-0.5 rounded" style={{ background: '#E8F8F0' }}>{c}</span>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="text-xs" style={{ color: TUV_RED }}>Excluded Clauses ({scope.excluded_clauses?.length || 0})</h4>
                <div className="flex flex-wrap gap-1 mt-1">
                  {(scope.excluded_clauses || []).map(c => (
                    <span key={c} className="text-xs px-1.5 py-0.5 rounded" style={{ background: '#FEF2F2' }}>{c}</span>
                  ))}
                </div>
              </div>
            </div>
            {scope.manday_reduction_pct > 0 && (
              <div className="mt-2 text-xs" style={{ color: 'var(--text-secondary)' }}>Manday reduction: {scope.manday_reduction_pct}%</div>
            )}
          </div>
        )}

        {showAddFinding && (
          <div className="card mb-4">
            <h3 className="mb-3">Add Finding</h3>
            <div className="grid grid-cols-2 gap-3">
              {[
                { label: 'Clause *', key: 'clause', type: 'text', placeholder: 'e.g. 4.1' },
                { label: 'Type', key: 'finding_type', type: 'select', options: [
                  { value: 'new_nc', label: 'New NC' }, { value: 'recurring_nc', label: 'Recurring NC' },
                  { value: 'ofi', label: 'OFI' }, { value: 'observation', label: 'Observation' },
                ]},
                { label: 'Severity', key: 'severity', type: 'select', options: [
                  { value: 'Major', label: 'Major' }, { value: 'Minor', label: 'Minor' }, { value: 'OFI', label: 'OFI' },
                ]},
                { label: 'Previous NC ID', key: 'previous_nc_id', type: 'text', placeholder: 'NC-XXXXXXXX' },
              ].map(f => (
                <div key={f.key} className="form-group">
                  <label>{f.label}</label>
                  {f.type === 'select' ? (
                    <select value={findingForm[f.key]} onChange={e => setFindingForm({ ...findingForm, [f.key]: e.target.value })}
                      style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-color)' }}>
                      {f.options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                    </select>
                  ) : (
                    <input type="text" value={findingForm[f.key]} placeholder={f.placeholder}
                      onChange={e => setFindingForm({ ...findingForm, [f.key]: e.target.value })}
                      style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-color)' }} />
                  )}
                </div>
              ))}
            </div>
            <div className="form-group mt-2">
              <label>Description *</label>
              <textarea value={findingForm.description} rows={3} placeholder="Detailed finding description..."
                onChange={e => setFindingForm({ ...findingForm, description: e.target.value })}
                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--border-color)', resize: 'vertical' }} />
            </div>
            <div className="flex gap-2 mt-2">
              <button className="btn btn-primary" onClick={handleAddFinding}>Add Finding</button>
              <button className="btn btn-secondary" onClick={() => setShowAddFinding(false)}>Cancel</button>
            </div>
          </div>
        )}

        <div className="card">
          <h3>Findings ({findings.length})</h3>
          {findings.length === 0 ? (
            <div className="empty-state">No findings recorded yet</div>
          ) : (
            <div className="flex flex-col gap-2 mt-2">
              {findings.map(f => (
                <div key={f.id} className="p-2.5 rounded-md" style={{ border: '1px solid var(--border-color)', borderLeft: `4px solid ${FINDING_TYPE_COLORS[f.finding_type] || '#999'}` }}>
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-sm">{f.clause}</span>
                    <div className="flex gap-1.5">
                      <span className="badge" style={{ background: FINDING_TYPE_COLORS[f.finding_type] + '20', color: FINDING_TYPE_COLORS[f.finding_type], fontSize: 10, padding: '2px 8px' }}>
                        {f.finding_type.replace('_', ' ')}</span>
                      <span className="badge" style={{ background: f.severity === 'Major' ? TUV_RED + '20' : '#F39C12' + '20', color: f.severity === 'Major' ? TUV_RED : '#F39C12', fontSize: 10, padding: '2px 8px' }}>
                        {f.severity}</span>
                    </div>
                  </div>
                  <p className="text-xs mt-1 m-0" style={{ color: 'var(--text-secondary)' }}>{f.description}</p>
                  {f.previous_nc_id && <div className="text-xs mt-1" style={{ color: TUV_RED }}>↳ Recurring from {f.previous_nc_id}</div>}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    )
  }

  // List View
  return (
    <div className="animate-fadeIn">
      <div className="page-header">
        <h2>🔄 Surveillance & Recertification</h2>
        <p>Manage post-certification surveillance audit cycles and recertification</p>
      </div>

      {stats && (
        <div className="stats-grid mb-4">
          <div className="stat-card"><div className="stat-number">{stats.total_cycles ?? 0}</div><h3>Total Cycles</h3></div>
          <div className="stat-card"><div className="stat-number" style={{ color: '#3498DB' }}>{stats.upcoming_30d ?? 0}</div><h3>Upcoming (30d)</h3></div>
          <div className="stat-card"><div className="stat-number" style={{ color: TUV_RED }}>{stats.overdue ?? 0}</div><h3>Overdue</h3></div>
          <div className="stat-card"><div className="stat-number" style={{ color: '#27AE60' }}>{stats.completed ?? 0}</div><h3>Completed</h3></div>
        </div>
      )}

      <div className="flex gap-2 mb-4 flex-wrap items-center">
        <button className="btn btn-primary" onClick={() => setShowCreate(!showCreate)}>
          {showCreate ? '✕ Cancel' : '+ New Cycle'}
        </button>
        <button className="btn btn-secondary" onClick={async () => { await fetch(`${API}/surveillance/check-overdue`, { method: 'POST' }); loadData() }}>
          ⚠ Check Overdue
        </button>
      </div>

      <div className="card mb-4">
        <h3>Auto-Schedule Surveillance</h3>
        <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>Create 3 cycles (Y1, Y2 surveillance + Y3 recert) from certification date</p>
        <div className="flex gap-2 mt-2 flex-wrap">
          <select value={autoScheduleProj} onChange={e => setAutoScheduleProj(e.target.value)}
            className="px-3 py-1.5 rounded-md text-sm" style={{ border: '1px solid var(--border-color)', minWidth: 180 }}>
            <option value="">-- Select Project --</option>
            {projects.map(p => <option key={p.id} value={p.id}>{p.title}</option>)}
          </select>
          <input type="date" value={autoScheduleDate} onChange={e => setAutoScheduleDate(e.target.value)}
            className="px-3 py-1.5 rounded-md" style={{ border: '1px solid var(--border-color)' }} />
          <button className="btn btn-primary" onClick={handleAutoSchedule} disabled={!autoScheduleProj || !autoScheduleDate}>Auto-Schedule</button>
        </div>
      </div>

      {showCreate && (
        <div className="card mb-4">
          <h3 className="mb-3">Create Surveillance Cycle</h3>
          <div className="grid grid-cols-2 gap-3">
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
          <button className="btn btn-primary mt-3" onClick={handleCreate}>Create Cycle</button>
        </div>
      )}

      {cycles.length === 0 ? (
        <div className="card text-center p-10">
          <div className="text-5xl mb-3">🔄</div>
          <h3>No surveillance cycles yet</h3>
          <p style={{ color: 'var(--text-secondary)' }}>Create a cycle manually or auto-schedule from a certified project</p>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {cycles.map(c => {
            const project = projects.find(p => p.id === c.project_id)
            return (
              <div key={c.id} className="card flex items-center justify-between cursor-pointer p-3"
                style={{ borderLeft: `4px solid ${STATUS_COLORS[c.status] || '#999'}` }}
                onClick={() => openCycle(c)}>
                <div>
                  <div className="font-semibold text-sm">C{c.cycle_number} — {CYCLE_LABELS[c.cycle_number] || 'Surveillance'}</div>
                  <div className="text-xs mt-0.5" style={{ color: 'var(--text-secondary)' }}>
                    {project?.title || c.project_id} · {c.scheduled_date}
                  </div>
                </div>
                <span className="badge" style={{ background: STATUS_COLORS[c.status] + '20', color: STATUS_COLORS[c.status], fontSize: 11, padding: '4px 10px' }}>
                  {c.status}
                </span>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
