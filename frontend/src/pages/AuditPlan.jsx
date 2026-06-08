import { useState } from 'react'

/* ─── Audit Plan Generator — Pre-Audit Client Document ─── */

const AUDIT_TYPES = [
  { value: 'stage1', label: 'Stage 1 — Readiness Review' },
  { value: 'stage2', label: 'Stage 2 — Certification Audit' },
  { value: 'surveillance', label: 'Surveillance Audit' },
  { value: 'recertification', label: 'Recertification Audit' },
  { value: 'transfer', label: 'Transfer Audit' },
]

const ISO_STANDARDS_LIST = [
  { key: 'iso_9001', label: 'ISO 9001:2015 — Quality' },
  { key: 'iso_14001', label: 'ISO 14001:2015 — Environmental' },
  { key: 'iso_45001', label: 'ISO 45001:2018 — OH&S' },
  { key: 'iso_27001', label: 'ISO 27001:2022 — Information Security' },
  { key: 'iso_50001', label: 'ISO 50001:2018 — Energy' },
  { key: 'iso_20000', label: 'ISO 20000-1:2018 — Service Management' },
  { key: 'iso_22301', label: 'ISO 22301:2019 — Business Continuity' },
  { key: 'iso_37301', label: 'ISO 37301:2021 — Compliance' },
  { key: 'iso_42001', label: 'ISO 42001:2023 — AI Management' },
  { key: 'iso_27701', label: 'ISO 27701:2025 — Privacy' },
  { key: 'iso_31000', label: 'ISO 31000:2018 — Risk Management' },
  { key: 'iso_30401', label: 'ISO 30401:2018 — Knowledge Management' },
  { key: 'iso_10002', label: 'ISO 10002:2018 — Complaints Handling' },
]

export default function AuditPlanGenerator({ API }) {
  const [form, setForm] = useState({
    client_name: '',
    client_key: '',
    standards: [],
    audit_type: 'stage2',
    lead_auditor: '',
    audit_team: '',
    start_date: '',
    end_date: '',
    location: '',
    audit_scope: '',
    audit_language: 'English',
    report_due_days: 30,
    notes: '',
  })

  const [schedule, setSchedule] = useState([])
  const [generating, setGenerating] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  // Schedule row management
  const addScheduleRow = () => {
    const day = schedule.length + 1
    setSchedule([...schedule, {
      day,
      date: '',
      time: '09:00 – 17:00',
      activity: '',
      auditee: '',
      auditor: '',
      clause: '',
    }])
  }

  const updateScheduleRow = (idx, field, value) => {
    const updated = [...schedule]
    updated[idx] = { ...updated[idx], [field]: value }
    setSchedule(updated)
  }

  const removeScheduleRow = (idx) => {
    setSchedule(schedule.filter((_, i) => i !== idx))
  }

  const generate = async () => {
    if (!form.client_name || !form.start_date || !form.end_date) {
      setError('Client name, start date, and end date are required.')
      return
    }
    setGenerating(true)
    setError('')
    setResult(null)

    const body = new URLSearchParams()
    Object.entries(form).forEach(([k, v]) => {
      if (Array.isArray(v)) body.append(k, JSON.stringify(v))
      else body.append(k, String(v))
    })
    body.append('daily_schedule', JSON.stringify(schedule))

    try {
      const r = await fetch(`${API}/audit_plan/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body,
      })
      if (!r.ok) {
        const d = await r.json().catch(() => ({}))
        throw new Error(d.detail || 'Generation failed')
      }
      const blob = await r.blob()
      const url = URL.createObjectURL(blob)
      const safeName = form.client_name.replace(/[^a-z0-9]/gi, '_')
      setResult({
        url,
        filename: `TUV_Audit_Plan_${safeName}_${form.audit_type}.docx`,
        size: blob.size,
      })
    } catch (e) {
      setError(e.message)
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div>
      <div style={{ marginBottom: 20 }}>
        <h2 style={{ margin: 0 }}>Audit Plan Generator</h2>
        <p style={{ color: 'var(--gray-500)', margin: '4px 0 0', fontSize: 13 }}>
          Generate a professional TÜV-branded Audit Plan to send to the client before the audit.
          Fill in the details below and download the Word document.
        </p>
      </div>

      {/* ── Section 1: Client & Audit Info ── */}
      <div className="card" style={{ marginBottom: 16 }}>
        <h3 style={{ margin: '0 0 16px', color: '#003D7A' }}>Client & Audit Information</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          <div>
            <label className="form-label">Client Name *</label>
            <input className="form-input" value={form.client_name}
              onChange={e => setForm({ ...form, client_name: e.target.value })}
              placeholder="Organization name" />
          </div>
          <div>
            <label className="form-label">Client Key</label>
            <input className="form-input" value={form.client_key}
              onChange={e => setForm({ ...form, client_key: e.target.value })}
              placeholder="e.g. abc-corp" />
          </div>
          <div>
            <label className="form-label">Audit Type</label>
            <select className="form-input" value={form.audit_type}
              onChange={e => setForm({ ...form, audit_type: e.target.value })}>
              {AUDIT_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
          </div>
          <div>
            <label className="form-label">Location</label>
            <input className="form-input" value={form.location}
              onChange={e => setForm({ ...form, location: e.target.value })}
              placeholder="Audit location / site" />
          </div>
          <div>
            <label className="form-label">Start Date *</label>
            <input type="date" className="form-input" value={form.start_date}
              onChange={e => setForm({ ...form, start_date: e.target.value })} />
          </div>
          <div>
            <label className="form-label">End Date *</label>
            <input type="date" className="form-input" value={form.end_date}
              onChange={e => setForm({ ...form, end_date: e.target.value })} />
          </div>
        </div>

        {/* Standards */}
        <div style={{ marginTop: 12 }}>
          <label className="form-label">Standard(s)</label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {ISO_STANDARDS_LIST.map(std => {
              const selected = form.standards.includes(std.key)
              return (
                <button
                  key={std.key}
                  className={`btn ${selected ? 'btn-primary' : 'btn-secondary'}`}
                  style={{ fontSize: 12, padding: '4px 10px' }}
                  onClick={() => {
                    const newStds = selected
                      ? form.standards.filter(s => s !== std.key)
                      : [...form.standards, std.key]
                    setForm({ ...form, standards: newStds })
                  }}
                >{std.label}</button>
              )
            })}
          </div>
        </div>
      </div>

      {/* ── Section 2: Audit Team ── */}
      <div className="card" style={{ marginBottom: 16 }}>
        <h3 style={{ margin: '0 0 16px', color: '#003D7A' }}>Audit Team</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
          <div>
            <label className="form-label">Lead Auditor</label>
            <input className="form-input" value={form.lead_auditor}
              onChange={e => setForm({ ...form, lead_auditor: e.target.value })}
              placeholder="Lead auditor name" />
          </div>
          <div style={{ gridColumn: 'span 2' }}>
            <label className="form-label">Audit Team (comma-separated)</label>
            <input className="form-input" value={form.audit_team}
              onChange={e => setForm({ ...form, audit_team: e.target.value })}
              placeholder="e.g. John Smith, Jane Doe, Ahmed Ali" />
          </div>
        </div>
      </div>

      {/* ── Section 3: Scope & Language ── */}
      <div className="card" style={{ marginBottom: 16 }}>
        <h3 style={{ margin: '0 0 16px', color: '#003D7A' }}>Scope & Language</h3>
        <div style={{ marginBottom: 12 }}>
          <label className="form-label">Audit Scope</label>
          <textarea className="form-input" rows={3} value={form.audit_scope}
            onChange={e => setForm({ ...form, audit_scope: e.target.value })}
            placeholder="Describe the audit scope — sites, processes, activities covered..." />
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
          <div>
            <label className="form-label">Audit Language</label>
            <select className="form-input" value={form.audit_language}
              onChange={e => setForm({ ...form, audit_language: e.target.value })}>
              <option value="English">English</option>
              <option value="Arabic">Arabic</option>
              <option value="English / Arabic">English / Arabic</option>
            </select>
          </div>
          <div>
            <label className="form-label">Report Due (days after audit)</label>
            <input type="number" className="form-input" min={1} max={90}
              value={form.report_due_days}
              onChange={e => setForm({ ...form, report_due_days: +e.target.value })} />
          </div>
        </div>
        <div style={{ marginTop: 12 }}>
          <label className="form-label">Additional Notes</label>
          <textarea className="form-input" rows={2} value={form.notes}
            onChange={e => setForm({ ...form, notes: e.target.value })}
            placeholder="Any additional information for the client..." />
        </div>
      </div>

      {/* ── Section 4: Daily Schedule ── */}
      <div className="card" style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
          <h3 style={{ margin: 0, color: '#003D7A' }}>Daily Schedule</h3>
          <button className="btn btn-primary" onClick={addScheduleRow}>+ Add Day / Slot</button>
        </div>

        {schedule.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 20, color: 'var(--gray-500)', fontSize: 13 }}>
            No schedule entries. Click "Add Day / Slot" to build the daily audit programme.
            <br />A default schedule will be auto-generated if left empty.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table" style={{ width: '100%', minWidth: 800 }}>
              <thead>
                <tr>
                  <th>Day</th>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Activity</th>
                  <th>Auditee</th>
                  <th>Auditor</th>
                  <th>Clause Ref</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {schedule.map((row, idx) => (
                  <tr key={idx}>
                    <td>
                      <input className="form-input" style={{ width: 50, padding: '4px' }}
                        type="number" min={1} value={row.day}
                        onChange={e => updateScheduleRow(idx, 'day', +e.target.value)} />
                    </td>
                    <td>
                      <input className="form-input" style={{ width: 110, padding: '4px' }}
                        type="date" value={row.date}
                        onChange={e => updateScheduleRow(idx, 'date', e.target.value)} />
                    </td>
                    <td>
                      <input className="form-input" style={{ width: 120, padding: '4px' }}
                        value={row.time}
                        onChange={e => updateScheduleRow(idx, 'time', e.target.value)}
                        placeholder="09:00 – 17:00" />
                    </td>
                    <td>
                      <input className="form-input" style={{ minWidth: 150, padding: '4px' }}
                        value={row.activity}
                        onChange={e => updateScheduleRow(idx, 'activity', e.target.value)}
                        placeholder="Activity description" />
                    </td>
                    <td>
                      <input className="form-input" style={{ width: 100, padding: '4px' }}
                        value={row.auditee}
                        onChange={e => updateScheduleRow(idx, 'auditee', e.target.value)}
                        placeholder="Department / person" />
                    </td>
                    <td>
                      <input className="form-input" style={{ width: 100, padding: '4px' }}
                        value={row.auditor}
                        onChange={e => updateScheduleRow(idx, 'auditor', e.target.value)}
                        placeholder="Auditor name" />
                    </td>
                    <td>
                      <input className="form-input" style={{ width: 80, padding: '4px' }}
                        value={row.clause}
                        onChange={e => updateScheduleRow(idx, 'clause', e.target.value)}
                        placeholder="e.g. 4.1-5.3" />
                    </td>
                    <td>
                      <button className="btn btn-danger" style={{ padding: '2px 6px', fontSize: 12 }}
                        onClick={() => removeScheduleRow(idx)}>✕</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* ── Generate Button ── */}
      <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 20 }}>
        <button
          className="btn btn-primary"
          style={{ fontSize: 16, padding: '12px 32px' }}
          onClick={generate}
          disabled={generating}
        >
          {generating ? '⏳ Generating...' : '📄 Generate Audit Plan'}
        </button>
        {error && <span style={{ color: '#DC2626', fontSize: 13 }}>⚠ {error}</span>}
      </div>

      {/* ── Result ── */}
      {result && (
        <div className="card" style={{ border: '2px solid #059669', background: '#F0FDF4' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h4 style={{ margin: '0 0 4px', color: '#065F46' }}>✅ Audit Plan Generated</h4>
              <p style={{ margin: 0, fontSize: 13, color: '#047857' }}>
                {result.filename} ({(result.size / 1024).toFixed(1)} KB)
              </p>
            </div>
            <a href={result.url} download={result.filename}
              className="btn btn-primary" style={{ background: '#059669' }}>
              ⬇ Download Word Document
            </a>
          </div>
        </div>
      )}
    </div>
  )
}
