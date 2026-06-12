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
        <p className="text-sm mt-1 text-[var(--gray-500)]">
          Generate a professional TÜV-branded Audit Plan to send to the client before the audit.
        </p>
      </div>

      <div className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)] mb-4">
        <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">Client & Audit Information</h3>
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
              <label className="block text-xs font-semibold mb-1.5 text-gray-700 dark:text-gray-300">{f.label}</label>
              {f.type === 'select' ? (
                <select className="w-full px-3 py-2.5 rounded-lg text-sm transition-colors border border-[var(--input-border)] bg-[var(--input-bg)] text-[var(--text-primary)] focus:outline-none focus:border-[var(--primary)] focus:ring-3 focus:ring-[rgba(0,61,122,0.1)]" value={form[f.key]} onChange={e => setForm({ ...form, [f.key]: e.target.value })}>
                  {f.options.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
              ) : (
                <input type={f.type} className="w-full px-3 py-2.5 rounded-lg text-sm transition-colors border border-[var(--input-border)] bg-[var(--input-bg)] text-[var(--text-primary)] focus:outline-none focus:border-[var(--primary)] focus:ring-3 focus:ring-[rgba(0,61,122,0.1)]" value={form[f.key]}
                  onChange={e => setForm({ ...form, [f.key]: e.target.value })}
                  placeholder={f.placeholder} />
              )}
            </div>
          ))}
        </div>
        <div className="mt-3">
          <label className="block text-xs font-semibold mb-1.5 text-gray-700 dark:text-gray-300">Standard(s)</label>
          <div className="flex flex-wrap gap-1.5">
            {ISO_STANDARDS_LIST.map(std => {
              const selected = form.standards.includes(std.key)
              return (
                <button key={std.key}
                  className={`${selected ? 'bg-[var(--primary)] text-white hover:bg-[var(--primary-dark)] disabled:opacity-50 disabled:cursor-not-allowed px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center border-none transition-all duration-150 cursor-pointer whitespace-nowrap' : 'bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200 dark:bg-gray-200 dark:text-gray-800 px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center transition-all duration-150 cursor-pointer whitespace-nowrap'}`}
                  style={{ fontSize: 12, padding: '4px 10px' }}
                  onClick={() => setForm({ ...form, standards: selected ? form.standards.filter(s => s !== std.key) : [...form.standards, std.key] })}>
                  {std.label}
                </button>
              )
            })}
          </div>
        </div>
      </div>

      <div className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)] mb-4">
        <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">Audit Team</h3>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <label className="block text-xs font-semibold mb-1.5 text-gray-700 dark:text-gray-300">Lead Auditor</label>
            <input className="w-full px-3 py-2.5 rounded-lg text-sm transition-colors border border-[var(--input-border)] bg-[var(--input-bg)] text-[var(--text-primary)] focus:outline-none focus:border-[var(--primary)] focus:ring-3 focus:ring-[rgba(0,61,122,0.1)]" value={form.lead_auditor}
              onChange={e => setForm({ ...form, lead_auditor: e.target.value })}
              placeholder="Lead auditor name" />
          </div>
          <div className="col-span-2">
            <label className="block text-xs font-semibold mb-1.5 text-gray-700 dark:text-gray-300">Audit Team (comma-separated)</label>
            <input className="w-full px-3 py-2.5 rounded-lg text-sm transition-colors border border-[var(--input-border)] bg-[var(--input-bg)] text-[var(--text-primary)] focus:outline-none focus:border-[var(--primary)] focus:ring-3 focus:ring-[rgba(0,61,122,0.1)]" value={form.audit_team}
              onChange={e => setForm({ ...form, audit_team: e.target.value })}
              placeholder="e.g. John Smith, Jane Doe, Ahmed Ali" />
          </div>
        </div>
      </div>

      <div className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)] mb-4">
        <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">Scope & Language</h3>
        <div className="mb-3">
          <label className="block text-xs font-semibold mb-1.5 text-gray-700 dark:text-gray-300">Audit Scope</label>
          <textarea className="w-full px-3 py-2.5 rounded-lg text-sm transition-colors border border-[var(--input-border)] bg-[var(--input-bg)] text-[var(--text-primary)] focus:outline-none focus:border-[var(--primary)] focus:ring-3 focus:ring-[rgba(0,61,122,0.1)]" rows={3} value={form.audit_scope}
            onChange={e => setForm({ ...form, audit_scope: e.target.value })}
            placeholder="Describe the audit scope — sites, processes, activities covered..." />
        </div>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <label className="block text-xs font-semibold mb-1.5 text-gray-700 dark:text-gray-300">Audit Language</label>
            <select className="w-full px-3 py-2.5 rounded-lg text-sm transition-colors border border-[var(--input-border)] bg-[var(--input-bg)] text-[var(--text-primary)] focus:outline-none focus:border-[var(--primary)] focus:ring-3 focus:ring-[rgba(0,61,122,0.1)]" value={form.audit_language}
              onChange={e => setForm({ ...form, audit_language: e.target.value })}>
              <option value="English">English</option>
              <option value="Arabic">Arabic</option>
              <option value="English / Arabic">English / Arabic</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold mb-1.5 text-gray-700 dark:text-gray-300">Report Due (days)</label>
            <input type="number" className="w-full px-3 py-2.5 rounded-lg text-sm transition-colors border border-[var(--input-border)] bg-[var(--input-bg)] text-[var(--text-primary)] focus:outline-none focus:border-[var(--primary)] focus:ring-3 focus:ring-[rgba(0,61,122,0.1)]" min={1} max={90} value={form.report_due_days}
              onChange={e => setForm({ ...form, report_due_days: +e.target.value })} />
          </div>
        </div>
        <div className="mt-3">
          <label className="block text-xs font-semibold mb-1.5 text-gray-700 dark:text-gray-300">Additional Notes</label>
          <textarea className="w-full px-3 py-2.5 rounded-lg text-sm transition-colors border border-[var(--input-border)] bg-[var(--input-bg)] text-[var(--text-primary)] focus:outline-none focus:border-[var(--primary)] focus:ring-3 focus:ring-[rgba(0,61,122,0.1)]" rows={2} value={form.notes}
            onChange={e => setForm({ ...form, notes: e.target.value })}
            placeholder="Any additional information for the client..." />
        </div>
      </div>

      <div className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)] mb-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">Daily Schedule</h3>
          <button className="bg-[var(--primary)] text-white hover:bg-[var(--primary-dark)] disabled:opacity-50 disabled:cursor-not-allowed px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center border-none transition-all duration-150 cursor-pointer whitespace-nowrap" onClick={addScheduleRow}>+ Add Day / Slot</button>
        </div>
        {schedule.length === 0 ? (
          <div className="text-center py-5 text-sm text-[var(--gray-500)]">
            No schedule entries. Click "Add Day / Slot" to build the daily audit programme.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs border-collapse" style={{ minWidth: 800 }}>
              <thead><tr>
                <th className="text-left px-3 py-2 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)] border-b-2 border-[var(--border-color)]">Day</th>
                <th className="text-left px-3 py-2 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)] border-b-2 border-[var(--border-color)]">Date</th>
                <th className="text-left px-3 py-2 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)] border-b-2 border-[var(--border-color)]">Time</th>
                <th className="text-left px-3 py-2 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)] border-b-2 border-[var(--border-color)]">Activity</th>
                <th className="text-left px-3 py-2 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)] border-b-2 border-[var(--border-color)]">Auditee</th>
                <th className="text-left px-3 py-2 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)] border-b-2 border-[var(--border-color)]">Auditor</th>
                <th className="text-left px-3 py-2 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)] border-b-2 border-[var(--border-color)]">Clause Ref</th>
                <th className="text-left px-3 py-2 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)] border-b-2 border-[var(--border-color)]"></th>
              </tr></thead>
              <tbody>
                {schedule.map((row, idx) => (
                  <tr key={idx}>
                    {['day', 'date', 'time', 'activity', 'auditee', 'auditor', 'clause'].map(f => (
                      <td key={f} className="px-3 py-2 border-b border-[var(--border-color)]">
                        <input className="w-full px-3 py-2.5 rounded-lg text-sm transition-colors border border-[var(--input-border)] bg-[var(--input-bg)] text-[var(--text-primary)] focus:outline-none focus:border-[var(--primary)] focus:ring-3 focus:ring-[rgba(0,61,122,0.1)]" style={{ width: f === 'day' ? 50 : f === 'date' ? 110 : f === 'time' ? 120 : f === 'clause' ? 80 : 100, padding: 4 }}
                          type={f === 'day' ? 'number' : f === 'date' ? 'date' : 'text'}
                          min={f === 'day' ? 1 : undefined}
                          value={row[f]} placeholder={f === 'time' ? '09:00 – 17:00' : f === 'activity' ? 'Activity description' : f === 'auditee' ? 'Department / person' : f === 'auditor' ? 'Auditor name' : f === 'clause' ? 'e.g. 4.1-5.3' : ''}
                          onChange={e => { const s = [...schedule]; s[idx] = { ...s[idx], [f]: e.target.value }; setSchedule(s) }} />
                      </td>
                    ))}
                    <td className="px-3 py-2 border-b border-[var(--border-color)]">
                      <button className="bg-red-600 text-white hover:bg-red-700 px-2.5 py-1 rounded-lg text-xs font-semibold inline-flex items-center justify-center border-none transition-all duration-150 cursor-pointer px-1.5 py-0.5 text-xs" onClick={() => removeScheduleRow(idx)}>✕</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="flex gap-3 items-center mb-5">
        <button className="bg-[var(--primary)] text-white hover:bg-[var(--primary-dark)] disabled:opacity-50 disabled:cursor-not-allowed px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center border-none transition-all duration-150 cursor-pointer whitespace-nowrap text-lg px-8 py-3" onClick={generate} disabled={generating}>
          {generating ? '⏳ Generating...' : '📄 Generate Audit Plan'}
        </button>
        {error && <span className="text-sm text-red-600">⚠ {error}</span>}
      </div>

      {result && (
        <div className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)] border-2 border-green-600 bg-green-50">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="m-0 mb-1 text-green-800">✅ Audit Plan Generated</h4>
              <p className="m-0 text-sm text-green-700">
                {result.filename} ({(result.size / 1024).toFixed(1)} KB)
              </p>
            </div>
            <a href={result.url} download={result.filename}
              className="bg-green-600 text-white hover:bg-green-700 px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center border-none transition-all duration-150 cursor-pointer no-underline">
              ⬇ Download Word Document
            </a>
          </div>
        </div>
      )}
    </div>
  )
}
