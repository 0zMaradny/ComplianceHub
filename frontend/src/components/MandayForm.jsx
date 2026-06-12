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
    <div className="border border-[var(--border-color)] rounded-lg mt-3 bg-[var(--bg-secondary,#f9fafb)]">
      <div
        className="px-4 py-3 cursor-pointer flex items-center justify-between select-none"
        onClick={() => setExpanded(!expanded)}
      >
        <span className="font-semibold text-sm text-gray-800 dark:text-gray-200">
          {expanded ? '\u25BC' : '\u25B6'} Manday Calculation
        </span>
        {computed && (
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {computed.total_mandays} days | {auditType.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())} | {employeeCount} emp
          </span>
        )}
      </div>

      {expanded && (
        <div className="px-4 pb-4 border-t border-[var(--border-color)]">
          <div className="flex gap-4 mt-3 flex-wrap">
            <div className="flex-1 min-w-[150px]">
              <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Audit Type</label>
              <select
                value={auditType}
                onChange={e => setAuditType(e.target.value)}
                className="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-600 rounded text-sm bg-white dark:bg-gray-800"
              >
                {AUDIT_TYPES.map(t => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
            </div>
            <div className="flex-1 min-w-[150px]">
              <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Employees</label>
              <input
                type="number"
                value={employeeCount}
                onChange={e => setEmployeeCount(Number(e.target.value))}
                className="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-600 rounded text-sm bg-[var(--input-bg)] text-[var(--text-primary)] box-border"
                min={1}
              />
            </div>
            <div className="flex-1 min-w-[150px]">
              <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Sites</label>
              <input
                type="number"
                value={siteCount}
                onChange={e => setSiteCount(Number(e.target.value))}
                className="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-600 rounded text-sm bg-[var(--input-bg)] text-[var(--text-primary)] box-border"
                min={1}
              />
            </div>
          </div>

          {stdCount > 0 && (
            <div className="mt-3">
              <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Per-Standard Details</label>
              <table className="w-full border-collapse text-sm mt-1">
                <thead>
                  <tr>
                    <th className="text-left px-2 py-1.5 border-b-2 border-gray-200 dark:border-gray-700 text-xs font-semibold text-gray-600 dark:text-gray-400">Standard</th>
                    <th className="text-left px-2 py-1.5 border-b-2 border-gray-200 dark:border-gray-700 text-xs font-semibold text-gray-600 dark:text-gray-400">Risk / Complexity</th>
                    <th className="text-left px-2 py-1.5 border-b-2 border-gray-200 dark:border-gray-700 text-xs font-semibold text-gray-600 dark:text-gray-400">Base Mandays (from DOCX or table)</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedStandards.map(s => {
                    const label = standards?.[s]?.split(' \u2014 ')?.[0] || s
                    return (
                      <tr key={s}>
                        <td className="px-2 py-1 border-b border-gray-100 dark:border-gray-800">{label}</td>
                        <td className="px-2 py-1 border-b border-gray-100 dark:border-gray-800">
                          <select
                            value={riskCategories[s] || 'medium'}
                            onChange={e => setRiskCategories({ ...riskCategories, [s]: e.target.value })}
                            className="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-600 rounded text-sm bg-white dark:bg-gray-800"
                          >
                            {COMPLEXITY_LEVELS.map(c => (
                              <option key={c.value} value={c.value}>{c.label}</option>
                            ))}
                          </select>
                        </td>
                        <td className="px-2 py-1 border-b border-gray-100 dark:border-gray-800">
                          <input
                            type="number"
                            value={baseMandays[s] || ''}
                            onChange={e => setBaseMandays({ ...baseMandays, [s]: Number(e.target.value) || '' })}
                            className="w-20 px-2 py-1.5 border border-gray-300 dark:border-gray-600 rounded text-sm bg-[var(--input-bg)] text-[var(--text-primary)] box-border"
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
          <div className="flex gap-4 mt-3 flex-wrap">
            <div className="flex-1 min-w-[150px]">
                <label className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">IMS Reduction (IAF MD 11) %</label>
                <input
                  type="number"
                  value={imsReduction !== null ? Math.round(imsReduction * 100) : ''}
                  onChange={e => setImsReduction(e.target.value ? Number(e.target.value) / 100 : null)}
                  className="w-full px-2 py-1.5 border border-gray-300 dark:border-gray-600 rounded text-sm bg-[var(--input-bg)] text-[var(--text-primary)] box-border"
                  min={0}
                  max={20}
                  placeholder={`Auto (${(stdCount >= 2 ? 20 : 0)})`}
                />
              </div>
            </div>
          )}

          {computed && (
            <div className="mt-4 p-3 bg-green-50 dark:bg-green-900/20 rounded-md border border-green-200 dark:border-green-800">
              <div className="font-bold text-xs text-green-700 dark:text-green-400 mb-2">Calculated Mandays</div>
              <div className="flex flex-col gap-1.5">
                <div className="flex justify-between text-xs">
                  <span className="text-gray-600 dark:text-gray-400 font-medium">Total Mandays</span>
                  <span className="text-gray-800 dark:text-gray-200 font-semibold">{computed.total_mandays}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-600 dark:text-gray-400 font-medium">Per Standard</span>
                  <span className="text-gray-800 dark:text-gray-200 font-semibold">
                    {Object.entries(computed.mandays_per_standard).map(([k, v]) =>
                      `${k.replace('iso_', '').toUpperCase()}: ${v}`
                    ).join(', ')}
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-600 dark:text-gray-400 font-medium">Team</span>
                  <span className="text-gray-800 dark:text-gray-200 font-semibold">
                    {computed.team_composition.map(t => `${t.role} x${t.count} (${t.days}d)`).join(', ')}
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-gray-600 dark:text-gray-400 font-medium">Base</span>
                  <span className="text-gray-800 dark:text-gray-200 font-semibold">
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

