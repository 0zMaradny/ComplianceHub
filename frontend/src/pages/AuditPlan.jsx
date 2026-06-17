import { useState } from 'react'
import { useTranslation } from 'react-i18next'

export default function AuditPlanGenerator({ API }) {
  const { t } = useTranslation()
  const AUDIT_TYPES = [
    { value: 'stage1', label: t('audit_plan.stage1') },
    { value: 'stage2', label: t('audit_plan.stage2') },
    { value: 'surveillance', label: t('audit_plan.surveillance') },
    { value: 'recertification', label: t('audit_plan.recertification') },
    { value: 'transfer', label: t('audit_plan.transfer') },
  ]

  const ISO_STANDARDS_LIST = [
    { key: 'iso_9001', label: t('audit_plan.iso_9001') },
    { key: 'iso_14001', label: t('audit_plan.iso_14001') },
    { key: 'iso_45001', label: t('audit_plan.iso_45001') },
    { key: 'iso_27001', label: t('audit_plan.iso_27001') },
    { key: 'iso_50001', label: t('audit_plan.iso_50001') },
    { key: 'iso_20000', label: t('audit_plan.iso_20000') },
    { key: 'iso_22301', label: t('audit_plan.iso_22301') },
    { key: 'iso_37301', label: t('audit_plan.iso_37301') },
    { key: 'iso_42001', label: t('audit_plan.iso_42001') },
    { key: 'iso_27701', label: t('audit_plan.iso_27701') },
    { key: 'iso_31000', label: t('audit_plan.iso_31000') },
    { key: 'iso_30401', label: t('audit_plan.iso_30401') },
    { key: 'iso_10002', label: t('audit_plan.iso_10002') },
  ]

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
      setError(t('audit_plan.required_fields')); return
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
      <div className="page-header">
        <h2>{t('audit_plan.title')}</h2>
        <p>{t('audit_plan.subtitle')}</p>
      </div>

      <div className="card mb-5">
        <h3 className="card-header">{t('audit_plan.client_info')}</h3>
        <div className="card-body">
          <div className="grid grid-cols-2 gap-3">
            {[
              { label: t('audit_plan.client_name'), key: 'client_name', type: 'text', placeholder: t('audit_plan.org_name_placeholder') },
              { label: t('audit_plan.client_key'), key: 'client_key', type: 'text', placeholder: t('audit_plan.client_key_placeholder') },
              { label: t('audit_plan.audit_type'), key: 'audit_type', type: 'select', options: AUDIT_TYPES },
              { label: t('audit_plan.location'), key: 'location', type: 'text', placeholder: t('audit_plan.location_placeholder') },
              { label: t('audit_plan.start_date'), key: 'start_date', type: 'date' },
              { label: t('audit_plan.end_date'), key: 'end_date', type: 'date' },
            ].map(f => (
              <div key={f.key}>
                <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{f.label}</label>
                {f.type === 'select' ? (
                  <select className="input" value={form[f.key]} onChange={e => setForm({ ...form, [f.key]: e.target.value })}>
                    {f.options.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                  </select>
                ) : (
                  <input type={f.type} className="input" value={form[f.key]}
                    onChange={e => setForm({ ...form, [f.key]: e.target.value })}
                    placeholder={f.placeholder} />
                )}
              </div>
            ))}
          </div>
          <div className="mt-3">
            <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('audit_plan.standards')}</label>
            <div className="flex flex-wrap gap-1.5">
              {ISO_STANDARDS_LIST.map(std => {
                const selected = form.standards.includes(std.key)
                return (
                  <button key={std.key}
                    className={`${selected ? 'btn btn-primary' : 'btn btn-secondary'}`}
                    style={{ fontSize: 12, padding: '4px 10px' }}
                    onClick={() => setForm({ ...form, standards: selected ? form.standards.filter(s => s !== std.key) : [...form.standards, std.key] })}>
                    {std.label}
                  </button>
                )
              })}
            </div>
          </div>
        </div>
      </div>

      <div className="card mb-5">
        <h3 className="card-header">{t('audit_plan.audit_team')}</h3>
        <div className="card-body">
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('audit_plan.lead_auditor')}</label>
              <input className="input" value={form.lead_auditor}
                onChange={e => setForm({ ...form, lead_auditor: e.target.value })}
                placeholder={t('audit_plan.lead_auditor_placeholder')} />
            </div>
            <div className="col-span-2">
              <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('audit_plan.audit_team')}</label>
              <input className="input" value={form.audit_team}
                onChange={e => setForm({ ...form, audit_team: e.target.value })}
                placeholder={t('audit_plan.team_placeholder')} />
            </div>
          </div>
        </div>
      </div>

      <div className="card mb-5">
        <h3 className="card-header">{t('audit_plan.scope_language')}</h3>
        <div className="card-body">
          <div className="mb-3">
            <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('audit_plan.audit_scope')}</label>
            <textarea className="input" rows={3} value={form.audit_scope}
              onChange={e => setForm({ ...form, audit_scope: e.target.value })}
              placeholder={t('audit_plan.scope_placeholder')}
              style={{ resize: 'vertical' }} />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('audit_plan.language')}</label>
              <select className="input" value={form.audit_language}
                onChange={e => setForm({ ...form, audit_language: e.target.value })}>
                <option value="English">{t('audit_plan.english')}</option>
                <option value="Arabic">{t('audit_plan.arabic')}</option>
                <option value="English / Arabic">{t('audit_plan.english_arabic')}</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('audit_plan.report_due')}</label>
              <input type="number" className="input" min={1} max={90} value={form.report_due_days}
                onChange={e => setForm({ ...form, report_due_days: +e.target.value })} />
            </div>
          </div>
          <div className="mt-3">
            <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('audit_plan.additional_notes')}</label>
            <textarea className="input" rows={2} value={form.notes}
              onChange={e => setForm({ ...form, notes: e.target.value })}
              placeholder={t('audit_plan.notes_placeholder')}
              style={{ resize: 'vertical' }} />
          </div>
        </div>
      </div>

      <div className="card mb-5">
        <div className="card-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <h3 style={{ margin: 0, fontSize: 14, fontWeight: 600 }}>{t('audit_plan.daily_schedule')}</h3>
          <button className="btn btn-secondary" onClick={addScheduleRow}>{t('audit_plan.add_day')}</button>
        </div>
        <div className="card-body">
          {schedule.length === 0 ? (
            <div className="text-center py-5 text-sm text-[var(--gray-500)]">
              {t('audit_plan.no_schedule')}
            </div>
          ) : (
            <div className="table-container" style={{ overflowX: 'auto' }}>
              <table style={{ minWidth: 800 }}>
                <thead><tr>
                  <th className="text-left px-3 py-2 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)] border-b-2 border-[var(--border-color)]">{t('audit_plan.day')}</th>
                  <th className="text-left px-3 py-2 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)] border-b-2 border-[var(--border-color)]">{t('audit_plan.date')}</th>
                  <th className="text-left px-3 py-2 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)] border-b-2 border-[var(--border-color)]">{t('audit_plan.time')}</th>
                  <th className="text-left px-3 py-2 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)] border-b-2 border-[var(--border-color)]">{t('audit_plan.activity')}</th>
                  <th className="text-left px-3 py-2 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)] border-b-2 border-[var(--border-color)]">{t('audit_plan.auditee')}</th>
                  <th className="text-left px-3 py-2 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)] border-b-2 border-[var(--border-color)]">{t('audit_plan.auditor')}</th>
                  <th className="text-left px-3 py-2 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)] border-b-2 border-[var(--border-color)]">{t('audit_plan.clause_ref')}</th>
                  <th className="text-left px-3 py-2 font-semibold text-[10px] uppercase tracking-wider text-[var(--text-secondary)] border-b-2 border-[var(--border-color)]"></th>
                </tr></thead>
                <tbody>
                  {schedule.map((row, idx) => (
                    <tr key={idx}>
                      {['day', 'date', 'time', 'activity', 'auditee', 'auditor', 'clause'].map(f => (
                        <td key={f} className="px-3 py-2 border-b border-[var(--border-color)]">
                          <input className="input" style={{ width: f === 'day' ? 50 : f === 'date' ? 110 : f === 'time' ? 120 : f === 'clause' ? 80 : 100, height: 28, padding: '2px 6px', fontSize: 12 }}
                            type={f === 'day' ? 'number' : f === 'date' ? 'date' : 'text'}
                            min={f === 'day' ? 1 : undefined}
                            value={row[f]} placeholder={f === 'time' ? t('audit_plan.time_placeholder') : f === 'activity' ? t('audit_plan.activity_placeholder') : f === 'auditee' ? t('audit_plan.auditee_placeholder') : f === 'auditor' ? t('audit_plan.auditor_placeholder') : f === 'clause' ? t('audit_plan.clause_placeholder') : ''}
                            onChange={e => { const s = [...schedule]; s[idx] = { ...s[idx], [f]: e.target.value }; setSchedule(s) }} />
                        </td>
                      ))}
                      <td className="px-3 py-2 border-b border-[var(--border-color)]">
                        <button className="btn btn-danger" style={{ padding: '4px 8px', fontSize: 12 }} onClick={() => removeScheduleRow(idx)}>✕</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      <div className="flex gap-3 items-center mb-5">
        <button className="btn btn-primary" style={{ fontSize: 16, padding: '12px 32px' }} onClick={generate} disabled={generating}>
          {generating ? t('audit_plan.generating') : t('audit_plan.generate')}
        </button>
        {error && <span className="text-sm text-red-600">⚠ {error}</span>}
      </div>

      {result && (
        <div className="card mb-5" style={{ borderColor: 'var(--green-600)', borderWidth: 2, background: 'var(--green-50)' }}>
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="m-0 mb-1 text-green-800">{t('audit_plan.generated')}</h4>
                <p className="m-0 text-sm text-green-700">
                  {result.filename} ({(result.size / 1024).toFixed(1)} KB)
                </p>
              </div>
              <a href={result.url} download={result.filename} className="btn btn-primary">
                {t('audit_plan.download')}
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
