import { useState, useEffect, useCallback } from 'react'

/* ─── Audit Execution Module — Live Audit Day-by-Day ─── */

// Status colors
const STATUS = {
  pending:    { bg: '#F3F4F6', fg: '#6B7280', label: 'Pending' },
  conforming: { bg: '#D1FAE5', fg: '#065F46', label: 'Conforming' },
  minor_nc:   { bg: '#FEF3C7', fg: '#92400E', label: 'Minor NC' },
  major_nc:   { bg: '#FEE2E2', fg: '#991B1B', label: 'Major NC' },
  ofi:        { bg: '#DBEAFE', fg: '#1E40AF', label: 'OFI' },
  na:         { bg: '#E5E7EB', fg: '#374151', label: 'N/A' },
  planned:    { bg: '#F3F4F6', fg: '#6B7280', label: 'Planned' },
  in_progress:{ bg: '#DBEAFE', fg: '#1E40AF', label: 'In Progress' },
  completed:  { bg: '#D1FAE5', fg: '#065F46', label: 'Completed' },
  cancelled:  { bg: '#FEE2E2', fg: '#991B1B', label: 'Cancelled' },
}

const AUDIT_TYPES = [
  { value: 'stage1', label: 'Stage 1 (Documentation Review)' },
  { value: 'stage2', label: 'Stage 2 (Certification Audit)' },
  { value: 'surveillance', label: 'Surveillance' },
  { value: 'recertification', label: 'Recertification' },
  { value: 'transfer', label: 'Transfer Audit' },
]

const EVIDENCE_TYPES = ['document', 'interview', 'observation', 'record']

// ─── Main Page ───
export default function AuditProgram({ API }) {
  const [programs, setPrograms] = useState([])
  const [selected, setSelected] = useState(null)   // program overview object
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({
    title: '', client_name: '', client_key: '', standards: [],
    audit_type: 'stage2', lead_auditor: '', audit_team: '',
    start_date: '', end_date: '', location: '', notes: '',
  })

  const loadPrograms = useCallback(() => {
    fetch(`${API}/audit_programs`)
      .then(r => r.json())
      .then(d => setPrograms(d.programs || []))
  }, [API])

  useEffect(() => { loadPrograms() }, [loadPrograms])

  const openProgram = async (p) => {
    const r = await fetch(`${API}/audit_programs/${p.id}`)
    if (r.ok) setSelected(await r.json())
  }

  const handleCreate = async () => {
    if (!form.title || !form.client_name || !form.start_date || !form.end_date) return
    const body = new URLSearchParams()
    Object.entries(form).forEach(([k, v]) => {
      if (Array.isArray(v)) body.append(k, JSON.stringify(v))
      else body.append(k, v)
    })
    const r = await fetch(`${API}/audit_programs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body,
    })
    if (r.ok) {
      setShowCreate(false)
      setForm({ title: '', client_name: '', client_key: '', standards: [], audit_type: 'stage2', lead_auditor: '', audit_team: '', start_date: '', end_date: '', location: '', notes: '' })
      loadPrograms()
    }
  }

  const handleDelete = async (pid) => {
    if (!confirm('Delete this audit program and all its data?')) return
    await fetch(`${API}/audit_programs/${pid}`, { method: 'DELETE' })
    setSelected(null)
    loadPrograms()
  }

  // ── Detail View ──
  if (selected) {
    return <ProgramDetail
      API={API}
      program={selected}
      onBack={() => { setSelected(null); loadPrograms() }}
      onDelete={handleDelete}
    />
  }

  // ── List View ──
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <h2 style={{ margin: 0 }}>Audit Programs</h2>
          <p style={{ color: 'var(--gray-500)', margin: '4px 0 0', fontSize: 13 }}>Day-by-day audit execution — schedule, clause checklist, evidence & findings</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreate(true)}>+ New Audit Program</button>
      </div>

      {showCreate && (
        <div className="card" style={{ marginBottom: 20 }}>
          <h3 style={{ margin: '0 0 16px' }}>Create Audit Program</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <label className="form-label">Title *</label>
              <input className="form-input" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} placeholder="e.g. ABC Corp ISO 27001 Stage 2" />
            </div>
            <div>
              <label className="form-label">Client Name *</label>
              <input className="form-input" value={form.client_name} onChange={e => setForm({ ...form, client_name: e.target.value })} placeholder="Client organization name" />
            </div>
            <div>
              <label className="form-label">Client Key</label>
              <input className="form-input" value={form.client_key} onChange={e => setForm({ ...form, client_key: e.target.value })} placeholder="e.g. abc-corp" />
            </div>
            <div>
              <label className="form-label">Audit Type</label>
              <select className="form-input" value={form.audit_type} onChange={e => setForm({ ...form, audit_type: e.target.value })}>
                {AUDIT_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
              </select>
            </div>
            <div>
              <label className="form-label">Lead Auditor *</label>
              <input className="form-input" value={form.lead_auditor} onChange={e => setForm({ ...form, lead_auditor: e.target.value })} placeholder="Lead auditor name" />
            </div>
            <div>
              <label className="form-label">Audit Team</label>
              <input className="form-input" value={form.audit_team} onChange={e => setForm({ ...form, audit_team: e.target.value })} placeholder="Comma-separated names" />
            </div>
            <div>
              <label className="form-label">Start Date *</label>
              <input type="date" className="form-input" value={form.start_date} onChange={e => setForm({ ...form, start_date: e.target.value })} />
            </div>
            <div>
              <label className="form-label">End Date *</label>
              <input type="date" className="form-input" value={form.end_date} onChange={e => setForm({ ...form, end_date: e.target.value })} />
            </div>
            <div>
              <label className="form-label">Location</label>
              <input className="form-input" value={form.location} onChange={e => setForm({ ...form, location: e.target.value })} placeholder="Audit location" />
            </div>
            <div>
              <label className="form-label">Standards</label>
              <input className="form-input" value={form.standards.join(', ')} onChange={e => setForm({ ...form, standards: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })} placeholder="iso_27001, iso_27701" />
            </div>
          </div>
          <div style={{ marginTop: 12 }}>
            <label className="form-label">Notes</label>
            <textarea className="form-input" rows={2} value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} placeholder="Additional notes..." />
          </div>
          <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
            <button className="btn btn-primary" onClick={handleCreate}>Create Program</button>
            <button className="btn btn-secondary" onClick={() => setShowCreate(false)}>Cancel</button>
          </div>
        </div>
      )}

      {programs.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 40 }}>
          <p style={{ color: 'var(--gray-500)' }}>No audit programs yet. Create one to start planning your day-by-day audit.</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: 12 }}>
          {programs.map(p => (
            <div key={p.id} className="card" style={{ cursor: 'pointer' }} onClick={() => openProgram(p)}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h4 style={{ margin: '0 0 4px' }}>{p.title}</h4>
                  <div style={{ fontSize: 13, color: 'var(--gray-500)' }}>
                    {p.client_name} · {p.standards.join(', ')} · {p.audit_type}
                    {p.lead_auditor && ` · Lead: ${p.lead_auditor}`}
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--gray-400)', marginTop: 4 }}>
                    {p.start_date} → {p.end_date} {p.location && `· ${p.location}`}
                  </div>
                </div>
                <span className="badge" style={{
                  background: p.status === 'active' ? '#D1FAE5' : p.status === 'completed' ? '#DBEAFE' : '#F3F4F6',
                  color: p.status === 'active' ? '#065F46' : p.status === 'completed' ? '#1E40AF' : '#6B7280',
                  textTransform: 'capitalize',
                }}>{p.status}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ─── Program Detail View ───
function ProgramDetail({ API, program: initialProgram, onBack, onDelete }) {
  const [program, setProgram] = useState(initialProgram)
  const [activeTab, setActiveTab] = useState('schedule')
  const [selectedDay, setSelectedDay] = useState(1)
  const [showAddEntry, setShowAddEntry] = useState(false)
  const [showAddEvidence, setShowAddEvidence] = useState(false)
  const [editingCl, setEditingCl] = useState(null)

  // Entry form
  const [entryForm, setEntryForm] = useState({
    day: 1, date: '', start_time: '09:00', end_time: '10:00',
    department: '', auditor: '', clause_refs: [], standard: '',
    description: '', room: '',
  })

  // Evidence form
  const [evForm, setEvForm] = useState({
    clause_ref: '', standard: '', evidence_type: 'document',
    description: '', collected_by: '',
  })

  const refresh = async () => {
    const r = await fetch(`${API}/audit_programs/${program.program.id}`)
    if (r.ok) setProgram(await r.json())
  }

  const days = Object.keys(program.days || {}).map(k => program.days[k])
  const dayEntries = (program.days?.[`day_${selectedDay}`]?.entries) || []
  const dayChecklist = program.checklist_by_day || []
  const stats = program.checklist_stats || {}

  const addEntry = async () => {
    if (!entryForm.department || !entryForm.start_time) return
    const body = new URLSearchParams()
    Object.entries(entryForm).forEach(([k, v]) => {
      if (Array.isArray(v)) body.append(k, JSON.stringify(v))
      else body.append(k, v)
    })
    await fetch(`${API}/audit_programs/${program.program.id}/entries`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body,
    })
    setShowAddEntry(false)
    setEntryForm({ day: 1, date: '', start_time: '09:00', end_time: '10:00', department: '', auditor: '', clause_refs: [], standard: '', description: '', room: '' })
    refresh()
  }

  const addEvidence = async () => {
    if (!evForm.description || !evForm.collected_by) return
    const body = new URLSearchParams()
    Object.entries(evForm).forEach(([k, v]) => body.append(k, v))
    await fetch(`${API}/audit_programs/${program.program.id}/evidence`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body,
    })
    setShowAddEvidence(false)
    setEvForm({ clause_ref: '', standard: '', evidence_type: 'document', description: '', collected_by: '' })
    refresh()
  }

  const updateClStatus = async (itemId, newStatus, extra = {}) => {
    const payload = { status: newStatus, ...extra }
    await fetch(`${API}/checklist/${itemId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    setEditingCl(null)
    refresh()
  }

  const tabs = [
    { id: 'schedule', label: '📅 Schedule' },
    { id: 'checklist', label: '☑️ Checklist' },
    { id: 'findings', label: '⚠️ Findings' },
    { id: 'evidence', label: '📎 Evidence' },
    { id: 'summary', label: '📊 Summary' },
  ]

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 16 }}>
        <button className="btn btn-secondary" onClick={onBack} style={{ marginBottom: 8 }}>← Back to Programs</button>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h2 style={{ margin: '0 0 4px' }}>{program.program.title}</h2>
            <div style={{ color: 'var(--gray-500)', fontSize: 13 }}>
              {program.program.client_name} · {program.program.standards.join(', ')} · {program.program.audit_type}
            </div>
            <div style={{ color: 'var(--gray-400)', fontSize: 12, marginTop: 2 }}>
              {program.program.start_date} → {program.program.end_date}
              {program.program.location && ` · ${program.program.location}`}
              {program.program.lead_auditor && ` · Lead: ${program.program.lead_auditor}`}
            </div>
          </div>
          <button className="btn btn-danger" onClick={() => onDelete(program.program.id)}>Delete</button>
        </div>
      </div>

      {/* Stats Bar */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 8, marginBottom: 16 }}>
        {[
          { label: 'Total Clauses', value: stats.total || 0, color: '#6B7280' },
          { label: 'Reviewed', value: stats.reviewed || 0, color: '#059669' },
          { label: 'Conforming', value: stats.conforming || 0, color: '#065F46' },
          { label: 'Minor NC', value: stats.minor_nc || 0, color: '#D97706' },
          { label: 'Major NC', value: stats.major_nc || 0, color: '#DC2626' },
          { label: 'OFI', value: stats.ofi || 0, color: '#2563EB' },
        ].map(s => (
          <div key={s.label} className="card" style={{ textAlign: 'center', padding: '8px 4px' }}>
            <div style={{ fontSize: 20, fontWeight: 700, color: s.color }}>{s.value}</div>
            <div style={{ fontSize: 11, color: 'var(--gray-500)' }}>{s.label}</div>
          </div>
        ))}
      </div>
      {/* Completion bar */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
          <span>Audit Progress</span>
          <span style={{ fontWeight: 600 }}>{stats.completion_pct || 0}%</span>
        </div>
        <div style={{ height: 8, background: '#E5E7EB', borderRadius: 4, overflow: 'hidden' }}>
          <div style={{
            height: '100%', width: `${stats.completion_pct || 0}%`,
            background: (stats.completion_pct || 0) > 75 ? '#059669' : (stats.completion_pct || 0) > 40 ? '#D97706' : '#DC2626',
            borderRadius: 4, transition: 'width 0.3s',
          }} />
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 4, marginBottom: 16, borderBottom: '1px solid var(--gray-200)', paddingBottom: 0 }}>
        {tabs.map(t => (
          <button
            key={t.id}
            className={`btn ${activeTab === t.id ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab(t.id)}
            style={{ borderRadius: '6px 6px 0 0' }}
          >{t.label}</button>
        ))}
      </div>

      {/* ── Schedule Tab ── */}
      {activeTab === 'schedule' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <h3 style={{ margin: 0 }}>Day-by-Day Schedule</h3>
            <button className="btn btn-primary" onClick={() => setShowAddEntry(true)}>+ Add Time Slot</button>
          </div>

          {/* Day selector */}
          {days.length > 0 && (
            <div style={{ display: 'flex', gap: 4, marginBottom: 12, flexWrap: 'wrap' }}>
              {days.map(d => (
                <button
                  key={d.day}
                  className={`btn ${selectedDay === d.day ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setSelectedDay(d.day)}
                >Day {d.day} ({d.date})</button>
              ))}
            </div>
          )}

          {showAddEntry && (
            <div className="card" style={{ marginBottom: 12 }}>
              <h4 style={{ margin: '0 0 12px' }}>Add Time Slot</h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: 8 }}>
                <div>
                  <label className="form-label">Day</label>
                  <input type="number" className="form-input" min={1} value={entryForm.day} onChange={e => setEntryForm({ ...entryForm, day: +e.target.value })} />
                </div>
                <div>
                  <label className="form-label">Date</label>
                  <input type="date" className="form-input" value={entryForm.date} onChange={e => setEntryForm({ ...entryForm, date: e.target.value })} />
                </div>
                <div>
                  <label className="form-label">Start</label>
                  <input type="time" className="form-input" value={entryForm.start_time} onChange={e => setEntryForm({ ...entryForm, start_time: e.target.value })} />
                </div>
                <div>
                  <label className="form-label">End</label>
                  <input type="time" className="form-input" value={entryForm.end_time} onChange={e => setEntryForm({ ...entryForm, end_time: e.target.value })} />
                </div>
                <div>
                  <label className="form-label">Department *</label>
                  <input className="form-input" value={entryForm.department} onChange={e => setEntryForm({ ...entryForm, department: e.target.value })} placeholder="e.g. IT, HR, Operations" />
                </div>
                <div>
                  <label className="form-label">Auditor</label>
                  <input className="form-input" value={entryForm.auditor} onChange={e => setEntryForm({ ...entryForm, auditor: e.target.value })} placeholder="Auditor name" />
                </div>
                <div>
                  <label className="form-label">Standard</label>
                  <input className="form-input" value={entryForm.standard} onChange={e => setEntryForm({ ...entryForm, standard: e.target.value })} placeholder="e.g. iso_27001" />
                </div>
                <div>
                  <label className="form-label">Room</label>
                  <input className="form-input" value={entryForm.room} onChange={e => setEntryForm({ ...entryForm, room: e.target.value })} placeholder="Room / location" />
                </div>
              </div>
              <div style={{ marginTop: 8 }}>
                <label className="form-label">Clause Refs (comma-separated)</label>
                <input className="form-input" value={entryForm.clause_refs.join(', ')} onChange={e => setEntryForm({ ...entryForm, clause_refs: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })} placeholder="4.1, 4.2, 5.1, A.5.1" />
              </div>
              <div style={{ marginTop: 8 }}>
                <label className="form-label">Description</label>
                <input className="form-input" value={entryForm.description} onChange={e => setEntryForm({ ...entryForm, description: e.target.value })} placeholder="What will be audited..." />
              </div>
              <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                <button className="btn btn-primary" onClick={addEntry}>Add Slot</button>
                <button className="btn btn-secondary" onClick={() => setShowAddEntry(false)}>Cancel</button>
              </div>
            </div>
          )}

          {dayEntries.length === 0 ? (
            <div className="card" style={{ textAlign: 'center', padding: 30, color: 'var(--gray-500)' }}>
              No time slots for Day {selectedDay}. Add one above.
            </div>
          ) : (
            <table className="table" style={{ width: '100%' }}>
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Department</th>
                  <th>Auditor</th>
                  <th>Clauses</th>
                  <th>Description</th>
                  <th>Room</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {dayEntries.map(e => (
                  <tr key={e.id}>
                    <td style={{ whiteSpace: 'nowrap', fontSize: 13 }}>{e.start_time}–{e.end_time}</td>
                    <td>{e.department}</td>
                    <td>{e.auditor || '—'}</td>
                    <td style={{ maxWidth: 200, fontSize: 12 }}>{e.clause_refs?.join(', ') || '—'}</td>
                    <td style={{ fontSize: 13 }}>{e.description || '—'}</td>
                    <td>{e.room || '—'}</td>
                    <td>
                      <span className="badge" style={{
                        background: STATUS[e.status]?.bg || '#F3F4F6',
                        color: STATUS[e.status]?.fg || '#6B7280',
                        fontSize: 11,
                      }}>{STATUS[e.status]?.label || e.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* ── Checklist Tab ── */}
      {activeTab === 'checklist' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <h3 style={{ margin: 0 }}>Clause Checklist</h3>
            <div style={{ display: 'flex', gap: 8 }}>
              <select className="form-input" style={{ width: 'auto' }} value={selectedDay} onChange={e => setSelectedDay(+e.target.value)}>
                {days.map(d => <option key={d.day} value={d.day}>Day {d.day}</option>)}
                <option value={0}>All Days</option>
              </select>
              <button className="btn btn-primary" onClick={async () => {
                await fetch(`${API}/audit_programs/${program.program.id}/checklist/build`, { method: 'POST' })
                refresh()
              }}>🔄 Build Checklist</button>
            </div>
          </div>

          {/* Standards filter */}
          <div style={{ display: 'flex', gap: 4, marginBottom: 12 }}>
            {program.program.standards.map(std => (
              <span key={std} className="badge" style={{ background: '#DBEAFE', color: '#1E40AF' }}>{std}</span>
            ))}
          </div>

          {editingCl && (
            <ClauseEditor
              item={editingCl}
              onSave={updateClStatus}
              onCancel={() => setEditingCl(null)}
            />
          )}

          <ChecklistTable
            API={API}
            programId={program.program.id}
            day={selectedDay}
            onEdit={setEditingCl}
            refresh={refresh}
          />
        </div>
      )}

      {/* ── Findings Tab ── */}
      {activeTab === 'findings' && (
        <div>
          <h3 style={{ margin: '0 0 12px' }}>Findings Register</h3>
          {(!program.ncs || program.ncs.length === 0) ? (
            <div className="card" style={{ textAlign: 'center', padding: 30, color: 'var(--gray-500)' }}>
              No findings recorded yet. Findings are auto-populated from the checklist.
            </div>
          ) : (
            <div style={{ display: 'grid', gap: 8 }}>
              {program.ncs.map((nc, i) => (
                <div key={i} className="card" style={{ borderLeft: `4px solid ${nc.severity === 'major_nc' || nc.severity === 'Major' ? '#DC2626' : nc.severity === 'ofi' || nc.severity === 'OFI' ? '#2563EB' : '#D97706'}` }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <div>
                      <strong>{nc.clause}</strong> — {nc.title}
                      <span className="badge" style={{
                        marginLeft: 8,
                        background: nc.severity === 'major_nc' || nc.severity === 'Major' ? '#FEE2E2' : nc.severity === 'ofi' || nc.severity === 'OFI' ? '#DBEAFE' : '#FEF3C7',
                        color: nc.severity === 'major_nc' || nc.severity === 'Major' ? '#991B1B' : nc.severity === 'ofi' || nc.severity === 'OFI' ? '#1E40AF' : '#92400E',
                      }}>{nc.severity}</span>
                    </div>
                    <span style={{ fontSize: 12, color: 'var(--gray-500)' }}>{nc.standard}</span>
                  </div>
                  {nc.description && <p style={{ margin: '8px 0 0', fontSize: 13 }}>{nc.description}</p>}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Evidence Tab ── */}
      {activeTab === 'evidence' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <h3 style={{ margin: 0 }}>Evidence Register ({program.evidence_count || 0})</h3>
            <button className="btn btn-primary" onClick={() => setShowAddEvidence(true)}>+ Add Evidence</button>
          </div>

          {showAddEvidence && (
            <div className="card" style={{ marginBottom: 12 }}>
              <h4 style={{ margin: '0 0 12px' }}>Record Evidence</h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8 }}>
                <div>
                  <label className="form-label">Clause Ref</label>
                  <input className="form-input" value={evForm.clause_ref} onChange={e => setEvForm({ ...evForm, clause_ref: e.target.value })} placeholder="e.g. 4.1, A.5.1" />
                </div>
                <div>
                  <label className="form-label">Standard</label>
                  <input className="form-input" value={evForm.standard} onChange={e => setEvForm({ ...evForm, standard: e.target.value })} placeholder="e.g. iso_27001" />
                </div>
                <div>
                  <label className="form-label">Type</label>
                  <select className="form-input" value={evForm.evidence_type} onChange={e => setEvForm({ ...evForm, evidence_type: e.target.value })}>
                    {EVIDENCE_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
              </div>
              <div style={{ marginTop: 8 }}>
                <label className="form-label">Description *</label>
                <input className="form-input" value={evForm.description} onChange={e => setEvForm({ ...evForm, description: e.target.value })} placeholder="What evidence was collected..." />
              </div>
              <div style={{ marginTop: 8 }}>
                <label className="form-label">Collected By *</label>
                <input className="form-input" value={evForm.collected_by} onChange={e => setEvForm({ ...evForm, collected_by: e.target.value })} placeholder="Auditor name" />
              </div>
              <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                <button className="btn btn-primary" onClick={addEvidence}>Record</button>
                <button className="btn btn-secondary" onClick={() => setShowAddEvidence(false)}>Cancel</button>
              </div>
            </div>
          )}

          <EvidenceTable API={API} programId={program.program.id} />
        </div>
      )}

      {/* ── Summary Tab ── */}
      {activeTab === 'summary' && (
        <div>
          <h3 style={{ margin: '0 0 12px' }}>Audit Summary</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div className="card">
              <h4 style={{ margin: '0 0 8px' }}>Program Info</h4>
              <table className="table">
                <tbody>
                  <tr><td><strong>Title</strong></td><td>{program.program.title}</td></tr>
                  <tr><td><strong>Client</strong></td><td>{program.program.client_name}</td></tr>
                  <tr><td><strong>Type</strong></td><td>{program.program.audit_type}</td></tr>
                  <tr><td><strong>Standards</strong></td><td>{program.program.standards.join(', ')}</td></tr>
                  <tr><td><strong>Dates</strong></td><td>{program.program.start_date} → {program.program.end_date}</td></tr>
                  <tr><td><strong>Lead Auditor</strong></td><td>{program.program.lead_auditor || '—'}</td></tr>
                  <tr><td><strong>Location</strong></td><td>{program.program.location || '—'}</td></tr>
                </tbody>
              </table>
            </div>
            <div className="card">
              <h4 style={{ margin: '0 0 8px' }}>Checklist Summary</h4>
              <table className="table">
                <tbody>
                  <tr><td><strong>Total Clauses</strong></td><td>{stats.total || 0}</td></tr>
                  <tr><td><strong>Reviewed</strong></td><td>{stats.reviewed || 0}</td></tr>
                  <tr><td><strong>Conforming</strong></td><td style={{ color: '#065F46' }}>{stats.conforming || 0}</td></tr>
                  <tr><td><strong>Minor NC</strong></td><td style={{ color: '#D97706' }}>{stats.minor_nc || 0}</td></tr>
                  <tr><td><strong>Major NC</strong></td><td style={{ color: '#DC2626' }}>{stats.major_nc || 0}</td></tr>
                  <tr><td><strong>OFI</strong></td><td style={{ color: '#2563EB' }}>{stats.ofi || 0}</td></tr>
                  <tr><td><strong>N/A</strong></td><td>{stats.na || 0}</td></tr>
                  <tr style={{ borderTop: '2px solid var(--gray-300)' }}>
                    <td><strong>Completion</strong></td><td><strong>{stats.completion_pct || 0}%</strong></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Daily breakdown */}
          <div className="card" style={{ marginTop: 12 }}>
            <h4 style={{ margin: '0 0 8px' }}>Daily Breakdown</h4>
            {days.length === 0 ? (
              <p style={{ color: 'var(--gray-500)' }}>No days scheduled yet.</p>
            ) : (
              <table className="table">
                <thead>
                  <tr><th>Day</th><th>Date</th><th>Time Slots</th></tr>
                </thead>
                <tbody>
                  {days.map(d => (
                    <tr key={d.day}>
                      <td>Day {d.day}</td>
                      <td>{d.date}</td>
                      <td>{d.entries?.length || 0}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// ─── Checklist Table (fetches its own data) ───
function ChecklistTable({ API, programId, day, onEdit, refresh }) {
  const [items, setItems] = useState([])
  const [filterStd, setFilterStd] = useState('')
  const [filterStatus, setFilterStatus] = useState('')

  useEffect(() => {
    const params = new URLSearchParams()
    if (day > 0) params.set('day', day)
    if (filterStd) params.set('standard', filterStd)
    if (filterStatus) params.set('status', filterStatus)
    fetch(`${API}/audit_programs/${programId}/checklist?${params}`)
      .then(r => r.json())
      .then(d => setItems(d.checklist || []))
  }, [API, programId, day, filterStatus, filterStd])

  const standards = [...new Set(items.map(i => i.standard))]

  return (
    <div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
        <select className="form-input" style={{ width: 'auto' }} value={filterStd} onChange={e => setFilterStd(e.target.value)}>
          <option value="">All Standards</option>
          {standards.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <select className="form-input" style={{ width: 'auto' }} value={filterStatus} onChange={e => setFilterStatus(e.target.value)}>
          <option value="">All Statuses</option>
          {Object.entries(STATUS).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
        </select>
        <span style={{ fontSize: 12, color: 'var(--gray-500)', alignSelf: 'center' }}>{items.length} items</span>
      </div>

      {items.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 30, color: 'var(--gray-500)' }}>
          No checklist items. Click "Build Checklist" to generate from standards.
        </div>
      ) : (
        <table className="table" style={{ width: '100%' }}>
          <thead>
            <tr>
              <th>Clause</th>
              <th>Title</th>
              <th>Standard</th>
              <th>Status</th>
              <th>Auditor Notes</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {items.map(item => {
              const st = STATUS[item.status] || STATUS.pending
              return (
                <tr key={item.id}>
                  <td style={{ fontWeight: 600, whiteSpace: 'nowrap' }}>{item.clause_ref}</td>
                  <td style={{ fontSize: 13 }}>{item.clause_title}</td>
                  <td style={{ fontSize: 12 }}>{item.standard}</td>
                  <td>
                    <span className="badge" style={{ background: st.bg, color: st.fg }}>{st.label}</span>
                  </td>
                  <td style={{ fontSize: 12, maxWidth: 200 }}>{item.auditor_notes || '—'}</td>
                  <td>
                    <button className="btn btn-secondary" style={{ padding: '2px 8px', fontSize: 12 }} onClick={() => onEdit(item)}>Update</button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      )}
    </div>
  )
}

// ─── Clause Editor Modal ───
function ClauseEditor({ item, onSave, onCancel }) {
  const [status, setStatus] = useState(item.status)
  const [notes, setNotes] = useState(item.auditor_notes || '')
  const [severity, setSeverity] = useState(item.severity || 'Minor')
  const [ncDesc, setNcDesc] = useState(item.nc_description || '')
  const [ofiDesc, setOfiDesc] = useState(item.ofi_description || '')
  const [auditee, setAuditee] = useState(item.auditee || '')

  const isNC = status === 'minor_nc' || status === 'major_nc'
  const isOFI = status === 'ofi'

  return (
    <div className="card" style={{ marginBottom: 16, border: '2px solid var(--primary, #003D7A)' }}>
      <h4 style={{ margin: '0 0 4px' }}>Update: {item.clause_ref} — {item.clause_title}</h4>
      <p style={{ margin: '0 0 12px', fontSize: 12, color: 'var(--gray-500)' }}>{item.standard} · {item.evidence_required}</p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 8 }}>
        <div>
          <label className="form-label">Status</label>
          <select className="form-input" value={status} onChange={e => setStatus(e.target.value)}>
            {Object.entries(STATUS).filter(([k]) => !['planned', 'in_progress', 'completed', 'cancelled'].includes(k)).map(([k, v]) => (
              <option key={k} value={k}>{v.label}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="form-label">Auditee</label>
          <input className="form-input" value={auditee} onChange={e => setAuditee(e.target.value)} placeholder="Person interviewed" />
        </div>
      </div>

      {isNC && (
        <>
          <div style={{ marginBottom: 8 }}>
            <label className="form-label">Severity</label>
            <select className="form-input" value={severity} onChange={e => setSeverity(e.target.value)}>
              <option value="Minor">Minor NC</option>
              <option value="Major">Major NC</option>
            </select>
          </div>
          <div style={{ marginBottom: 8 }}>
            <label className="form-label">NC Description *</label>
            <textarea className="form-input" rows={3} value={ncDesc} onChange={e => setNcDesc(e.target.value)} placeholder="Describe the nonconformity — what requirement was not met, what evidence was found..." />
          </div>
        </>
      )}

      {isOFI && (
        <div style={{ marginBottom: 8 }}>
          <label className="form-label">OFI Description *</label>
          <textarea className="form-input" rows={2} value={ofiDesc} onChange={e => setOfiDesc(e.target.value)} placeholder="Describe the opportunity for improvement..." />
        </div>
      )}

      <div style={{ marginBottom: 8 }}>
        <label className="form-label">Auditor Notes</label>
        <textarea className="form-input" rows={2} value={notes} onChange={e => setNotes(e.target.value)} placeholder="General notes, evidence references..." />
      </div>

      <div style={{ display: 'flex', gap: 8 }}>
        <button className="btn btn-primary" onClick={() => {
          const extra = { auditor_notes: notes, auditee }
          if (isNC) {
            extra.severity = severity
            extra.nc_description = ncDesc
            if (status === 'minor_nc' && severity === 'Major') extra.status = 'major_nc'
            if (status === 'major_nc' && severity === 'Minor') extra.status = 'minor_nc'
          }
          if (isOFI) extra.ofi_description = ofiDesc
          onSave(item.id, status, extra)
        }}>Save</button>
        <button className="btn btn-secondary" onClick={onCancel}>Cancel</button>
      </div>
    </div>
  )
}

// ─── Evidence Table ───
function EvidenceTable({ API, programId }) {
  const [items, setItems] = useState([])

  useEffect(() => {
    fetch(`${API}/audit_programs/${programId}/evidence`)
      .then(r => r.json())
      .then(d => setItems(d.evidence || []))
  }, [API, programId])

  if (items.length === 0) {
    return <div className="card" style={{ textAlign: 'center', padding: 30, color: 'var(--gray-500)' }}>No evidence recorded yet.</div>
  }

  return (
    <table className="table" style={{ width: '100%' }}>
      <thead>
        <tr>
          <th>Clause</th>
          <th>Type</th>
          <th>Description</th>
          <th>Collected By</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {items.map(ev => (
          <tr key={ev.id}>
            <td style={{ fontWeight: 600 }}>{ev.clause_ref}</td>
            <td style={{ textTransform: 'capitalize' }}>{ev.evidence_type}</td>
            <td style={{ fontSize: 13 }}>{ev.description}</td>
            <td>{ev.collected_by}</td>
            <td>
              <span className="badge" style={{
                background: ev.status === 'reviewed' ? '#D1FAE5' : ev.status === 'rejected' ? '#FEE2E2' : '#FEF3C7',
                color: ev.status === 'reviewed' ? '#065F46' : ev.status === 'rejected' ? '#991B1B' : '#92400E',
                textTransform: 'capitalize',
              }}>{ev.status}</span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
