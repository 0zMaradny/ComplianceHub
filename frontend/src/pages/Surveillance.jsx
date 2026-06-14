import { useState, useEffect, useCallback } from 'react'
import { useTranslation } from 'react-i18next'

const TUV_RED = '#C00000'

const STATUS_COLORS = {
  scheduled: '#3498DB', in_progress: '#F39C12', completed: '#27AE60', overdue: TUV_RED,
}

const CYCLE_LABELS = {
  1: 'surveillance.y1', 2: 'surveillance.y2', 3: 'surveillance.y3',
}

const FINDING_TYPE_COLORS = {
  recurring_nc: TUV_RED, new_nc: '#E67E22', ofi: '#3498DB', observation: '#95A5A6',
}

export default function Surveillance({ API }) {
  const { t } = useTranslation()
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

  const loadData = useCallback(() => {
    Promise.all([
      fetch(`${API}/surveillance/cycles`).then(r => r.json()).catch(() => ({ cycles: [] })),
      fetch(`${API}/projects`).then(r => r.json()).catch(() => ({ projects: [] })),
      fetch(`${API}/surveillance/dashboard`).then(r => r.json()).catch(() => ({})),
    ]).then(([c, p, s]) => { setCycles(c.cycles || []); setProjects(p.projects || []); setStats(s) })
  }, [API])

  useEffect(() => { loadData() }, [API, loadData])

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
        <button className="btn btn-ghost mb-4" onClick={() => { setSelectedCycle(null); setScope(null) }}>
          {t('surveillance.back')}
        </button>

        <div className="card mb-5">
          <div className="card-body">
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">{t('surveillance.cycle_prefix')}{selectedCycle.cycle_number}: {t(CYCLE_LABELS[selectedCycle.cycle_number])}</h2>
                <div className="text-sm text-[var(--text-secondary)]">
                  {project?.title || selectedCycle.project_id} · Scheduled: {selectedCycle.scheduled_date}
                </div>
              </div>
              <span className={`badge badge-${selectedCycle.status === 'in_progress' ? 'warning' : selectedCycle.status === 'completed' ? 'success' : selectedCycle.status === 'overdue' ? 'error' : 'info'}`}>
                {selectedCycle.status}
              </span>
            </div>
          </div>
        </div>

        <div className="flex gap-2 mb-4 flex-wrap">
          <button className="btn btn-secondary" onClick={() => loadScope(selectedCycle.id)}>{t('surveillance.generate_scope')}</button>
          <button className="btn btn-secondary" onClick={() => setShowAddFinding(!showAddFinding)}>{t('surveillance.add_finding')}</button>
          {selectedCycle.status === 'scheduled' && (
            <button className="btn btn-primary" onClick={() => handleUpdateStatus(selectedCycle.id, 'in_progress')}>{t('surveillance.start_audit')}</button>
          )}
          {selectedCycle.status === 'in_progress' && (
            <button className="btn btn-primary" onClick={() => handleUpdateStatus(selectedCycle.id, 'completed')}>{t('surveillance.complete')}</button>
          )}
        </div>

        {scope && (
          <div className="card mb-5">
            <div className="card-header">{t('surveillance.reduced_scope')}</div>
            <div className="card-body">
              <p className="text-sm text-[var(--text-secondary)]">{scope.rationale}</p>
              <div className="grid grid-cols-2 gap-3 mt-2">
                <div>
                  <h4 className="text-xs" style={{ color: '#27AE60' }}>{t('surveillance.included_clauses')} ({scope.included_clauses?.length || 0})</h4>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {(scope.included_clauses || []).map(c => (
                      <span key={c} className="text-xs px-1.5 py-0.5 rounded" style={{ background: '#E8F8F0' }}>{c}</span>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="text-xs" style={{ color: TUV_RED }}>{t('surveillance.excluded_clauses')} ({scope.excluded_clauses?.length || 0})</h4>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {(scope.excluded_clauses || []).map(c => (
                      <span key={c} className="text-xs px-1.5 py-0.5 rounded" style={{ background: '#FEF2F2' }}>{c}</span>
                    ))}
                  </div>
                </div>
              </div>
              {scope.manday_reduction_pct > 0 && (
                <div className="mt-2 text-xs text-[var(--text-secondary)]">{t('surveillance.manday_reduction')}{scope.manday_reduction_pct}%</div>
              )}
            </div>
          </div>
        )}

        {showAddFinding && (
          <div className="card mb-5">
            <div className="card-header">{t('surveillance.add_finding_title')}</div>
            <div className="card-body">
              <div className="grid grid-cols-2 gap-3">
                {[
                  { label: t('surveillance.clause'), key: 'clause', type: 'text', placeholder: t('surveillance.clause_placeholder') },
                  { label: t('surveillance.finding_type'), key: 'finding_type', type: 'select', options: [
                    { value: 'new_nc', label: t('surveillance.finding_nc') }, { value: 'recurring_nc', label: t('surveillance.finding_recurring') },
                    { value: 'ofi', label: t('surveillance.finding_ofi') }, { value: 'observation', label: t('surveillance.finding_obs') },
                  ]},
                  { label: t('surveillance.severity'), key: 'severity', type: 'select', options: [
                    { value: 'Major', label: t('surveillance.severity_major') }, { value: 'Minor', label: t('surveillance.severity_minor') }, { value: 'OFI', label: t('surveillance.severity_ofi') },
                  ]},
                  { label: t('surveillance.prev_nc_id'), key: 'previous_nc_id', type: 'text', placeholder: t('surveillance.prev_nc_placeholder') },
                ].map(f => (
                  <div key={f.key} className="mb-5">
                    <label>{f.label}</label>
                    {f.type === 'select' ? (
                      <select value={findingForm[f.key]} onChange={e => setFindingForm({ ...findingForm, [f.key]: e.target.value })}
                        className="input">
                        {f.options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                      </select>
                    ) : (
                      <input type="text" value={findingForm[f.key]} placeholder={f.placeholder}
                        onChange={e => setFindingForm({ ...findingForm, [f.key]: e.target.value })}
                        className="input" />
                    )}
                  </div>
                ))}
              </div>
              <div className="mb-5 mt-2">
                <label>{t('surveillance.description')}</label>
                <textarea value={findingForm.description} rows={3} placeholder={t('surveillance.desc_placeholder')}
                  onChange={e => setFindingForm({ ...findingForm, description: e.target.value })}
                  className="input" style={{ resize: 'vertical' }} />
              </div>
              <div className="flex gap-2 mt-2">
                <button className="btn btn-primary" onClick={handleAddFinding}>{t('surveillance.add_btn')}</button>
                <button className="btn btn-secondary" onClick={() => setShowAddFinding(false)}>{t('surveillance.cancel_btn')}</button>
              </div>
            </div>
          </div>
        )}

        <div className="card mb-5">
          <div className="card-header">{t('surveillance.findings')} ({findings.length})</div>
          <div className="card-body">
            {findings.length === 0 ? (
              <div className="text-center p-12 text-[var(--text-secondary)]">{t('surveillance.no_findings')}</div>
            ) : (
              <div className="flex flex-col gap-2 mt-2">
                {findings.map(f => (
                  <div key={f.id} className="p-2.5 rounded-md" style={{ border: '1px solid var(--border-color)', borderLeft: `4px solid ${FINDING_TYPE_COLORS[f.finding_type] || '#999'}` }}>
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-sm">{f.clause}</span>
                      <div className="flex gap-1.5">
                        <span className={`badge badge-${f.finding_type === 'recurring_nc' ? 'error' : f.finding_type === 'new_nc' ? 'warning' : 'info'}`}>
                          {f.finding_type.replace('_', ' ')}</span>
                        <span className={`badge badge-${f.severity === 'Major' ? 'error' : f.severity === 'Minor' ? 'warning' : 'info'}`}>
                          {f.severity}</span>
                      </div>
                    </div>
                    <p className="text-xs mt-1 m-0 text-[var(--text-secondary)]">{f.description}</p>
                    {f.previous_nc_id && <div className="text-xs mt-1" style={{ color: TUV_RED }}>{t('surveillance.recurring_from')}{f.previous_nc_id}</div>}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  // List View
  return (
    <div className="animate-pageIn">
      <div className="page-header">
        <h2>{t('surveillance.title')}</h2>
        <p>{t('surveillance.subtitle')}</p>
      </div>

      {stats && (
        <div className="grid gap-5 mb-8 grid-cols-[repeat(auto-fit,minmax(220px,1fr))]">
          <div className="stat-card"><div className="stat-card-value" style={{ color: 'var(--primary)' }}>{stats.total_cycles ?? 0}</div><div className="stat-card-label">{t('surveillance.total_cycles')}</div></div>
          <div className="stat-card"><div className="stat-card-value" style={{ color: '#3498DB' }}>{stats.upcoming_30d ?? 0}</div><div className="stat-card-label">{t('surveillance.upcoming')}</div></div>
          <div className="stat-card"><div className="stat-card-value" style={{ color: TUV_RED }}>{stats.overdue ?? 0}</div><div className="stat-card-label">{t('surveillance.overdue')}</div></div>
          <div className="stat-card"><div className="stat-card-value" style={{ color: '#27AE60' }}>{stats.completed ?? 0}</div><div className="stat-card-label">{t('surveillance.completed')}</div></div>
        </div>
      )}

      <div className="flex gap-2 mb-4 flex-wrap items-center">
        <button className="btn btn-primary" onClick={() => setShowCreate(!showCreate)}>
          {showCreate ? t('surveillance.cancel') : t('surveillance.new_cycle')}
        </button>
        <button className="btn btn-secondary" onClick={async () => { await fetch(`${API}/surveillance/check-overdue`, { method: 'POST' }); loadData() }}>
          {t('surveillance.check_overdue')}
        </button>
      </div>

      <div className="card mb-5">
        <div className="card-header">{t('surveillance.auto_schedule')}</div>
        <div className="card-body">
          <p className="text-xs text-[var(--text-secondary)]">{t('surveillance.auto_desc')}</p>
          <div className="flex gap-2 mt-2 flex-wrap">
            <select value={autoScheduleProj} onChange={e => setAutoScheduleProj(e.target.value)}
              className="input" style={{ width: 'auto', minWidth: 180 }}>
              <option value="">{t('surveillance.select_project')}</option>
              {projects.map(p => <option key={p.id} value={p.id}>{p.title}</option>)}
            </select>
            <input type="date" value={autoScheduleDate} onChange={e => setAutoScheduleDate(e.target.value)}
              className="input" style={{ width: 'auto' }} />
            <button className="btn btn-primary" onClick={handleAutoSchedule} disabled={!autoScheduleProj || !autoScheduleDate}>{t('surveillance.auto_btn')}</button>
          </div>
        </div>
      </div>

      {showCreate && (
        <div className="card mb-5">
          <div className="card-header">{t('surveillance.create_title')}</div>
          <div className="card-body">
            <div className="grid grid-cols-2 gap-3">
              <div className="mb-5">
                <label>{t('surveillance.project')}</label>
                <select value={form.project_id} onChange={e => setForm({ ...form, project_id: e.target.value })}
                  className="input">
                  <option value="">{t('surveillance.select')}</option>
                  {projects.map(p => <option key={p.id} value={p.id}>{p.title}</option>)}
                </select>
              </div>
              <div className="mb-5">
                <label>{t('surveillance.cycle')}</label>
                <select value={form.cycle_number} onChange={e => setForm({ ...form, cycle_number: parseInt(e.target.value) })}
                  className="input">
                  <option value={1}>{t('surveillance.cycle_y1')}</option>
                  <option value={2}>{t('surveillance.cycle_y2')}</option>
                  <option value={3}>{t('surveillance.cycle_y3')}</option>
                </select>
              </div>
              <div className="mb-5">
                <label>{t('surveillance.scheduled_date')}</label>
                <input type="date" value={form.scheduled_date}
                  onChange={e => setForm({ ...form, scheduled_date: e.target.value })}
                  className="input" />
              </div>
              <div className="mb-5">
                <label>{t('surveillance.notes')}</label>
                <input type="text" value={form.notes} placeholder={t('surveillance.notes_placeholder')}
                  onChange={e => setForm({ ...form, notes: e.target.value })}
                  className="input" />
              </div>
            </div>
            <button className="btn btn-primary mt-3" onClick={handleCreate}>{t('surveillance.create_cycle')}</button>
          </div>
        </div>
      )}

      {cycles.length === 0 ? (
        <div className="card mb-5 text-center">
          <div className="card-body">
            <div className="text-5xl mb-3">🔄</div>
            <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">{t('surveillance.empty')}</h3>
            <p className="text-[var(--text-secondary)]">{t('surveillance.empty_sub')}</p>
          </div>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {cycles.map(c => {
            const project = projects.find(p => p.id === c.project_id)
            return (
              <div key={c.id} className="card mb-5 cursor-pointer"
                style={{ borderLeft: `4px solid ${STATUS_COLORS[c.status] || '#999'}` }}
                onClick={() => openCycle(c)}>
                <div className="card-body flex items-center justify-between">
                  <div>
                    <div className="font-semibold text-sm">C{c.cycle_number} — {t(CYCLE_LABELS[c.cycle_number])}</div>
                    <div className="text-xs mt-0.5 text-[var(--text-secondary)]">
                      {project?.title || c.project_id} · {c.scheduled_date}
                    </div>
                  </div>
                  <span className={`badge badge-${c.status === 'in_progress' ? 'warning' : c.status === 'completed' ? 'success' : c.status === 'overdue' ? 'error' : 'info'}`}>
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
