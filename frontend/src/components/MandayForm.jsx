import { useState, useMemo } from 'react'

const AUDIT_TYPES = [
  { value: 'initial', label: 'Initial Certification' },
  { value: 'surveillance_1', label: 'Surveillance 1' },
  { value: 'surveillance_2', label: 'Surveillance 2' },
  { value: 'recertification', label: 'Recertification' },
  { value: 'transfer', label: 'Transfer' },
]

const COMPLEXITY_LEVELS = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
]

function roundHalf(v) {
  return Math.round(v * 2) / 2
}

function computeMandays(auditType, employeeCount, siteCount, riskCategories, baseMandays, imsReduction, selectedStandards) {
  if (!selectedStandards.length) return null

  const bm = {}
  let hasDocxBase = false
  selectedStandards.forEach(s => {
    const v = baseMandays[s]
    if (v && v > 0) {
      bm[s] = Number(v)
      hasDocxBase = true
    }
  })

  const totalBase = hasDocxBase
    ? Object.values(bm).reduce((a, b) => a + b, 0)
    : selectedStandards.length * 4

  const imsPct = imsReduction !== null && imsReduction !== ''
    ? Number(imsReduction)
    : (selectedStandards.length >= 2 ? 0.2 : 0)

  const afterIms = totalBase * (1 - Math.min(imsPct, 0.2))
  const mult = auditType === 'initial' ? 1.0
    : auditType === 'surveillance_1' || auditType === 'surveillance_2' ? 1 / 3
    : auditType === 'recertification' || auditType === 'transfer' ? 2 / 3
    : 1.0

  const total = Math.max(roundHalf(afterIms * mult * siteCount), 1.0)

  const perStandard = {}
  if (totalBase > 0) {
    selectedStandards.forEach(s => {
      const base = hasDocxBase ? (bm[s] || 0) : (totalBase / selectedStandards.length)
      perStandard[s] = roundHalf((base / totalBase) * total)
    })
  }

  const team = total <= 1.5
    ? [{ role: 'Lead Auditor', count: 1, days: total }]
    : total <= 4
      ? [{ role: 'Lead Auditor', count: 1, days: roundHalf(total * 0.6) },
         { role: 'Auditor', count: 1, days: roundHalf(total * 0.4) }]
      : total <= 8
        ? [{ role: 'Lead Auditor', count: 1, days: roundHalf(total * 0.4) },
           { role: 'Auditor', count: 2, days: roundHalf(total * 0.3) }]
        : [{ role: 'Lead Auditor', count: 1, days: roundHalf(total * 0.3) },
           { role: 'Auditor', count: 2, days: roundHalf(total * 0.35) }]

  return {
    audit_type: auditType,
    employee_count: Number(employeeCount),
    site_count: Number(siteCount),
    risk_categories: riskCategories,
    base_mandays_from_docx: bm,
    ims_reduction: imsPct,
    total_mandays: total,
    mandays_per_standard: perStandard,
    team_composition: team,
  }
}

export default function MandayForm({
  standards,
  selectedStandards,
  mandayExtracted,
  onMandayConfigChange,
}) {
  const [expanded, setExpanded] = useState(false)
  const [auditType, setAuditType] = useState(
    () => mandayExtracted?.audit_type || 'initial'
  )
  const [employeeCount, setEmployeeCount] = useState(
    () => mandayExtracted?.employee_count || 50
  )
  const [siteCount, setSiteCount] = useState(1)
  const [riskCategories, setRiskCategories] = useState({})
  const [baseMandays, setBaseMandays] = useState({})
  const [imsReduction, setImsReduction] = useState(
    () => mandayExtracted?.ims_reduction_pct != null
      ? mandayExtracted.ims_reduction_pct / 100
      : null
  )

  const stdKey = selectedStandards.join(',')
  const result = useMemo(() => {
    const r = { ...riskCategories }
    const b = { ...baseMandays }
    let changed = false
    selectedStandards.forEach(s => {
      if (!(s in r)) { r[s] = 'medium'; changed = true }
      if (!(s in b)) { b[s] = ''; changed = true }
    })
    return changed ? { riskCategories: r, baseMandays: b } : null
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stdKey, riskCategories, baseMandays])

  if (result) {
    if (result.riskCategories !== riskCategories) setRiskCategories(result.riskCategories)
    if (result.baseMandays !== baseMandays) setBaseMandays(result.baseMandays)
  }

  const computed = useMemo(() => computeMandays(
    auditType, employeeCount, siteCount, riskCategories, baseMandays, imsReduction, selectedStandards
  ), [auditType, employeeCount, siteCount, riskCategories, baseMandays, imsReduction, selectedStandards])

  if (computed && onMandayConfigChange) {
    onMandayConfigChange(computed)
  }

  const stdCount = selectedStandards.length

  return (
    <div className="manday-form" style={styles.container}>
      <div
        style={styles.header}
        onClick={() => setExpanded(!expanded)}
      >
        <span style={styles.title}>
          {expanded ? '\u25BC' : '\u25B6'} Manday Calculation
        </span>
        {computed && (
          <span style={styles.summary}>
            {computed.total_mandays} days | {auditType.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())} | {employeeCount} emp
          </span>
        )}
      </div>

      {expanded && (
        <div style={styles.body}>
          <div style={styles.row}>
            <div style={styles.field}>
              <label style={styles.label}>Audit Type</label>
              <select
                value={auditType}
                onChange={e => setAuditType(e.target.value)}
                style={styles.select}
              >
                {AUDIT_TYPES.map(t => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
            </div>
            <div style={styles.field}>
              <label style={styles.label}>Employees</label>
              <input
                type="number"
                value={employeeCount}
                onChange={e => setEmployeeCount(Number(e.target.value))}
                style={styles.input}
                min={1}
              />
            </div>
            <div style={styles.field}>
              <label style={styles.label}>Sites</label>
              <input
                type="number"
                value={siteCount}
                onChange={e => setSiteCount(Number(e.target.value))}
                style={styles.input}
                min={1}
              />
            </div>
          </div>

          {stdCount > 0 && (
            <div style={styles.section}>
              <label style={styles.label}>Per-Standard Details</label>
              <table style={styles.table}>
                <thead>
                  <tr>
                    <th style={styles.th}>Standard</th>
                    <th style={styles.th}>Risk / Complexity</th>
                    <th style={styles.th}>Base Mandays (from DOCX or table)</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedStandards.map(s => {
                    const label = standards?.[s]?.split(' \u2014 ')?.[0] || s
                    return (
                      <tr key={s}>
                        <td style={styles.td}>{label}</td>
                        <td style={styles.td}>
                          <select
                            value={riskCategories[s] || 'medium'}
                            onChange={e => setRiskCategories({ ...riskCategories, [s]: e.target.value })}
                            style={styles.select}
                          >
                            {COMPLEXITY_LEVELS.map(c => (
                              <option key={c.value} value={c.value}>{c.label}</option>
                            ))}
                          </select>
                        </td>
                        <td style={styles.td}>
                          <input
                            type="number"
                            value={baseMandays[s] || ''}
                            onChange={e => setBaseMandays({ ...baseMandays, [s]: Number(e.target.value) || '' })}
                            style={{ ...styles.input, width: '80px' }}
                            min={0}
                            step={0.5}
                            placeholder="Auto"
                          />
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}

          {stdCount >= 2 && (
            <div style={styles.row}>
              <div style={styles.field}>
                <label style={styles.label}>IMS Reduction (IAF MD 11) %</label>
                <input
                  type="number"
                  value={imsReduction !== null ? Math.round(imsReduction * 100) : ''}
                  onChange={e => setImsReduction(e.target.value ? Number(e.target.value) / 100 : null)}
                  style={styles.input}
                  min={0}
                  max={20}
                  placeholder={`Auto (${(stdCount >= 2 ? 20 : 0)})`}
                />
              </div>
            </div>
          )}

          {computed && (
            <div style={styles.result}>
              <div style={styles.resultTitle}>Calculated Mandays</div>
              <div style={styles.resultGrid}>
                <div style={styles.resultItem}>
                  <span style={styles.resultLabel}>Total Mandays</span>
                  <span style={styles.resultValue}>{computed.total_mandays}</span>
                </div>
                <div style={styles.resultItem}>
                  <span style={styles.resultLabel}>Per Standard</span>
                  <span style={styles.resultValue}>
                    {Object.entries(computed.mandays_per_standard).map(([k, v]) =>
                      `${k.replace('iso_', '').toUpperCase()}: ${v}`
                    ).join(', ')}
                  </span>
                </div>
                <div style={styles.resultItem}>
                  <span style={styles.resultLabel}>Team</span>
                  <span style={styles.resultValue}>
                    {computed.team_composition.map(t => `${t.role} x${t.count} (${t.days}d)`).join(', ')}
                  </span>
                </div>
                <div style={styles.resultItem}>
                  <span style={styles.resultLabel}>Base</span>
                  <span style={styles.resultValue}>
                    {selectedStandards.map(s => {
                      const b = baseMandays[s]
                      return `${s.replace('iso_', '').toUpperCase()}: ${b || 'auto'}`
                    }).join(', ')}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

const styles = {
  container: {
    border: '1px solid #e0e0e0',
    borderRadius: '8px',
    marginTop: '12px',
    background: '#f9fafb',
  },
  header: {
    padding: '12px 16px',
    cursor: 'pointer',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    userSelect: 'none',
  },
  title: {
    fontWeight: 600,
    fontSize: '14px',
    color: '#333',
  },
  summary: {
    fontSize: '12px',
    color: '#666',
  },
  body: {
    padding: '0 16px 16px',
    borderTop: '1px solid #e0e0e0',
  },
  row: {
    display: 'flex',
    gap: '16px',
    marginTop: '12px',
    flexWrap: 'wrap',
  },
  field: {
    flex: '1',
    minWidth: '150px',
  },
  label: {
    display: 'block',
    fontSize: '12px',
    fontWeight: 600,
    color: '#555',
    marginBottom: '4px',
  },
  input: {
    width: '100%',
    padding: '6px 8px',
    border: '1px solid #ccc',
    borderRadius: '4px',
    fontSize: '13px',
    boxSizing: 'border-box',
  },
  select: {
    width: '100%',
    padding: '6px 8px',
    border: '1px solid #ccc',
    borderRadius: '4px',
    fontSize: '13px',
    background: '#fff',
  },
  section: {
    marginTop: '12px',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: '13px',
    marginTop: '4px',
  },
  th: {
    textAlign: 'left',
    padding: '6px 8px',
    borderBottom: '2px solid #e0e0e0',
    fontSize: '12px',
    fontWeight: 600,
    color: '#555',
  },
  td: {
    padding: '4px 8px',
    borderBottom: '1px solid #eee',
  },
  result: {
    marginTop: '16px',
    padding: '12px',
    background: '#e8f4e8',
    borderRadius: '6px',
    border: '1px solid #c8e6c9',
  },
  resultTitle: {
    fontWeight: 700,
    fontSize: '13px',
    color: '#2e7d32',
    marginBottom: '8px',
  },
  resultGrid: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  resultItem: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '13px',
  },
  resultLabel: {
    color: '#555',
    fontWeight: 500,
  },
  resultValue: {
    color: '#333',
    fontWeight: 600,
  },
}
