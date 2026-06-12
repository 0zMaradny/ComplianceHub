import { useState, useEffect } from 'react'
import { useToast } from '../components/Toast'

const GATE_COLORS = {
  1: '#003D7A', 2: '#1A5276', 3: '#2E86C1',
  4: '#27AE60', 5: '#F39C12', 6: '#C0392B',
}

const GATE_LABELS = {
  1: 'Scope', 2: 'Gap', 3: 'Risk',
  4: 'Docs', 5: 'Audit', 6: 'Cert',
}

export default function Projects({ API }) {
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
    if (!form.client_key) errors.client_key = 'Client is required'
    if (!form.title) errors.title = 'Title is required'
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
      showToast('Project created', 'success')
      setShowCreate(false)
      setFormErrors({})
      setForm({ client_key: '', title: '', standards: [], target_date: '', lead_auditor: '' })
      refresh()
    } else showToast('Failed to create project', 'error')
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
    if (!confirm('Delete this project?')) return
    await fetch(`${API}/projects/${pid}`, { method: 'DELETE' })
    showToast('Project deleted', 'success')
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
        <button className="bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200 dark:bg-gray-200 dark:text-gray-800 px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center transition-all duration-150 cursor-pointer whitespace-nowrap mb-4" onClick={() => setSelectedProject(null)}>
          ← Back to Projects
        </button>

        <div className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)] mb-4">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="m-0 mb-1">{p.title}</h2>
              <div className="text-sm text-[var(--gray-500)]">
                {client?.name || p.client_key} · {p.standards.join(', ')} · {p.lead_auditor || 'No lead auditor'}
              </div>
            </div>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" style={{
              background: GATE_COLORS[p.current_gate] + '20',
              color: GATE_COLORS[p.current_gate],
              fontSize: 14, padding: '6px 14px',
            }}>
              G{p.current_gate}: {GATE_LABELS[p.current_gate]}
            </span>
          </div>
        </div>

        {/* Gate Progress */}
        <div className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)] mb-4">
          <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">6-Gate Pipeline</h3>
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
                <div className="text-xs mt-0.5">{GATE_LABELS[g]}</div>
              </div>
            ))}
          </div>
          {p.current_gate < 6 && (
            <button className="bg-[var(--primary)] text-white hover:bg-[var(--primary-dark)] disabled:opacity-50 disabled:cursor-not-allowed px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center border-none transition-all duration-150 cursor-pointer whitespace-nowrap" onClick={() => handleAdvance(p.id)}>
              ▶ Advance to Gate {p.current_gate + 1}
            </button>
          )}
          {p.current_gate === 6 && (
            <div className="text-sm font-semibold" style={{ color: '#27AE60' }}>
              ✅ All gates complete — ready for certification
            </div>
          )}
        </div>

        {/* NC + CAPA Summary */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)]">
            <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">Nonconformities</h3>
            <div className="grid grid-cols-2 gap-2 mt-2">
              <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]"><div className="text-3xl font-bold text-[var(--primary)]">{selectedProject.nc_summary.total}</div><h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">Total</h3></div>
              <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]"><div className="text-3xl font-bold text-[var(--primary)]" style={{ color: '#E74C3C' }}>{selectedProject.nc_summary.open}</div><h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">Open</h3></div>
              <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]"><div className="text-3xl font-bold text-[var(--primary)]" style={{ color: '#E67E22' }}>{selectedProject.nc_summary.major}</div><h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">Major</h3></div>
              <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]"><div className="text-3xl font-bold text-[var(--primary)]" style={{ color: '#F39C12' }}>{selectedProject.nc_summary.minor}</div><h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">Minor</h3></div>
            </div>
          </div>
          <div className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)]">
            <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">CAPA Items</h3>
            <div className="grid grid-cols-2 gap-2 mt-2">
              <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]"><div className="text-3xl font-bold text-[var(--primary)]">{selectedProject.capa_summary.total}</div><h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">Total</h3></div>
              <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]"><div className="text-3xl font-bold text-[var(--primary)]" style={{ color: '#3498DB' }}>{selectedProject.capa_summary.draft}</div><h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">Draft</h3></div>
              <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]"><div className="text-3xl font-bold text-[var(--primary)]" style={{ color: '#F39C12' }}>{selectedProject.capa_summary.in_progress}</div><h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">In Progress</h3></div>
              <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]"><div className="text-3xl font-bold text-[var(--primary)]" style={{ color: '#27AE60' }}>{selectedProject.capa_summary.verified}</div><h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">Verified</h3></div>
            </div>
          </div>
        </div>

        {/* Gate Deliverables */}
        <div className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)]">
          <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">Gate {p.current_gate}: {selectedProject.current_gate_info?.name}</h3>
          <p className="text-sm text-[var(--gray-500)]">{selectedProject.current_gate_info?.description}</p>
          <div className="mt-3">
            <h4 className="text-sm font-semibold text-[var(--text-primary)] m-0 text-[var(--gray-600)]">Deliverables:</h4>
            <ul className="m-1 ml-4 text-sm">
              {selectedProject.current_gate_info?.deliverables?.map((d, i) => (
                <li key={i} className="mb-1">{d.replace(/_/g, ' ')}</li>
              ))}
            </ul>
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
          <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]">
            <div className="text-3xl font-bold text-[var(--primary)]">{stats.total_projects}</div>
            <h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">Projects</h3>
          </div>
          <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]">
            <div className="text-3xl font-bold text-[var(--primary)]" style={{ color: '#27AE60' }}>{stats.active_projects}</div>
            <h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">Active</h3>
          </div>
          <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]">
            <div className="text-3xl font-bold text-[var(--primary)]" style={{ color: '#E74C3C' }}>{stats.open_ncs}</div>
            <h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">Open NCs</h3>
          </div>
          <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]">
            <div className="text-3xl font-bold text-[var(--primary)]" style={{ color: '#F39C12' }}>{stats.pending_capas}</div>
            <h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">Pending CAPAs</h3>
          </div>
        </div>
      )}

      {/* Gate Distribution */}
      {stats?.gate_distribution && (
        <div className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)] mb-4">
          <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">Projects by Gate</h3>
          <div className="flex gap-2">
            {[1, 2, 3, 4, 5, 6].map(g => (
              <div key={g} style={{
                flex: 1, textAlign: 'center', padding: '8px 4px', borderRadius: 6,
                background: GATE_COLORS[g] + '15', border: '2px solid ' + GATE_COLORS[g] + '40',
              }}>
                <div className="text-xl font-bold" style={{ color: GATE_COLORS[g] }}>
                  {stats.gate_distribution[g] || 0}
                </div>
                <div className="text-xs" style={{ color: GATE_COLORS[g] }}>G{g} {GATE_LABELS[g]}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="m-0">Audit Projects</h2>
        <button className="bg-[var(--primary)] text-white hover:bg-[var(--primary-dark)] disabled:opacity-50 disabled:cursor-not-allowed px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center border-none transition-all duration-150 cursor-pointer whitespace-nowrap" onClick={() => setShowCreate(!showCreate)}>
          {showCreate ? '✕ Cancel' : '+ New Project'}
        </button>
      </div>

      {/* Create Form */}
      {showCreate && (
        <div className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)] mb-4">
          <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">Create Audit Project</h3>
          <div className="grid grid-cols-2 gap-3">
            <div className="mb-5">
              <label>Client *</label>
              <select value={form.client_key} onChange={e => { setForm({ ...form, client_key: e.target.value }); setFormErrors(prev => ({ ...prev, client_key: '' })) }}
                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: `1px solid ${formErrors.client_key ? 'var(--red-600)' : 'var(--gray-300)'}` }}>
                <option value="">-- Select --</option>
                {clients.map(c => <option key={c.key} value={c.key}>{c.name}</option>)}
              </select>
              {formErrors.client_key && <span className="text-xs mt-1" style={{ color: 'var(--red-600)' }}>{formErrors.client_key}</span>}
            </div>
            <div className="mb-5">
              <label>Title *</label>
              <input type="text" value={form.title} placeholder="e.g. ISO 22301 Certification 2026"
                onChange={e => { setForm({ ...form, title: e.target.value }); setFormErrors(prev => ({ ...prev, title: '' })) }}
                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: `1px solid ${formErrors.title ? 'var(--red-600)' : 'var(--gray-300)'}` }} />
              {formErrors.title && <span className="text-xs mt-1" style={{ color: 'var(--red-600)' }}>{formErrors.title}</span>}
            </div>
            <div className="mb-5">
              <label>Target Date</label>
              <input type="date" value={form.target_date}
                onChange={e => setForm({ ...form, target_date: e.target.value })}
                className="w-full px-3 py-2 rounded-md border border-[var(--border-color)]" />
            </div>
            <div className="mb-5">
              <label>Lead Auditor</label>
              <input type="text" value={form.lead_auditor}
                onChange={e => setForm({ ...form, lead_auditor: e.target.value })}
                className="w-full px-3 py-2 rounded-md border border-[var(--border-color)]" />
            </div>
          </div>
          <button className="bg-[var(--primary)] text-white hover:bg-[var(--primary-dark)] disabled:opacity-50 disabled:cursor-not-allowed px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center border-none transition-all duration-150 cursor-pointer whitespace-nowrap mt-3" onClick={handleCreate}>
            Create Project
          </button>
        </div>
      )}

      {/* Project List */}
      {projects.length === 0 ? (
        <div className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)] text-center p-10">
          <div className="text-5xl mb-3">📋</div>
          <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">No projects yet</h3>
          <p className="text-[var(--gray-500)]">Create your first audit project to get started</p>
        </div>
      ) : (
        <div className="animate-slideIn flex flex-col gap-2">
          {projects.map(p => {
            const client = clients.find(c => c.key === p.client_key)
            return (
              <div key={p.id} className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)] flex items-center justify-between cursor-pointer p-3"
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
                  <button className="bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200 dark:bg-gray-200 dark:text-gray-800 px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center transition-all duration-150 cursor-pointer whitespace-nowrap" style={{ padding: '4px 8px', fontSize: 11 }}
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
