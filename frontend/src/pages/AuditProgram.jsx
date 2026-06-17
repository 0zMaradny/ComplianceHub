import { useState, useEffect, useCallback } from 'react'
import { useTranslation } from 'react-i18next'

const STATUS = (t) => ({
  pending:    { bg: '#F3F4F6', fg: '#6B7280', label: t('audit_program.pending') },
  conforming: { bg: '#D1FAE5', fg: '#065F46', label: t('audit_program.conforming') },
  minor_nc:   { bg: '#FEF3C7', fg: '#92400E', label: t('audit_program.minor_nc') },
  major_nc:   { bg: '#FEE2E2', fg: '#991B1B', label: t('audit_program.major_nc') },
  ofi:        { bg: '#DBEAFE', fg: '#1E40AF', label: t('audit_program.ofi') },
  na:         { bg: '#E5E7EB', fg: '#374151', label: t('audit_program.na') },
})

const AUDIT_TYPES = (t) => [
  { value: 'stage1', label: t('audit_program.stage1') },
  { value: 'stage2', label: t('audit_program.stage2') },
  { value: 'surveillance', label: t('audit_program.surveillance') },
  { value: 'recertification', label: t('audit_program.recertification') },
  { value: 'transfer', label: t('audit_program.transfer') },
]

const EVIDENCE_TYPES = ['document', 'interview', 'observation', 'record']

export default function AuditProgram({ API }) {
  const { t } = useTranslation()
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
    if (!confirm(t('audit_program.delete_confirm'))) return
    await fetch(`${API}/audit_programs/${pid}`, { method: 'DELETE' })
    setSelected(null); loadPrograms()
  }

  if (selected) {
    return <ProgramDetail API={API} program={selected} onBack={() => { setSelected(null); loadPrograms() }} onDelete={handleDelete} />
  }

  return (
    <div className="animate-fadeIn">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2>{t('audit_program.title')}</h2>
          <p>{t('audit_program.subtitle')}</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreate(true)}>{t('audit_program.new')}</button>
      </div>

      {showCreate && (
        <div className="card mb-5">
          <div className="card-header">{t('audit_program.create_title')}</div>
          <div className="card-body">
            <div className="grid grid-cols-2 gap-3">
              {[
                { label: t('audit_program.program_title') + ' *', key: 'title', placeholder: t('audit_program.create_title_placeholder') },
                { label: t('audit_program.client_name'), key: 'client_name', placeholder: t('audit_program.client_placeholder') },
                { label: t('audit_program.client_key'), key: 'client_key', placeholder: t('audit_program.client_key_placeholder') },
                { label: t('audit_program.audit_type'), key: 'audit_type', type: 'select', options: AUDIT_TYPES(t) },
                { label: t('audit_program.lead_auditor'), key: 'lead_auditor', placeholder: t('audit_program.lead_auditor_placeholder') },
                { label: t('audit_program.audit_team'), key: 'audit_team', placeholder: t('audit_program.team_placeholder') },
                { label: t('audit_program.start_date'), key: 'start_date', type: 'date' },
                { label: t('audit_program.end_date'), key: 'end_date', type: 'date' },
                { label: t('audit_program.location'), key: 'location', placeholder: t('audit_program.location_placeholder') },
                { label: t('audit_program.standards'), key: 'standards', placeholder: t('audit_program.standards_placeholder') },
              ].map(f => (
                <div key={f.key}>
                  <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{f.label}</label>
                  {f.type === 'select' ? (
                    <select className="input" value={form[f.key]} onChange={e => setForm({ ...form, [f.key]: e.target.value })}>
                      {f.options.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
                    </select>
                  ) : f.type === 'date' ? (
                    <input type="date" className="input" value={form[f.key]}
                      onChange={e => setForm({ ...form, [f.key]: e.target.value })} />
                  ) : f.key === 'standards' ? (
                    <input className="input" value={form.standards.join(', ')}
                      onChange={e => setForm({ ...form, standards: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                      placeholder={f.placeholder} />
                  ) : (
                    <input className="input" value={form[f.key]}
                      onChange={e => setForm({ ...form, [f.key]: e.target.value })} placeholder={f.placeholder} />
                  )}
                </div>
              ))}
            </div>
            <div className="mt-3">
              <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('audit_program.notes')}</label>
              <textarea className="input" rows={2} value={form.notes}
                onChange={e => setForm({ ...form, notes: e.target.value })} placeholder={t('audit_program.notes_placeholder')} />
            </div>
            <div className="flex gap-2 mt-4">
              <button className="btn btn-primary" onClick={handleCreate}>{t('audit_program.create')}</button>
              <button className="btn btn-secondary" onClick={() => setShowCreate(false)}>{t('audit_program.cancel')}</button>
            </div>
          </div>
        </div>
      )}

      {programs.length === 0 ? (
        <div className="card mb-5 text-center p-10">
          <p className="text-[var(--gray-500)]">{t('audit_program.empty')}</p>
        </div>
      ) : (
        <div className="grid gap-3">
          {programs.map(p => (
            <div key={p.id} className="card mb-2 cursor-pointer p-4" onClick={() => openProgram(p)}>
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-semibold text-[var(--text-primary)] m-0 mb-1">{p.title}</h4>
                  <div className="text-sm text-[var(--gray-500)]">
                    {p.client_name} · {p.standards.join(', ')} · {p.audit_type}
                    {p.lead_auditor && ` · ${t('audit_program.lead_auditor')}: ${p.lead_auditor}`}
                  </div>
                  <div className="text-xs mt-1 text-[var(--gray-400)]">
                    {p.start_date} → {p.end_date} {p.location && `· ${p.location}`}
                  </div>
                </div>
                <span className={`badge capitalize ${p.status === 'active' ? 'badge-success' : p.status === 'completed' ? 'badge-info' : 'badge-warning'}`}>{p.status}</span>
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
  const { t } = useTranslation()
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
    { id: 'checklist', label: t('audit_program.tab_checklist') },
    { id: 'findings', label: t('audit_program.tab_findings') },
    { id: 'evidence', label: t('audit_program.tab_evidence') },
    { id: 'summary', label: t('audit_program.tab_summary') },
  ]

  return (
    <div className="animate-fadeIn">
      <div className="mb-4">
        <button className="btn btn-ghost mb-2" onClick={onBack}>{t('audit_program.back')}</button>
        <div className="flex justify-between items-start">
          <div>
            <h2 className="m-0 mb-1">{program.program.title}</h2>
            <div className="text-sm text-[var(--gray-500)]">
              {program.program.client_name} · {program.program.standards.join(', ')} · {program.program.audit_type}
            </div>
            <div className="text-xs mt-0.5 text-[var(--gray-400)]">
              {program.program.start_date} → {program.program.end_date}
              {program.program.location && ` · ${program.program.location}`}
              {program.program.lead_auditor && ` · ${t('audit_program.lead_auditor')}: ${program.program.lead_auditor}`}
            </div>
          </div>
          <button className="btn btn-danger" onClick={() => onDelete(program.program.id)}>{t('audit_program.delete')}</button>
        </div>
      </div>

      <div className="grid grid-cols-6 gap-2 mb-4">
        {[
          { label: t('audit_program.total_clauses'), value: stats.total || 0, color: '#6B7280' },
          { label: t('audit_program.reviewed'), value: stats.reviewed || 0, color: '#059669' },
          { label: t('audit_program.conforming'), value: stats.conforming || 0, color: '#065F46' },
          { label: t('audit_program.minor_nc'), value: stats.minor_nc || 0, color: '#D97706' },
          { label: t('audit_program.major_nc'), value: stats.major_nc || 0, color: '#DC2626' },
          { label: t('audit_program.ofi'), value: stats.ofi || 0, color: '#2563EB' },
        ].map(s => (
          <div key={s.label} className="stat-card text-center p-2">
            <div className="stat-card-value" style={{ color: s.color }}>{s.value}</div>
            <div className="stat-card-label">{s.label}</div>
          </div>
        ))}
      </div>

      <div className="mb-4">
        <div className="flex justify-between text-xs mb-1">
          <span>{t('audit_program.audit_progress')}</span>
          <span className="font-semibold">{stats.completion_pct || 0}%</span>
        </div>
        <div className="progress-bar">
          <div className="progress-bar-fill" style={{
            width: `${stats.completion_pct || 0}%`,
            background: (stats.completion_pct || 0) > 75 ? '#059669' : (stats.completion_pct || 0) > 40 ? '#D97706' : '#DC2626',
          }} />
        </div>
      </div>

      <div className="flex gap-1 mb-4 border-b border-[var(--gray-200)] pb-0">
        {tabs.map(tab => (
          <button key={tab.id} className={`btn ${activeTab === tab.id ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab(tab.id)}
            style={{ borderRadius: '6px 6px 0 0' }}>{tab.label}</button>
        ))}
      </div>

      {activeTab === 'checklist' && (
        <div className="card mb-5">
          <div className="card-header flex items-center justify-between">
            <h3 className="m-0">{t('audit_program.clause_checklist')}</h3>
            <button className="btn btn-secondary" onClick={async () => {
              await fetch(`${API}/audit_programs/${program.program.id}/checklist/build`, { method: 'POST' })
              refresh()
            }}>{t('audit_program.build_checklist')}</button>
          </div>
          <div className="card-body">
            <div className="flex gap-1 mb-3">
              {program.program.standards.map(std => (
                <span key={std} className="badge badge-info" style={{ background: '#DBEAFE', color: '#1E40AF' }}>{std}</span>
              ))}
            </div>
            {editingCl && <ClauseEditor item={editingCl} onSave={updateClStatus} onCancel={() => setEditingCl(null)} />}
            <ChecklistTable API={API} programId={program.program.id} onEdit={setEditingCl} refresh={refresh} />
          </div>
        </div>
      )}

      {activeTab === 'findings' && (
        <div className="card mb-5">
          <div className="card-header">
            <h3 className="m-0">{t('audit_program.findings_register')}</h3>
          </div>
          <div className="card-body">
            {(!program.ncs || program.ncs.length === 0) ? (
              <div className="text-center p-8 text-[var(--gray-500)]">
                {t('audit_program.no_findings')}
              </div>
            ) : (
              <div className="grid gap-2">
                {program.ncs.map((nc, i) => (
                  <div key={i} className="card mb-2" style={{ borderLeft: `4px solid ${nc.severity === 'major_nc' || nc.severity === 'Major' ? '#DC2626' : nc.severity === 'ofi' || nc.severity === 'OFI' ? '#2563EB' : '#D97706'}` }}>
                    <div className="flex justify-between p-4">
                      <div>
                        <strong>{nc.clause}</strong> — {nc.title}
                        <span className={`badge ml-2 ${nc.severity === 'major_nc' || nc.severity === 'Major' ? 'badge-error' : nc.severity === 'ofi' || nc.severity === 'OFI' ? 'badge-info' : 'badge-warning'}`}>{nc.severity}</span>
                      </div>
                      <span className="text-xs text-[var(--gray-500)]">{nc.standard}</span>
                    </div>
                    {nc.description && <p className="mt-2 text-sm m-0 px-4 pb-4">{nc.description}</p>}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'evidence' && (
        <div className="card mb-5">
          <div className="card-header flex items-center justify-between">
            <h3 className="m-0">{t('audit_program.evidence_register')} ({program.evidence_count || 0})</h3>
            <button className="btn btn-primary" onClick={() => setShowAddEvidence(true)}>{t('audit_program.add_evidence')}</button>
          </div>
          <div className="card-body">
            {showAddEvidence && (
              <div className="card mb-3">
                <div className="card-header">{t('audit_program.record_evidence')}</div>
                <div className="card-body">
                  <div className="grid grid-cols-3 gap-2">
                    <div>
                      <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('audit_program.clause_ref')}</label>
                      <input className="input" value={evForm.clause_ref}
                        onChange={e => setEvForm({ ...evForm, clause_ref: e.target.value })} placeholder={t('audit_program.clause_ref_placeholder')} />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('audit_program.standard')}</label>
                      <input className="input" value={evForm.standard}
                        onChange={e => setEvForm({ ...evForm, standard: e.target.value })} placeholder={t('audit_program.standard_placeholder')} />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('audit_program.type')}</label>
                      <select className="input" value={evForm.evidence_type}
                        onChange={e => setEvForm({ ...evForm, evidence_type: e.target.value })}>
                        {EVIDENCE_TYPES.map(et => <option key={et} value={et}>{t('audit_program.type_' + et)}</option>)}
                      </select>
                    </div>
                  </div>
                  <div className="mt-2">
                    <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('audit_program.description')}</label>
                    <input className="input" value={evForm.description}
                      onChange={e => setEvForm({ ...evForm, description: e.target.value })} placeholder={t('audit_program.description_placeholder')} />
                    <input type="file" className="input mt-1 p-[6px]"
                      onChange={e => setEvForm({ ...evForm, file: e.target.files[0] || null })} />
                  </div>
                  <div className="mt-2">
                    <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('audit_program.collected_by')}</label>
                    <input className="input" value={evForm.collected_by}
                      onChange={e => setEvForm({ ...evForm, collected_by: e.target.value })} placeholder={t('audit_program.collected_placeholder')} />
                  </div>
                  <div className="flex gap-2 mt-3">
                    <button className="btn btn-primary" onClick={addEvidence}>{t('audit_program.record_btn')}</button>
                    <button className="btn btn-secondary" onClick={() => setShowAddEvidence(false)}>{t('audit_program.cancel_btn')}</button>
                  </div>
                </div>
              </div>
            )}
            <EvidenceTable API={API} programId={program.program.id} />
          </div>
        </div>
      )}

      {activeTab === 'summary' && (
        <div className="card mb-5">
          <div className="card-header">
            <h3 className="m-0">{t('audit_program.audit_summary')}</h3>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-2 gap-3">
              <div className="card">
                <div className="card-header">{t('audit_program.program_info')}</div>
                <div className="card-body p-0">
                  <table className="w-full text-xs border-collapse">
                    <tbody>
                      {[
                        [t('audit_program.program_title'), program.program.title],
                        [t('audit_program.client'), program.program.client_name],
                        [t('audit_program.type_label'), program.program.audit_type],
                        [t('audit_program.standards_label'), program.program.standards.join(', ')],
                        [t('audit_program.dates'), `${program.program.start_date} → ${program.program.end_date}`],
                        [t('audit_program.lead_auditor'), program.program.lead_auditor || '—'],
                        [t('audit_program.location_label'), program.program.location || '—'],
                      ].map(([k, v]) => (
                        <tr key={k}><td className="px-4 py-2.5 border-b border-[var(--border-color)]"><strong>{k}</strong></td><td className="px-4 py-2.5 border-b border-[var(--border-color)]">{v}</td></tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
              <div className="card">
                <div className="card-header">{t('audit_program.checklist_summary')}</div>
                <div className="card-body p-0">
                  <table className="w-full text-xs border-collapse">
                    <tbody>
                      <tr><td className="px-4 py-2.5 border-b border-[var(--border-color)]"><strong>{t('audit_program.total_clauses')}</strong></td><td className="px-4 py-2.5 border-b border-[var(--border-color)]">{stats.total || 0}</td></tr>
                      <tr><td className="px-4 py-2.5 border-b border-[var(--border-color)]"><strong>{t('audit_program.reviewed')}</strong></td><td className="px-4 py-2.5 border-b border-[var(--border-color)]">{stats.reviewed || 0}</td></tr>
                      <tr><td className="px-4 py-2.5 border-b border-[var(--border-color)]"><strong>{t('audit_program.conforming')}</strong></td><td className="px-4 py-2.5 border-b border-[var(--border-color)] text-emerald-800">{stats.conforming || 0}</td></tr>
                      <tr><td className="px-4 py-2.5 border-b border-[var(--border-color)]"><strong>{t('audit_program.minor_nc')}</strong></td><td className="px-4 py-2.5 border-b border-[var(--border-color)] text-amber-600">{stats.minor_nc || 0}</td></tr>
                      <tr><td className="px-4 py-2.5 border-b border-[var(--border-color)]"><strong>{t('audit_program.major_nc')}</strong></td><td className="px-4 py-2.5 border-b border-[var(--border-color)] text-red-600">{stats.major_nc || 0}</td></tr>
                      <tr><td className="px-4 py-2.5 border-b border-[var(--border-color)]"><strong>{t('audit_program.ofi')}</strong></td><td className="px-4 py-2.5 border-b border-[var(--border-color)] text-blue-600">{stats.ofi || 0}</td></tr>
                      <tr><td className="px-4 py-2.5 border-b border-[var(--border-color)]"><strong>{t('audit_program.na')}</strong></td><td className="px-4 py-2.5 border-b border-[var(--border-color)]">{stats.na || 0}</td></tr>
                      <tr className="border-t-2 border-[var(--gray-300)]"><td className="px-4 py-2.5 border-b border-[var(--border-color)]"><strong>{t('audit_program.completion')}</strong></td><td className="px-4 py-2.5 border-b border-[var(--border-color)]"><strong>{stats.completion_pct || 0}%</strong></td></tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ─── Checklist Table ───
function ChecklistTable({ API, programId, refresh }) {
  const { t } = useTranslation()
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
  const statusMap = STATUS(t)

  return (
    <div>
      <div className="flex gap-2 mb-2">
        <select className="input w-auto" value={filterStd} onChange={e => setFilterStd(e.target.value)}>
          <option value="">{t('audit_program.all_standards')}</option>
          {standards.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <select className="input w-auto" value={filterStatus} onChange={e => setFilterStatus(e.target.value)}>
          <option value="">{t('audit_program.all_statuses')}</option>
          {Object.entries(STATUS(t)).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
        </select>
        <span className="text-xs self-center text-[var(--gray-500)]">{items.length} {t('audit_program.items_count')}</span>
      </div>

      {items.length === 0 ? (
        <div className="text-center p-8 text-[var(--gray-500)]">
          {t('audit_program.no_checklist_items')}
        </div>
      ) : (
        <div className="grid gap-1.5">
          {items.map(item => {
            const st = statusMap[item.status] || statusMap.pending
            const isExpanded = expandedId === item.id
            const suggestions = item.evidence_suggestions || []

            return (
              <div key={item.id} className="card mb-2" style={{
                padding: isExpanded ? 16 : 8,
                borderLeft: `4px solid ${st.fg}`,
                background: isExpanded ? '#FAFBFC' : undefined,
                transition: 'all 0.15s',
              }}>
                <div className="flex items-center gap-2 cursor-pointer"
                  onClick={() => setExpandedId(isExpanded ? null : item.id)}>
                  <span className="text-base select-none text-[var(--gray-400)]">
                    {isExpanded ? '▼' : '▶'}
                  </span>
                  <span className="font-semibold whitespace-nowrap min-w-[80px]">{item.clause_ref}</span>
                  <span className="text-sm flex-1 truncate">{item.clause_title}</span>
                  <span className="badge badge-info" style={{ background: '#E0E7FF', color: '#3730A3', fontSize: 10 }}>{item.standard}</span>
                  <span className="badge" style={{ background: st.bg, color: st.fg }}>{st.label}</span>
                  {item.evidence_found && <span className="text-xs text-emerald-600">{t('audit_program.evidence_tag')}</span>}
                </div>

                {isExpanded && (
                  <div className="mt-3 pl-6">
                    {suggestions.length > 0 && (
                      <div className="mb-2.5">
                        <div className="text-xs font-semibold uppercase tracking-wide mb-1 text-[var(--text-secondary)]">{t('audit_program.evidence_to_review')}</div>
                        <div className="flex flex-col gap-1">
                          {suggestions.map((ev, idx) => (
                            <div key={idx} className="text-xs px-2 py-1 rounded bg-sky-50 border border-sky-200 text-sky-800">
                              <span className="text-sky-700 font-semibold mr-1.5">{t('audit_program.eg')}</span>{ev}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="mb-2.5">
                      <div className="text-xs font-semibold uppercase tracking-wide mb-1 text-[var(--text-secondary)]">{t('audit_program.evidence_found')}</div>
                      <textarea className="input" rows={3} placeholder={t('audit_program.evidence_placeholder')}
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
                      <div className="text-xs font-semibold uppercase tracking-wide mb-1 text-[var(--text-secondary)]">{t('audit_program.auditor_notes')}</div>
                      <textarea className="input" rows={2} placeholder={t('audit_program.notes_placeholder')}
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
                      {Object.entries(statusMap).map(([k, v]) => (
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
  const { t } = useTranslation()
  const [status, setStatus] = useState(item.status || 'pending')
  const [notes, setNotes] = useState(item.auditor_notes || '')
  const [evidence, setEvidence] = useState(item.evidence_found || '')

  return (
    <div className="card mb-5 animate-slideIn">
      <div className="card-header flex items-center justify-between">
        <h4 className="text-sm font-semibold m-0">{t('audit_program.edit_header')} {item.clause_ref}</h4>
        <button className="btn btn-ghost text-xs px-2 py-1" onClick={onCancel}>✕</button>
      </div>
      <div className="card-body">
        <div className="flex gap-1 flex-wrap mb-3">
          {Object.entries(STATUS(t)).map(([k, v]) => (
            <button key={k} className={`btn ${status === k ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: 11, padding: '3px 10px', background: status === k ? v.fg : undefined, color: status === k ? 'white' : undefined }}
              onClick={() => setStatus(k)}>{v.label}</button>
          ))}
        </div>
        <div className="mb-3"><label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('audit_program.auditor_notes')}</label>
          <textarea className="input" rows={2} value={notes} onChange={e => setNotes(e.target.value)} /></div>
        <div className="mb-3"><label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('audit_program.evidence_found')}</label>
          <textarea className="input" rows={3} value={evidence} onChange={e => setEvidence(e.target.value)} /></div>
        <div className="flex gap-2">
          <button className="btn btn-primary" onClick={() => onSave(item.id, status, { auditor_notes: notes, evidence_found: evidence })}>{t('audit_program.save')}</button>
          <button className="btn btn-secondary" onClick={onCancel}>{t('audit_program.cancel')}</button>
        </div>
      </div>
    </div>
  )
}

// ─── Evidence Table ───
function EvidenceTable({ API, programId }) {
  const { t } = useTranslation()
  const [items, setItems] = useState([])
  useEffect(() => {
    fetch(`${API}/audit_programs/${programId}/evidence`)
      .then(r => r.json()).then(d => setItems(d.evidence || []))
  }, [API, programId])

  if (items.length === 0) {
    return <div className="text-center p-8 text-[var(--gray-500)]">{t('audit_program.no_evidence')}</div>
  }

  return (
    <div className="table-container">
      <table className="w-full text-xs border-collapse">
        <thead><tr><th className="text-left px-4 py-2.5 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)]">{t('audit_program.clause')}</th><th className="text-left px-4 py-2.5 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)]">{t('audit_program.type')}</th><th className="text-left px-4 py-2.5 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)]">{t('audit_program.description')}</th><th className="text-left px-4 py-2.5 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)]">{t('audit_program.collected_by')}</th><th className="text-left px-4 py-2.5 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)]">{t('audit_program.status')}</th></tr></thead>
        <tbody>
          {items.map(ev => (
            <tr key={ev.id}>
              <td className="px-4 py-2.5 border-b border-[var(--border-color)] font-semibold">{ev.clause_ref}</td>
              <td className="px-4 py-2.5 border-b border-[var(--border-color)] capitalize">{ev.evidence_type}</td>
              <td className="px-4 py-2.5 border-b border-[var(--border-color)] text-sm">{ev.description}</td>
              <td className="px-4 py-2.5 border-b border-[var(--border-color)]">{ev.collected_by}</td>
              <td className="px-4 py-2.5 border-b border-[var(--border-color)]">
                <span className={`badge capitalize ${ev.status === 'reviewed' ? 'badge-success' : ev.status === 'rejected' ? 'badge-error' : 'badge-warning'}`}>{ev.status}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
