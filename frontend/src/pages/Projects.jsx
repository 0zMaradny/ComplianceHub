import { useState, useEffect } from 'react'

const GATE_COLORS = {
  1: '#003D7A', 2: '#1A5276', 3: '#2E86C1',
  4: '#27AE60', 5: '#F39C12', 6: '#C0392B',
}

const GATE_LABELS = {
  1: 'Scope', 2: 'Gap', 3: 'Risk',
  4: 'Docs', 5: 'Audit', 6: 'Cert',
}

export default function Projects({ API }) {
  const [projects, setProjects] = useState([])
  const [clients, setClients] = useState([])
  const [stats, setStats] = useState(null)
  const [selectedProject, setSelectedProject] = useState(null)
  const [showCreate, setShowCreate] = useState(false)
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
    if (!form.client_key || !form.title) return
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
      setShowCreate(false)
      setForm({ client_key: '', title: '', standards: [], target_date: '', lead_auditor: '' })
      refresh()
    }
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
      <div>
        <button className="btn btn-secondary" onClick={() => setSelectedProject(null)} style={{ marginBottom: 16 }}>
          ← Back to Projects
        </button>

        <div className="card" style={{ marginBottom: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <h2 style={{ margin: '0 0 4px' }}>{p.title}</h2>
              <div style={{ color: 'var(--gray-500)', fontSize: 13 }}>
                {client?.name || p.client_key} · {p.standards.join(', ')} · {p.lead_auditor || 'No lead auditor'}
              </div>
            </div>
            <span className="badge" style={{
              background: GATE_COLORS[p.current_gate] + '20',
              color: GATE_COLORS[p.current_gate],
              fontSize: 14, padding: '6px 14px',
            }}>
              G{p.current_gate}: {GATE_LABELS[p.current_gate]}
            </span>
          </div>
        </div>

        {/* Gate Progress */}
        <div className="card" style={{ marginBottom: 16 }}>
          <h3 style={{ marginBottom: 12 }}>6-Gate Pipeline</h3>
          <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
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
                <div style={{ fontSize: 18 }}>G{g}</div>
                <div style={{ fontSize: 10, marginTop: 2 }}>{GATE_LABELS[g]}</div>
              </div>
            ))}
          </div>
          {p.current_gate < 6 && (
            <button className="btn btn-primary" onClick={() => handleAdvance(p.id)}>
              ▶ Advance to Gate {p.current_gate + 1}
            </button>
          )}
          {p.current_gate === 6 && (
            <div style={{ color: '#27AE60', fontWeight: 600, fontSize: 14 }}>
              ✅ All gates complete — ready for certification
            </div>
          )}
        </div>

        {/* NC + CAPA Summary */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
          <div className="card">
            <h3>Nonconformities</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginTop: 8 }}>
              <div className="stat-card"><div className="stat-number">{selectedProject.nc_summary.total}</div><h3>Total</h3></div>
              <div className="stat-card"><div className="stat-number" style={{ color: '#E74C3C' }}>{selectedProject.nc_summary.open}</div><h3>Open</h3></div>
              <div className="stat-card"><div className="stat-number" style={{ color: '#E67E22' }}>{selectedProject.nc_summary.major}</div><h3>Major</h3></div>
              <div className="stat-card"><div className="stat-number" style={{ color: '#F39C12' }}>{selectedProject.nc_summary.minor}</div><h3>Minor</h3></div>
            </div>
          </div>
          <div className="card">
            <h3>CAPA Items</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginTop: 8 }}>
              <div className="stat-card"><div className="stat-number">{selectedProject.capa_summary.total}</div><h3>Total</h3></div>
              <div className="stat-card"><div className="stat-number" style={{ color: '#3498DB' }}>{selectedProject.capa_summary.draft}</div><h3>Draft</h3></div>
              <div className="stat-card"><div className="stat-number" style={{ color: '#F39C12' }}>{selectedProject.capa_summary.in_progress}</div><h3>In Progress</h3></div>
              <div className="stat-card"><div className="stat-number" style={{ color: '#27AE60' }}>{selectedProject.capa_summary.verified}</div><h3>Verified</h3></div>
            </div>
          </div>
        </div>

        {/* Gate Deliverables */}
        <div className="card">
          <h3>Gate {p.current_gate}: {selectedProject.current_gate_info?.name}</h3>
          <p style={{ color: 'var(--gray-500)', fontSize: 13 }}>{selectedProject.current_gate_info?.description}</p>
          <div style={{ marginTop: 12 }}>
            <h4 style={{ fontSize: 13, color: 'var(--gray-600)' }}>Deliverables:</h4>
            <ul style={{ margin: '4px 0 0 16px', fontSize: 13 }}>
              {selectedProject.current_gate_info?.deliverables?.map((d, i) => (
                <li key={i} style={{ marginBottom: 4 }}>{d.replace(/_/g, ' ')}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    )
  }

  // ── List View ──
  return (
    <div>
      {/* Dashboard Stats */}
      {stats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 12, marginBottom: 20 }}>
          <div className="stat-card">
            <div className="stat-number">{stats.total_projects}</div>
            <h3>Projects</h3>
          </div>
          <div className="stat-card">
            <div className="stat-number" style={{ color: '#27AE60' }}>{stats.active_projects}</div>
            <h3>Active</h3>
          </div>
          <div className="stat-card">
            <div className="stat-number" style={{ color: '#E74C3C' }}>{stats.open_ncs}</div>
            <h3>Open NCs</h3>
          </div>
          <div className="stat-card">
            <div className="stat-number" style={{ color: '#F39C12' }}>{stats.pending_capas}</div>
            <h3>Pending CAPAs</h3>
          </div>
        </div>
      )}

      {/* Gate Distribution */}
      {stats?.gate_distribution && (
        <div className="card" style={{ marginBottom: 16 }}>
          <h3 style={{ marginBottom: 12 }}>Projects by Gate</h3>
          <div style={{ display: 'flex', gap: 8 }}>
            {[1, 2, 3, 4, 5, 6].map(g => (
              <div key={g} style={{
                flex: 1, textAlign: 'center', padding: '8px 4px', borderRadius: 6,
                background: GATE_COLORS[g] + '15', border: '2px solid ' + GATE_COLORS[g] + '40',
              }}>
                <div style={{ fontSize: 20, fontWeight: 700, color: GATE_COLORS[g] }}>
                  {stats.gate_distribution[g] || 0}
                </div>
                <div style={{ fontSize: 10, color: GATE_COLORS[g] }}>G{g} {GATE_LABELS[g]}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h2 style={{ margin: 0 }}>Audit Projects</h2>
        <button className="btn btn-primary" onClick={() => setShowCreate(!showCreate)}>
          {showCreate ? '✕ Cancel' : '+ New Project'}
        </button>
      </div>

      {/* Create Form */}
      {showCreate && (
        <div className="card" style={{ marginBottom: 16 }}>
          <h3 style={{ marginBottom: 12 }}>Create Audit Project</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div className="form-group">
              <label>Client *</label>
              <select value={form.client_key} onChange={e => setForm({ ...form, client_key: e.target.value })}
                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--gray-300)' }}>
                <option value="">-- Select --</option>
                {clients.map(c => <option key={c.key} value={c.key}>{c.name}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Title *</label>
              <input type="text" value={form.title} placeholder="e.g. ISO 22301 Certification 2026"
                onChange={e => setForm({ ...form, title: e.target.value })}
                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--gray-300)' }} />
            </div>
            <div className="form-group">
              <label>Target Date</label>
              <input type="date" value={form.target_date}
                onChange={e => setForm({ ...form, target_date: e.target.value })}
                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--gray-300)' }} />
            </div>
            <div className="form-group">
              <label>Lead Auditor</label>
              <input type="text" value={form.lead_auditor}
                onChange={e => setForm({ ...form, lead_auditor: e.target.value })}
                style={{ width: '100%', padding: '8px 12px', borderRadius: 6, border: '1px solid var(--gray-300)' }} />
            </div>
          </div>
          <button className="btn btn-primary" onClick={handleCreate} style={{ marginTop: 12 }}>
            Create Project
          </button>
        </div>
      )}

      {/* Project List */}
      {projects.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 40 }}>
          <div style={{ fontSize: 48, marginBottom: 12 }}>📋</div>
          <h3>No projects yet</h3>
          <p style={{ color: 'var(--gray-500)' }}>Create your first audit project to get started</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {projects.map(p => {
            const client = clients.find(c => c.key === p.client_key)
            return (
              <div key={p.id} className="card" style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                cursor: 'pointer', padding: '12px 16px',
              }} onClick={() => openProject(p)}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>{p.title}</div>
                  <div style={{ fontSize: 12, color: 'var(--gray-500)', marginTop: 2 }}>
                    {client?.name || p.client_key} · {p.standards.join(', ')}
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <span className="badge" style={{
                    background: GATE_COLORS[p.current_gate] + '20',
                    color: GATE_COLORS[p.current_gate],
                    fontSize: 12, padding: '4px 10px',
                  }}>
                    G{p.current_gate}
                  </span>
                  <span style={{ fontSize: 12, color: 'var(--gray-400)' }}>
                    {new Date(p.updated_at).toLocaleDateString()}
                  </span>
                  <button className="btn btn-secondary" style={{ padding: '4px 8px', fontSize: 11 }}
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
