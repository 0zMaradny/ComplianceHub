import { useState } from 'react'

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
    client_name: '', client_key: '', standards: [], audit_type: 'stage2',
    lead_auditor: '', audit_team: '', start_date: '', end_date: '',
    location: '', audit_scope: '', audit_language: 'English', report_due_days: 30, notes: '',
  })
  const [schedule, setSchedule] = useState([])
  const [generating, setGenerating] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const addScheduleRow = () => {
    const day = schedule.length + 1
    setSchedule([...schedule, { day, date: '', time: '09:00 – 17:00', activity: '', auditee: '', auditor: '', clause: '' }])
  }

  const removeScheduleRow = (idx) => setSchedule(schedule.filter((_, i) => i !== idx))

  const generate = async () => {
    if (!form.client_name || !form.start_date || !form.end_date) {
      setError('Client name, start date, and end date are required.'); return
    }
    setGenerating(true); setError(''); setResult(null)
    const body = new URLSearchParams()
    Object.entries(form).forEach(([k, v]) => body.append(k, Array.isArray(v) ? JSON.stringify(v) : String(v)))
    body.append('daily_schedule', JSON.stringify(schedule))
    try {
      const r = await fetch(`${API}/audit_plan/generate`, {
        method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body,
      })
      if (!r.ok) { const d = await r.json().catch(() => ({})); throw new Error(d.detail || 'Generation failed') }
      const blob = await r.blob()
      const url = URL.createObjectURL(blob)
      const safeName = form.client_name.replace(/[^a-z0-9]/gi, '_')
      setResult({ url, filename: `TUV_Audit_Plan_${safeName}_${form.audit_type}.docx`, size: blob.size })
    } catch (e) { setError(e.message) }
    finally { setGenerating(false) }
  }

  return (
    <div className="animate-fadeIn">
      <div className="mb-5">
        <h2 className="m-0">Audit Plan Generator</h2>
        <p className="text-sm mt-1" style={{ color: 'var(--gray-500)' }}>
          Generate a professional TÜV-branded Audit Plan to send to the client before the audit.
        </p>
      </div>

      <div className="card mb-4">
        <h3 className="m-0 mb-4" style={{ color: '#003D7A' }}>Client & Audit Information</h3>
        <div className="grid grid-cols-2 gap-3">
          {[
            { label: 'Client Name *', key: 'client_name', type: 'text', placeholder: 'Organization name' },
            { label: 'Client Key', key: 'client_key', type: 'text', placeholder: 'e.g. abc-corp' },
            { label: 'Audit Type', key: 'audit_type', type: 'select', options: AUDIT_TYPES },
            { label: 'Location', key: 'location', type: 'text', placeholder: 'Audit location / site' },
            { label: 'Start Date *', key: 'start_date', type: 'date' },
            { label: 'End Date *', key: 'end_date', type: 'date' },
          ].map(f => (
            <div key={f.key}>
              <label className="form-label">{f.label}</label>
              {f.type === 'select' ? (
                <select className="form-input" value={form[f.key]} onChange={e => setForm({ ...form, [f.key]: e.target.value })}>
                  {f.options.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
              ) : (
                <input type={f.type} className="form-input" value={form[f.key]}
                  onChange={e => setForm({ ...form, [f.key]: e.target.value })}
                  placeholder={f.placeholder} />
              )}
            </div>
          ))}
        </div>
        <div className="mt-3">
          <label className="form-label">Standard(s)</label>
          <div className="flex flex-wrap gap-1.5">
            {ISO_STANDARDS_LIST.map(std => {
              const selected = form.standards.includes(std.key)
              return (
                <button key={std.key}
                  className={`btn ${selected ? 'btn-primary' : 'btn-secondary'}`}
                  style={{ fontSize: 12, padding: '4px 10px' }}
                  onClick={() => setForm({ ...form, standards: selected ? form.standards.filter(s => s !== std.key) : [...form.standards, std.key] })}>
                  {std.label}
                </button>
              )
            })}
          </div>
        </div>
      </div>

      <div className="card mb-4">
        <h3 className="m-0 mb-4" style={{ color: '#003D7A' }}>Audit Team</h3>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <label className="form-label">Lead Auditor</label>
            <input className="form-input" value={form.lead_auditor}
              onChange={e => setForm({ ...form, lead_auditor: e.target.value })}
              placeholder="Lead auditor name" />
          </div>
          <div className="col-span-2">
            <label className="form-label">Audit Team (comma-separated)</label>
            <input className="form-input" value={form.audit_team}
              onChange={e => setForm({ ...form, audit_team: e.target.value })}
              placeholder="e.g. John Smith, Jane Doe, Ahmed Ali" />
          </div>
        </div>
      </div>

      <div className="card mb-4">
        <h3 className="m-0 mb-4" style={{ color: '#003D7A' }}>Scope & Language</h3>
        <div className="mb-3">
          <label className="form-label">Audit Scope</label>
          <textarea className="form-input" rows={3} value={form.audit_scope}
            onChange={e => setForm({ ...form, audit_scope: e.target.value })}
            placeholder="Describe the audit scope — sites, processes, activities covered..." />
        </div>
        <div className="grid grid-cols-3 gap-3">
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
            <label className="form-label">Report Due (days)</label>
            <input type="number" className="form-input" min={1} max={90} value={form.report_due_days}
              onChange={e => setForm({ ...form, report_due_days: +e.target.value })} />
          </div>
        </div>
        <div className="mt-3">
          <label className="form-label">Additional Notes</label>
          <textarea className="form-input" rows={2} value={form.notes}
            onChange={e => setForm({ ...form, notes: e.target.value })}
            placeholder="Any additional information for the client..." />
        </div>
      </div>

      <div className="card mb-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="m-0" style={{ color: '#003D7A' }}>Daily Schedule</h3>
          <button className="btn btn-primary" onClick={addScheduleRow}>+ Add Day / Slot</button>
        </div>
        {schedule.length === 0 ? (
          <div className="text-center py-5 text-sm" style={{ color: 'var(--gray-500)' }}>
            No schedule entries. Click "Add Day / Slot" to build the daily audit programme.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="table w-full" style={{ minWidth: 800 }}>
              <thead><tr>
                <th>Day</th><th>Date</th><th>Time</th><th>Activity</th><th>Auditee</th><th>Auditor</th><th>Clause Ref</th><th></th>
              </tr></thead>
              <tbody>
                {schedule.map((row, idx) => (
                  <tr key={idx}>
                    {['day', 'date', 'time', 'activity', 'auditee', 'auditor', 'clause'].map(f => (
                      <td key={f}>
                        <input className="form-input" style={{ width: f === 'day' ? 50 : f === 'date' ? 110 : f === 'time' ? 120 : f === 'clause' ? 80 : 100, padding: 4 }}
                          type={f === 'day' ? 'number' : f === 'date' ? 'date' : 'text'}
                          min={f === 'day' ? 1 : undefined}
                          value={row[f]} placeholder={f === 'time' ? '09:00 – 17:00' : f === 'activity' ? 'Activity description' : f === 'auditee' ? 'Department / person' : f === 'auditor' ? 'Auditor name' : f === 'clause' ? 'e.g. 4.1-5.3' : ''}
                          onChange={e => { const s = [...schedule]; s[idx] = { ...s[idx], [f]: e.target.value }; setSchedule(s) }} />
                      </td>
                    ))}
                    <td>
                      <button className="btn btn-danger px-1.5 py-0.5 text-xs" onClick={() => removeScheduleRow(idx)}>✕</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="flex gap-3 items-center mb-5">
        <button className="btn btn-primary text-lg px-8 py-3" onClick={generate} disabled={generating}>
          {generating ? '⏳ Generating...' : '📄 Generate Audit Plan'}
        </button>
        {error && <span className="text-sm" style={{ color: '#DC2626' }}>⚠ {error}</span>}
      </div>

      {result && (
        <div className="card" style={{ border: '2px solid #059669', background: '#F0FDF4' }}>
          <div className="flex items-center justify-between">
            <div>
              <h4 className="m-0 mb-1" style={{ color: '#065F46' }}>✅ Audit Plan Generated</h4>
              <p className="m-0 text-sm" style={{ color: '#047857' }}>
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
