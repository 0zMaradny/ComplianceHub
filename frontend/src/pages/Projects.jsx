import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useToast } from '../hooks/useToast'
import EmptyState from '../components/EmptyState'

const GATE_COLORS = {
  1: '#003D7A', 2: '#1A5276', 3: '#2E86C1',
  4: '#27AE60', 5: '#F39C12', 6: '#C0392B',
}

const GATE_LABELS = {
  1: 'projects.gate_scope', 2: 'projects.gate_gap', 3: 'projects.gate_risk',
  4: 'projects.gate_docs', 5: 'projects.gate_audit', 6: 'projects.gate_cert',
}

export default function Projects({ API }) {
  const { t } = useTranslation()
  const showToast = useToast()
  const [projects, setProjects] = useState([])
  const [clients, setClients] = useState([])
  const [stats, setStats] = useState(null)
  const [selectedProject, setSelectedProject] = useState(null)
  const [showCreate, setShowCreate] = useState(false)
  const [formErrors, setFormErrors] = useState({})
  const [form, setForm] = useState({
    client_key: '', title: '', standards: [], target_date: '', lead_auditor: '',
  })

  useEffect(() => {
    fetch(`${API}/projects`).then(r => r.json()).then(d => setProjects(d.projects || []))
    fetch(`${API}/clients`).then(r => r.json()).then(d => setClients(d.clients || []))
    fetch(`${API}/dashboard`).then(r => r.json()).then(d => setStats(d))
  }, [API])

  const refresh = () => {
    fetch(`${API}/projects`).then(r => r.json()).then(d => setProjects(d.projects || []))
    fetch(`${API}/dashboard`).then(r => r.json()).then(d => setStats(d))
  }

  const handleCreate = async () => {
    const errors = {}
    if (!form.client_key) errors.client_key = t('projects.client_required')
    if (!form.title) errors.title = t('projects.title_required')
    setFormErrors(errors)
    if (Object.keys(errors).length > 0) return
    const body = new URLSearchParams()
    body.append('client_key', form.client_key)
    body.append('title', form.title)
    body.append('standards', JSON.stringify(form.standards))
    if (form.target_date) body.append('target_date', form.target_date)
    if (form.lead_auditor) body.append('lead_auditor', form.lead_auditor)
    const r = await fetch(`${API}/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body,
    })
    if (r.ok) {
      showToast(t('projects.created'), 'success')
      setShowCreate(false)
      setFormErrors({})
      setForm({ client_key: '', title: '', standards: [], target_date: '', lead_auditor: '' })
      refresh()
    } else showToast(t('projects.create_failed'), 'error')
  }

  const handleAdvance = async (pid) => {
    await fetch(`${API}/projects/${pid}/advance`, { method: 'POST' })
    refresh()
    if (selectedProject?.id === pid) {
      const r = await fetch(`${API}/projects/${pid}/progress`)
      if (r.ok) setSelectedProject(await r.json())
    }
  }

  const handleDelete = async (pid) => {
    if (!confirm(t('projects.delete_confirm'))) return
    await fetch(`${API}/projects/${pid}`, { method: 'DELETE' })
    showToast(t('projects.deleted'), 'success')
    setSelectedProject(null)
    refresh()
  }

  const openProject = async (p) => {
    const r = await fetch(`${API}/projects/${p.id}/progress`)
    if (r.ok) setSelectedProject(await r.json())
  }

  // ── Detail View ──
  if (selectedProject) {
    const p = selectedProject.project
    const client = clients.find(c => c.key === p.client_key)
    return (
      <div className="animate-fadeIn">
        <button className="btn btn-ghost mb-4" onClick={() => setSelectedProject(null)}>
            {t('projects.back')}
        </button>

        <div className="card mb-5 p-6">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="m-0 mb-1">{p.title}</h2>
              <div className="text-sm text-[var(--gray-500)]">
                {client?.name || p.client_key} · {p.standards.join(', ')} · {p.lead_auditor || t('projects.no_auditor')}
              </div>
            </div>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" style={{
              background: GATE_COLORS[p.current_gate] + '20',
              color: GATE_COLORS[p.current_gate],
              fontSize: 14, padding: '6px 14px',
            }}>
              G{p.current_gate}: {t(GATE_LABELS[p.current_gate])}
            </span>
          </div>
        </div>

        {/* Gate Progress */}
        <div className="card mb-5">
          <div className="card-header">{t('projects.pipeline')}</div>
          <div className="card-body">
            <div className="flex gap-2 mb-4">
              {[1, 2, 3, 4, 5, 6].map(g => (
                <div key={g} style={{
                  flex: 1, textAlign: 'center', padding: '12px 4px',
                  borderRadius: 8, cursor: 'pointer',
                  background: g <= p.current_gate ? GATE_COLORS[g] : 'var(--gray-100)',
                  color: g <= p.current_gate ? '#fff' : 'var(--gray-400)',
                  fontWeight: g === p.current_gate ? 700 : 400,
                  border: g === p.current_gate ? '3px solid ' + GATE_COLORS[g] : '3px solid transparent',
                  boxShadow: g === p.current_gate ? '0 2px 8px rgba(0,0,0,0.15)' : 'none',
                }}>
                  <div className="text-lg">G{g}</div>
                  <div className="text-xs mt-0.5">{t(GATE_LABELS[g])}</div>
                </div>
              ))}
            </div>
            {p.current_gate < 6 && (
              <button className="btn btn-primary" onClick={() => handleAdvance(p.id)}>
                {t('projects.advance_gate')}{p.current_gate + 1}
              </button>
            )}
            {p.current_gate === 6 && (
              <div className="text-sm font-semibold" style={{ color: '#27AE60' }}>
                {t('projects.gates_complete')}
              </div>
            )}
          </div>
        </div>

        {/* NC + CAPA Summary */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="card mb-5">
            <div className="card-header">{t('projects.nonconformities')}</div>
            <div className="card-body">
              <div className="grid grid-cols-2 gap-2">
                <div className="stat-card"><div className="stat-card-value" style={{ color: 'var(--primary)' }}>{selectedProject.nc_summary.total}</div><div className="stat-card-label">{t('projects.total')}</div></div>
                <div className="stat-card"><div className="stat-card-value" style={{ color: '#E74C3C' }}>{selectedProject.nc_summary.open}</div><div className="stat-card-label">{t('projects.open')}</div></div>
                <div className="stat-card"><div className="stat-card-value" style={{ color: '#E67E22' }}>{selectedProject.nc_summary.major}</div><div className="stat-card-label">{t('projects.major')}</div></div>
                <div className="stat-card"><div className="stat-card-value" style={{ color: '#F39C12' }}>{selectedProject.nc_summary.minor}</div><div className="stat-card-label">{t('projects.minor')}</div></div>
              </div>
            </div>
          </div>
          <div className="card mb-5">
            <div className="card-header">{t('projects.capa_items')}</div>
            <div className="card-body">
              <div className="grid grid-cols-2 gap-2">
                <div className="stat-card"><div className="stat-card-value" style={{ color: 'var(--primary)' }}>{selectedProject.capa_summary.total}</div><div className="stat-card-label">{t('projects.total')}</div></div>
                <div className="stat-card"><div className="stat-card-value" style={{ color: '#3498DB' }}>{selectedProject.capa_summary.draft}</div><div className="stat-card-label">{t('projects.draft')}</div></div>
                <div className="stat-card"><div className="stat-card-value" style={{ color: '#F39C12' }}>{selectedProject.capa_summary.in_progress}</div><div className="stat-card-label">{t('projects.in_progress')}</div></div>
                <div className="stat-card"><div className="stat-card-value" style={{ color: '#27AE60' }}>{selectedProject.capa_summary.verified}</div><div className="stat-card-label">{t('projects.verified')}</div></div>
              </div>
            </div>
          </div>
        </div>

        {/* Gate Deliverables */}
        <div className="card mb-5">
          <div className="card-header">Gate {p.current_gate}: {selectedProject.current_gate_info?.name}</div>
          <div className="card-body">
            <p className="text-sm text-[var(--gray-500)]">{selectedProject.current_gate_info?.description}</p>
            <div className="mt-3">
              <h4 className="text-sm font-semibold text-[var(--text-primary)] m-0 text-[var(--gray-600)]">{t('projects.deliverables')}</h4>
              <ul className="m-1 ml-4 text-sm">
                {selectedProject.current_gate_info?.deliverables?.map((d, i) => (
                  <li key={i} className="mb-1">{d.replace(/_/g, ' ')}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // ── List View ──
  return (
    <div className="animate-fadeIn">
      {/* Dashboard Stats */}
      {stats && (
        <div className="grid gap-3 mb-5" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))' }}>
          <div className="stat-card">
            <div className="stat-card-value" style={{ color: 'var(--primary)' }}>{stats.total_projects}</div>
            <div className="stat-card-label">{t('projects.projects')}</div>
          </div>
          <div className="stat-card">
            <div className="stat-card-value" style={{ color: '#27AE60' }}>{stats.active_projects}</div>
            <div className="stat-card-label">{t('projects.active')}</div>
          </div>
          <div className="stat-card">
            <div className="stat-card-value" style={{ color: '#E74C3C' }}>{stats.open_ncs}</div>
            <div className="stat-card-label">{t('projects.open_ncs')}</div>
          </div>
          <div className="stat-card">
            <div className="stat-card-value" style={{ color: '#F39C12' }}>{stats.pending_capas}</div>
            <div className="stat-card-label">{t('projects.pending_capas')}</div>
          </div>
        </div>
      )}

      {/* Gate Distribution */}
      {stats?.gate_distribution && (
        <div className="card mb-5">
          <div className="card-header">{t('projects.by_gate')}</div>
          <div className="card-body">
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5, 6].map(g => (
                <div key={g} style={{
                  flex: 1, textAlign: 'center', padding: '8px 4px', borderRadius: 6,
                  background: GATE_COLORS[g] + '15', border: '2px solid ' + GATE_COLORS[g] + '40',
                }}>
                  <div className="text-xl font-bold" style={{ color: GATE_COLORS[g] }}>
                    {stats.gate_distribution[g] || 0}
                  </div>
                  <div className="text-xs" style={{ color: GATE_COLORS[g] }}>G{g} {t(GATE_LABELS[g])}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div><h2>{t('projects.audit_projects')}</h2></div>
        <button className="btn btn-primary" onClick={() => setShowCreate(!showCreate)}>
          {showCreate ? t('projects.cancel') : t('projects.new')}
        </button>
      </div>

      {/* Create Form */}
      {showCreate && (
        <div className="card mb-5">
          <div className="card-header">{t('projects.create_title')}</div>
          <div className="card-body">
            <div className="grid grid-cols-2 gap-3">
              <div className="mb-5">
                <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('projects.client')}</label>
                <select className="input" value={form.client_key}
                  style={formErrors.client_key ? { border: '1px solid var(--red-600)' } : {}}
                  onChange={e => { setForm({ ...form, client_key: e.target.value }); setFormErrors(prev => ({ ...prev, client_key: '' })) }}>
                  <option value="">{t('projects.select_client')}</option>
                  {clients.map(c => <option key={c.key} value={c.key}>{c.name}</option>)}
                </select>
                {formErrors.client_key && <span className="text-xs mt-1" style={{ color: 'var(--red-600)' }}>{formErrors.client_key}</span>}
              </div>
              <div className="mb-5">
                <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('projects.project_title')}</label>
                <input type="text" className="input" value={form.title} placeholder={t('projects.title_placeholder')}
                  style={formErrors.title ? { border: '1px solid var(--red-600)' } : {}}
                  onChange={e => { setForm({ ...form, title: e.target.value }); setFormErrors(prev => ({ ...prev, title: '' })) }} />
                {formErrors.title && <span className="text-xs mt-1" style={{ color: 'var(--red-600)' }}>{formErrors.title}</span>}
              </div>
              <div className="mb-5">
                <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('projects.target_date')}</label>
                <input type="date" className="input" value={form.target_date}
                  onChange={e => setForm({ ...form, target_date: e.target.value })} />
              </div>
              <div className="mb-5">
                <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('projects.lead_auditor')}</label>
                <input type="text" className="input" value={form.lead_auditor}
                  onChange={e => setForm({ ...form, lead_auditor: e.target.value })} />
              </div>
            </div>
            <button className="btn btn-primary mt-3" onClick={handleCreate}>
              {t('projects.create')}
            </button>
          </div>
        </div>
      )}

      {/* Project List */}
      {projects.length === 0 ? (
        <div className="card text-center p-10">
          <div className="text-5xl mb-3">📋</div>
          <EmptyState icon="folder" title={t('projects.empty')} description={t('projects.empty_sub')} />
        </div>
      ) : (
        <div className="animate-slideIn flex flex-col gap-2">
          {projects.map(p => {
            const client = clients.find(c => c.key === p.client_key)
            return (
              <div key={p.id} className="card cursor-pointer flex items-center justify-between p-3"
                   onClick={() => openProject(p)}>
                <div>
                  <div className="font-semibold text-sm">{p.title}</div>
                  <div className="text-xs mt-0.5 text-[var(--gray-500)]">
                    {client?.name || p.client_key} · {p.standards.join(', ')}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" style={{
                    background: GATE_COLORS[p.current_gate] + '20',
                    color: GATE_COLORS[p.current_gate],
                    fontSize: 12, padding: '4px 10px',
                  }}>
                    G{p.current_gate}
                  </span>
                  <span className="text-xs text-[var(--gray-400)]">
                    {new Date(p.updated_at).toLocaleDateString()}
                  </span>
                  <button className="btn btn-ghost" style={{ padding: '4px 8px', fontSize: 11 }}
                    onClick={e => { e.stopPropagation(); handleDelete(p.id) }}>
                    🗑
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
