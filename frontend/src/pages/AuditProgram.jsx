import { useState, useEffect, useCallback } from 'react'

const STATUS = {
  pending:    { bg: '#F3F4F6', fg: '#6B7280', label: 'Pending' },
  conforming: { bg: '#D1FAE5', fg: '#065F46', label: 'Conforming' },
  minor_nc:   { bg: '#FEF3C7', fg: '#92400E', label: 'Minor NC' },
  major_nc:   { bg: '#FEE2E2', fg: '#991B1B', label: 'Major NC' },
  ofi:        { bg: '#DBEAFE', fg: '#1E40AF', label: 'OFI' },
  na:         { bg: '#E5E7EB', fg: '#374151', label: 'N/A' },
}

const AUDIT_TYPES = [
  { value: 'stage1', label: 'Stage 1 (Documentation Review)' },
  { value: 'stage2', label: 'Stage 2 (Certification Audit)' },
  { value: 'surveillance', label: 'Surveillance' },
  { value: 'recertification', label: 'Recertification' },
  { value: 'transfer', label: 'Transfer Audit' },
]

const EVIDENCE_TYPES = ['document', 'interview', 'observation', 'record']

export default function AuditProgram({ API }) {
  const [programs, setPrograms] = useState([])
  const [selected, setSelected] = useState(null)
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({
    title: '', client_name: '', client_key: '', standards: [],
    audit_type: 'stage2', lead_auditor: '', audit_team: '',
    start_date: '', end_date: '', location: '', notes: '',
  })

  const loadPrograms = useCallback(() => {
    fetch(`${API}/audit_programs`).then(r => r.json()).then(d => setPrograms(d.programs || []))
  }, [API])

  useEffect(() => { loadPrograms() }, [loadPrograms])

  const openProgram = async (p) => {
    const r = await fetch(`${API}/audit_programs/${p.id}`)
    if (r.ok) setSelected(await r.json())
  }

  const handleCreate = async () => {
    if (!form.title || !form.client_name || !form.start_date || !form.end_date) return
    const body = new URLSearchParams()
    Object.entries(form).forEach(([k, v]) => body.append(k, Array.isArray(v) ? JSON.stringify(v) : v))
    const r = await fetch(`${API}/audit_programs`, {
      method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body,
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
    setSelected(null); loadPrograms()
  }

  if (selected) {
    return <ProgramDetail API={API} program={selected} onBack={() => { setSelected(null); loadPrograms() }} onDelete={handleDelete} />
  }

  return (
    <div className="animate-fadeIn">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="m-0">Audit Programs</h2>
          <p className="text-sm mt-1" style={{ color: 'var(--gray-500)' }}>Day-by-day audit execution — clause checklist, evidence & findings</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreate(true)}>+ New Audit Program</button>
      </div>

      {showCreate && (
        <div className="card mb-5">
          <h3 className="m-0 mb-4">Create Audit Program</h3>
          <div className="grid grid-cols-2 gap-3">
            {[
              { label: 'Title *', key: 'title', placeholder: 'e.g. ABC Corp ISO 27001 Stage 2' },
              { label: 'Client Name *', key: 'client_name', placeholder: 'Client organization name' },
              { label: 'Client Key', key: 'client_key', placeholder: 'e.g. abc-corp' },
              { label: 'Audit Type', key: 'audit_type', type: 'select', options: AUDIT_TYPES },
              { label: 'Lead Auditor', key: 'lead_auditor', placeholder: 'Lead auditor name' },
              { label: 'Audit Team', key: 'audit_team', placeholder: 'Comma-separated names' },
              { label: 'Start Date *', key: 'start_date', type: 'date' },
              { label: 'End Date *', key: 'end_date', type: 'date' },
              { label: 'Location', key: 'location', placeholder: 'Audit location' },
              { label: 'Standards', key: 'standards', placeholder: 'iso_27001, iso_27701' },
            ].map(f => (
              <div key={f.key}>
                <label className="form-label">{f.label}</label>
                {f.type === 'select' ? (
                  <select className="form-input" value={form[f.key]} onChange={e => setForm({ ...form, [f.key]: e.target.value })}>
                    {f.options.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                  </select>
                ) : f.type === 'date' ? (
                  <input type="date" className="form-input" value={form[f.key]}
                    onChange={e => setForm({ ...form, [f.key]: e.target.value })} />
                ) : f.key === 'standards' ? (
                  <input className="form-input" value={form.standards.join(', ')}
                    onChange={e => setForm({ ...form, standards: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                    placeholder={f.placeholder} />
                ) : (
                  <input className="form-input" value={form[f.key]}
                    onChange={e => setForm({ ...form, [f.key]: e.target.value })} placeholder={f.placeholder} />
                )}
              </div>
            ))}
          </div>
          <div className="mt-3">
            <label className="form-label">Notes</label>
            <textarea className="form-input" rows={2} value={form.notes}
              onChange={e => setForm({ ...form, notes: e.target.value })} placeholder="Additional notes..." />
          </div>
          <div className="flex gap-2 mt-4">
            <button className="btn btn-primary" onClick={handleCreate}>Create Program</button>
            <button className="btn btn-secondary" onClick={() => setShowCreate(false)}>Cancel</button>
          </div>
        </div>
      )}

      {programs.length === 0 ? (
        <div className="card text-center p-10">
          <p style={{ color: 'var(--gray-500)' }}>No audit programs yet. Create one to start your live audit.</p>
        </div>
      ) : (
        <div className="grid gap-3">
          {programs.map(p => (
            <div key={p.id} className="card cursor-pointer" onClick={() => openProgram(p)}>
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="m-0 mb-1">{p.title}</h4>
                  <div className="text-sm" style={{ color: 'var(--gray-500)' }}>
                    {p.client_name} · {p.standards.join(', ')} · {p.audit_type}
                    {p.lead_auditor && ` · Lead: ${p.lead_auditor}`}
                  </div>
                  <div className="text-xs mt-1" style={{ color: 'var(--gray-400)' }}>
                    {p.start_date} → {p.end_date} {p.location && `· ${p.location}`}
                  </div>
                </div>
                <span className="badge capitalize" style={{
                  background: p.status === 'active' ? '#D1FAE5' : p.status === 'completed' ? '#DBEAFE' : '#F3F4F6',
                  color: p.status === 'active' ? '#065F46' : p.status === 'completed' ? '#1E40AF' : '#6B7280',
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
  const [activeTab, setActiveTab] = useState('checklist')
  const [showAddEvidence, setShowAddEvidence] = useState(false)
  const [editingCl, setEditingCl] = useState(null)
  const [evForm, setEvForm] = useState({ clause_ref: '', standard: '', evidence_type: 'document', description: '', collected_by: '', file: null })

  const refresh = async () => {
    const r = await fetch(`${API}/audit_programs/${program.program.id}`)
    if (r.ok) setProgram(await r.json())
  }

  const stats = program.checklist_stats || {}

  const addEvidence = async () => {
    if (!evForm.description || !evForm.collected_by) return
    const body = new FormData()
    body.append('clause_ref', evForm.clause_ref)
    body.append('standard', evForm.standard)
    body.append('evidence_type', evForm.evidence_type)
    body.append('description', evForm.description)
    body.append('collected_by', evForm.collected_by)
    if (evForm.file) body.append('file', evForm.file)
    await fetch(`${API}/audit_programs/${program.program.id}/evidence`, { method: 'POST', body })
    setShowAddEvidence(false)
    setEvForm({ clause_ref: '', standard: '', evidence_type: 'document', description: '', collected_by: '', file: null })
    refresh()
  }

  const updateClStatus = async (itemId, newStatus, extra = {}) => {
    await fetch(`${API}/checklist/${itemId}`, {
      method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status: newStatus, ...extra }),
    })
    setEditingCl(null); refresh()
  }

  const tabs = [
    { id: 'checklist', label: '☑️ Clause Checklist' },
    { id: 'findings', label: '⚠️ Findings' },
    { id: 'evidence', label: '📎 Evidence' },
    { id: 'summary', label: '📊 Summary' },
  ]

  return (
    <div className="animate-fadeIn">
      <div className="mb-4">
        <button className="btn btn-secondary mb-2" onClick={onBack}>← Back to Programs</button>
        <div className="flex justify-between items-start">
          <div>
            <h2 className="m-0 mb-1">{program.program.title}</h2>
            <div className="text-sm" style={{ color: 'var(--gray-500)' }}>
              {program.program.client_name} · {program.program.standards.join(', ')} · {program.program.audit_type}
            </div>
            <div className="text-xs mt-0.5" style={{ color: 'var(--gray-400)' }}>
              {program.program.start_date} → {program.program.end_date}
              {program.program.location && ` · ${program.program.location}`}
              {program.program.lead_auditor && ` · Lead: ${program.program.lead_auditor}`}
            </div>
          </div>
          <button className="btn btn-danger" onClick={() => onDelete(program.program.id)}>Delete</button>
        </div>
      </div>

      <div className="grid grid-cols-6 gap-2 mb-4">
        {[
          { label: 'Total Clauses', value: stats.total || 0, color: '#6B7280' },
          { label: 'Reviewed', value: stats.reviewed || 0, color: '#059669' },
          { label: 'Conforming', value: stats.conforming || 0, color: '#065F46' },
          { label: 'Minor NC', value: stats.minor_nc || 0, color: '#D97706' },
          { label: 'Major NC', value: stats.major_nc || 0, color: '#DC2626' },
          { label: 'OFI', value: stats.ofi || 0, color: '#2563EB' },
        ].map(s => (
          <div key={s.label} className="card text-center p-2">
            <div className="text-xl font-bold" style={{ color: s.color }}>{s.value}</div>
            <div className="text-xs" style={{ color: 'var(--gray-500)' }}>{s.label}</div>
          </div>
        ))}
      </div>

      <div className="mb-4">
        <div className="flex justify-between text-xs mb-1">
          <span>Audit Progress</span>
          <span className="font-semibold">{stats.completion_pct || 0}%</span>
        </div>
        <div className="h-2 rounded overflow-hidden" style={{ background: '#E5E7EB' }}>
          <div className="h-full rounded transition-all duration-300" style={{
            width: `${stats.completion_pct || 0}%`,
            background: (stats.completion_pct || 0) > 75 ? '#059669' : (stats.completion_pct || 0) > 40 ? '#D97706' : '#DC2626',
          }} />
        </div>
      </div>

      <div className="flex gap-1 mb-4" style={{ borderBottom: '1px solid var(--gray-200)', paddingBottom: 0 }}>
        {tabs.map(t => (
          <button key={t.id} className={`btn ${activeTab === t.id ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab(t.id)}
            style={{ borderRadius: '6px 6px 0 0' }}>{t.label}</button>
        ))}
      </div>

      {activeTab === 'checklist' && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="m-0">Clause Checklist</h3>
            <button className="btn btn-primary" onClick={async () => {
              await fetch(`${API}/audit_programs/${program.program.id}/checklist/build`, { method: 'POST' })
              refresh()
            }}>🔄 Build Checklist</button>
          </div>
          <div className="flex gap-1 mb-3">
            {program.program.standards.map(std => (
              <span key={std} className="badge" style={{ background: '#DBEAFE', color: '#1E40AF' }}>{std}</span>
            ))}
          </div>
          {editingCl && <ClauseEditor item={editingCl} onSave={updateClStatus} onCancel={() => setEditingCl(null)} />}
          <ChecklistTable API={API} programId={program.program.id} onEdit={setEditingCl} refresh={refresh} />
        </div>
      )}

      {activeTab === 'findings' && (
        <div>
          <h3 className="m-0 mb-3">Findings Register</h3>
          {(!program.ncs || program.ncs.length === 0) ? (
            <div className="card text-center p-8" style={{ color: 'var(--gray-500)' }}>
              No findings recorded yet. Findings are auto-populated from the checklist.
            </div>
          ) : (
            <div className="grid gap-2">
              {program.ncs.map((nc, i) => (
                <div key={i} className="card" style={{ borderLeft: `4px solid ${nc.severity === 'major_nc' || nc.severity === 'Major' ? '#DC2626' : nc.severity === 'ofi' || nc.severity === 'OFI' ? '#2563EB' : '#D97706'}` }}>
                  <div className="flex justify-between">
                    <div>
                      <strong>{nc.clause}</strong> — {nc.title}
                      <span className="badge ml-2" style={{
                        background: nc.severity === 'major_nc' || nc.severity === 'Major' ? '#FEE2E2' : nc.severity === 'ofi' || nc.severity === 'OFI' ? '#DBEAFE' : '#FEF3C7',
                        color: nc.severity === 'major_nc' || nc.severity === 'Major' ? '#991B1B' : nc.severity === 'ofi' || nc.severity === 'OFI' ? '#1E40AF' : '#92400E',
                      }}>{nc.severity}</span>
                    </div>
                    <span className="text-xs" style={{ color: 'var(--gray-500)' }}>{nc.standard}</span>
                  </div>
                  {nc.description && <p className="mt-2 text-sm m-0">{nc.description}</p>}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'evidence' && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="m-0">Evidence Register ({program.evidence_count || 0})</h3>
            <button className="btn btn-primary" onClick={() => setShowAddEvidence(true)}>+ Add Evidence</button>
          </div>
          {showAddEvidence && (
            <div className="card mb-3">
              <h4 className="m-0 mb-3">Record Evidence</h4>
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="form-label">Clause Ref</label>
                  <input className="form-input" value={evForm.clause_ref}
                    onChange={e => setEvForm({ ...evForm, clause_ref: e.target.value })} placeholder="e.g. 4.1, A.5.1" />
                </div>
                <div>
                  <label className="form-label">Standard</label>
                  <input className="form-input" value={evForm.standard}
                    onChange={e => setEvForm({ ...evForm, standard: e.target.value })} placeholder="e.g. iso_27001" />
                </div>
                <div>
                  <label className="form-label">Type</label>
                  <select className="form-input" value={evForm.evidence_type}
                    onChange={e => setEvForm({ ...evForm, evidence_type: e.target.value })}>
                    {EVIDENCE_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                  </select>
                </div>
              </div>
              <div className="mt-2">
                <label className="form-label">Description *</label>
                <input className="form-input" value={evForm.description}
                  onChange={e => setEvForm({ ...evForm, description: e.target.value })} placeholder="What evidence was collected..." />
                <input type="file" className="form-input mt-1" style={{ padding: 6 }}
                  onChange={e => setEvForm({ ...evForm, file: e.target.files[0] || null })} />
              </div>
              <div className="mt-2">
                <label className="form-label">Collected By *</label>
                <input className="form-input" value={evForm.collected_by}
                  onChange={e => setEvForm({ ...evForm, collected_by: e.target.value })} placeholder="Auditor name" />
              </div>
              <div className="flex gap-2 mt-3">
                <button className="btn btn-primary" onClick={addEvidence}>Record</button>
                <button className="btn btn-secondary" onClick={() => setShowAddEvidence(false)}>Cancel</button>
              </div>
            </div>
          )}
          <EvidenceTable API={API} programId={program.program.id} />
        </div>
      )}

      {activeTab === 'summary' && (
        <div>
          <h3 className="m-0 mb-3">Audit Summary</h3>
          <div className="grid grid-cols-2 gap-3">
            <div className="card">
              <h4 className="m-0 mb-2">Program Info</h4>
              <table className="table">
                <tbody>
                  {[
                    ['Title', program.program.title],
                    ['Client', program.program.client_name],
                    ['Type', program.program.audit_type],
                    ['Standards', program.program.standards.join(', ')],
                    ['Dates', `${program.program.start_date} → ${program.program.end_date}`],
                    ['Lead Auditor', program.program.lead_auditor || '—'],
                    ['Location', program.program.location || '—'],
                  ].map(([k, v]) => (
                    <tr key={k}><td><strong>{k}</strong></td><td>{v}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="card">
              <h4 className="m-0 mb-2">Checklist Summary</h4>
              <table className="table">
                <tbody>
                  <tr><td><strong>Total Clauses</strong></td><td>{stats.total || 0}</td></tr>
                  <tr><td><strong>Reviewed</strong></td><td>{stats.reviewed || 0}</td></tr>
                  <tr><td><strong>Conforming</strong></td><td style={{ color: '#065F46' }}>{stats.conforming || 0}</td></tr>
                  <tr><td><strong>Minor NC</strong></td><td style={{ color: '#D97706' }}>{stats.minor_nc || 0}</td></tr>
                  <tr><td><strong>Major NC</strong></td><td style={{ color: '#DC2626' }}>{stats.major_nc || 0}</td></tr>
                  <tr><td><strong>OFI</strong></td><td style={{ color: '#2563EB' }}>{stats.ofi || 0}</td></tr>
                  <tr><td><strong>N/A</strong></td><td>{stats.na || 0}</td></tr>
                  <tr style={{ borderTop: '2px solid var(--gray-300)' }}><td><strong>Completion</strong></td><td><strong>{stats.completion_pct || 0}%</strong></td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ─── Checklist Table ───
function ChecklistTable({ API, programId, refresh }) {
  const [items, setItems] = useState([])
  const [filterStd, setFilterStd] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [expandedId, setExpandedId] = useState(null)

  useEffect(() => {
    const params = new URLSearchParams()
    if (filterStd) params.set('standard', filterStd)
    if (filterStatus) params.set('status', filterStatus)
    fetch(`${API}/audit_programs/${programId}/checklist?${params}`)
      .then(r => r.json()).then(d => setItems(d.checklist || []))
  }, [API, programId, filterStatus, filterStd])

  const standards = [...new Set(items.map(i => i.standard))]

  return (
    <div>
      <div className="flex gap-2 mb-2">
        <select className="form-input w-auto" value={filterStd} onChange={e => setFilterStd(e.target.value)}>
          <option value="">All Standards</option>
          {standards.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <select className="form-input w-auto" value={filterStatus} onChange={e => setFilterStatus(e.target.value)}>
          <option value="">All Statuses</option>
          {Object.entries(STATUS).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
        </select>
        <span className="text-xs self-center" style={{ color: 'var(--gray-500)' }}>{items.length} items</span>
      </div>

      {items.length === 0 ? (
        <div className="card text-center p-8" style={{ color: 'var(--gray-500)' }}>
          No checklist items. Click "Build Checklist" to generate from standards.
        </div>
      ) : (
        <div className="grid gap-1.5">
          {items.map(item => {
            const st = STATUS[item.status] || STATUS.pending
            const isExpanded = expandedId === item.id
            const suggestions = item.evidence_suggestions || []

            return (
              <div key={item.id} className="card" style={{
                padding: isExpanded ? 16 : 8,
                borderLeft: `4px solid ${st.fg}`,
                background: isExpanded ? '#FAFBFC' : 'white',
                transition: 'all 0.15s',
              }}>
                <div className="flex items-center gap-2 cursor-pointer"
                  onClick={() => setExpandedId(isExpanded ? null : item.id)}>
                  <span className="text-base select-none" style={{ color: 'var(--gray-400)' }}>
                    {isExpanded ? '▼' : '▶'}
                  </span>
                  <span className="font-semibold whitespace-nowrap min-w-[80px]">{item.clause_ref}</span>
                  <span className="text-sm flex-1 truncate">{item.clause_title}</span>
                  <span className="badge" style={{ background: '#E0E7FF', color: '#3730A3', fontSize: 10 }}>{item.standard}</span>
                  <span className="badge" style={{ background: st.bg, color: st.fg }}>{st.label}</span>
                  {item.evidence_found && <span className="text-xs" style={{ color: '#059669' }}>📎 Evidence recorded</span>}
                </div>

                {isExpanded && (
                  <div className="mt-3 pl-6">
                    {suggestions.length > 0 && (
                      <div className="mb-2.5">
                        <div className="text-xs font-semibold uppercase tracking-wide mb-1" style={{ color: '#6B7280' }}>Evidence to Review</div>
                        <div className="flex flex-col gap-1">
                          {suggestions.map((ev, idx) => (
                            <div key={idx} className="text-xs px-2 py-1 rounded" style={{ background: '#F0F9FF', border: '1px solid #BAE6FD', color: '#075985' }}>
                              <span style={{ color: '#0369A1', fontWeight: 600, marginRight: 6 }}>e.g.</span>{ev}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="mb-2.5">
                      <div className="text-xs font-semibold uppercase tracking-wide mb-1" style={{ color: '#6B7280' }}>Evidence Found</div>
                      <textarea className="form-input text-sm" rows={3} placeholder="Type what you actually observed / found for this clause..."
                        value={item.evidence_found || ''} onClick={e => e.stopPropagation()}
                        onChange={e => setItems(items.map(i => i.id === item.id ? { ...i, evidence_found: e.target.value } : i))}
                        onBlur={e => {
                          if (e.target.value !== (item.evidence_found || '')) {
                            fetch(`${API}/checklist/${item.id}`, {
                              method: 'PUT', headers: { 'Content-Type': 'application/json' },
                              body: JSON.stringify({ evidence_found: e.target.value }),
                            }).then(() => refresh())
                          }
                        }} />
                    </div>

                    <div className="mb-2.5">
                      <div className="text-xs font-semibold uppercase tracking-wide mb-1" style={{ color: '#6B7280' }}>Auditor Notes</div>
                      <textarea className="form-input text-sm" rows={2} placeholder="General notes..."
                        value={item.auditor_notes || ''} onClick={e => e.stopPropagation()}
                        onChange={e => setItems(items.map(i => i.id === item.id ? { ...i, auditor_notes: e.target.value } : i))}
                        onBlur={e => {
                          if (e.target.value !== (item.auditor_notes || '')) {
                            fetch(`${API}/checklist/${item.id}`, {
                              method: 'PUT', headers: { 'Content-Type': 'application/json' },
                              body: JSON.stringify({ auditor_notes: e.target.value }),
                            }).then(() => refresh())
                          }
                        }} />
                    </div>

                    <div className="flex gap-1 flex-wrap">
                      {Object.entries(STATUS).map(([k, v]) => (
                        <button key={k}
                          className={`btn ${item.status === k ? 'btn-primary' : 'btn-secondary'}`}
                          style={{ fontSize: 11, padding: '3px 10px', background: item.status === k ? v.fg : undefined, color: item.status === k ? 'white' : undefined }}
                          onClick={e => {
                            e.stopPropagation()
                            const extra = { auditor_notes: item.auditor_notes || '', evidence_found: item.evidence_found || '' }
                            if (k === 'minor_nc' || k === 'major_nc') { extra.severity = k === 'major_nc' ? 'Major' : 'Minor'; extra.nc_description = item.nc_description || '' }
                            if (k === 'ofi') extra.ofi_description = item.ofi_description || ''
                            fetch(`${API}/checklist/${item.id}`, {
                              method: 'PUT', headers: { 'Content-Type': 'application/json' },
                              body: JSON.stringify({ status: k, ...extra }),
                            }).then(() => { refresh(); setExpandedId(null) })
                          }}>{v.label}</button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

// ─── Clause Editor ───
function ClauseEditor({ item, onSave, onCancel }) {
  const [status, setStatus] = useState(item.status || 'pending')
  const [notes, setNotes] = useState(item.auditor_notes || '')
  const [evidence, setEvidence] = useState(item.evidence_found || '')

  return (
    <div className="card mb-3 animate-slideIn">
      <div className="flex items-center justify-between mb-3">
        <h4 className="m-0">Edit: {item.clause_ref}</h4>
        <button className="btn btn-secondary text-xs px-2 py-1" onClick={onCancel}>✕</button>
      </div>
      <div className="flex gap-1 flex-wrap mb-3">
        {Object.entries(STATUS).map(([k, v]) => (
          <button key={k} className={`btn btn-small ${status === k ? 'btn-primary' : 'btn-secondary'}`}
            style={{ background: status === k ? v.fg : undefined, color: status === k ? 'white' : undefined }}
            onClick={() => setStatus(k)}>{v.label}</button>
        ))}
      </div>
      <div className="mb-3"><label className="form-label">Auditor Notes</label>
        <textarea className="form-input" rows={2} value={notes} onChange={e => setNotes(e.target.value)} /></div>
      <div className="mb-3"><label className="form-label">Evidence Found</label>
        <textarea className="form-input" rows={3} value={evidence} onChange={e => setEvidence(e.target.value)} /></div>
      <div className="flex gap-2">
        <button className="btn btn-primary" onClick={() => onSave(item.id, status, { auditor_notes: notes, evidence_found: evidence })}>Save</button>
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
      .then(r => r.json()).then(d => setItems(d.evidence || []))
  }, [API, programId])

  if (items.length === 0) {
    return <div className="card text-center p-8" style={{ color: 'var(--gray-500)' }}>No evidence recorded yet.</div>
  }

  return (
    <table className="table w-full">
      <thead><tr><th>Clause</th><th>Type</th><th>Description</th><th>Collected By</th><th>Status</th></tr></thead>
      <tbody>
        {items.map(ev => (
          <tr key={ev.id}>
            <td className="font-semibold">{ev.clause_ref}</td>
            <td className="capitalize">{ev.evidence_type}</td>
            <td className="text-sm">{ev.description}</td>
            <td>{ev.collected_by}</td>
            <td>
              <span className="badge capitalize" style={{
                background: ev.status === 'reviewed' ? '#D1FAE5' : ev.status === 'rejected' ? '#FEE2E2' : '#FEF3C7',
                color: ev.status === 'reviewed' ? '#065F46' : ev.status === 'rejected' ? '#991B1B' : '#92400E',
              }}>{ev.status}</span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
