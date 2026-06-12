import { useState, useEffect } from 'react'
import Skeleton from '../components/Skeleton'

const STATUS_ORDER = ['compliant', 'partial', 'non_compliant', 'na']
const STATUS_LABELS = { compliant: 'Compliant', partial: 'Partial', non_compliant: 'Non-Compliant', na: 'N/A' }
const STATUS_COLORS = {
  compliant: { bg: 'var(--green-50)', color: 'var(--green-600)' },
  partial: { bg: 'var(--amber-50)', color: 'var(--amber-600)' },
  non_compliant: { bg: 'var(--red-50)', color: 'var(--red-600)' },
  na: { bg: 'var(--gray-100)', color: 'var(--gray-500)' },
}

function loadLocal() {
  try { return JSON.parse(localStorage.getItem('compliance_assessments') || '{}') }
  catch { return {} }
}

function saveLocal(assessments) {
  localStorage.setItem('compliance_assessments', JSON.stringify(assessments))
}

async function loadServer(API, stdKey) {
  try {
    const r = await fetch(`${API}/compliance/assessment/${stdKey}`)
    if (!r.ok) return null
    const data = await r.json()
    return data.assessments || {}
  } catch { return null }
}

async function saveServer(API, stdKey, assessments) {
  try {
    await fetch(`${API}/compliance/assessment/${stdKey}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ assessments }),
    })
  } catch { /* server save failed, localStorage persisted as fallback */ }
}

export default function Compliance({ API }) {
  const [selected, setSelected] = useState(null)
  const [allStandards, setAllStandards] = useState([])
  const [clauses, setClauses] = useState([])
  const [annex, setAnnex] = useState({})
  const [loading, setLoading] = useState(false)
  const [assessments, setAssessments] = useState(loadLocal)
  const [serverLoaded, setServerLoaded] = useState(false)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    fetch(`${API}/standards`)
      .then(r => r.json())
      .then(data => {
        if (data?.standards) {
          const list = Object.entries(data.standards).map(([id, label]) => {
            const parts = label.split(' — ')
            return { id, label: parts[0] || label, desc: parts[1] || '' }
          })
          setAllStandards(list)
        }
      })
      .catch(() => {})
  }, [API])

  const stdKey = selected || '__empty__'

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      if (!selected) { setClauses([]); setAnnex({}); return }
      setLoading(true)

      const serverData = await loadServer(API, selected)
      if (!cancelled && serverData) {
        const merged = { ...loadLocal(), [selected]: serverData }
        saveLocal(merged)
        setAssessments(merged)
        setServerLoaded(true)
      } else if (!cancelled) {
        setAssessments(loadLocal())
      }

      try {
        const r = await fetch(`${API}/compliance/standards/${selected}/clauses`)
        if (!r.ok) throw new Error('Failed')
        const data = await r.json()
        if (!cancelled) { setClauses(data.clauses || []); setAnnex(data.annex_a || {}) }
      } catch {
        if (!cancelled) { setClauses([]); setAnnex({}) }
      }
      if (!cancelled) setLoading(false)
    }
    load()
    return () => { cancelled = true }
  }, [selected, API])

  const getStatus = (clauseId) => assessments[stdKey]?.[clauseId] || 'untouched'
  const setStatus = (clauseId, status) => {
    setAssessments(prev => {
      const next = { ...prev }
      const key = stdKey
      if (!next[key]) next[key] = {}
      if (status === 'untouched') delete next[key][clauseId]
      else next[key][clauseId] = status
      if (Object.keys(next[key]).length === 0) delete next[key]
      saveLocal(next)
      saveServer(API, selected, next[key] || {})
      return next
    })
  }

  const stdAssess = assessments[stdKey] || {}
  const assessed = Object.keys(stdAssess)
  const compliantCount = Object.values(stdAssess).filter(s => s === 'compliant').length
  const partialCount = Object.values(stdAssess).filter(s => s === 'partial').length
  const nonCompliantCount = Object.values(stdAssess).filter(s => s === 'non_compliant').length
  const totalClauses = clauses.length
  const scoredClauses = totalClauses > 0
    ? Math.round((compliantCount + partialCount * 0.5) / totalClauses * 100)
    : 0

  const visible = clauses.filter(c => {
    if (filter === 'all') return true
    if (filter === 'compliant') return getStatus(c.id) === 'compliant'
    if (filter === 'partial') return getStatus(c.id) === 'partial'
    if (filter === 'non_compliant') return getStatus(c.id) === 'non_compliant'
    if (filter === 'untouched') return getStatus(c.id) === 'untouched'
    return true
  })

  const annexKeys = typeof annex === 'object' && !Array.isArray(annex) ? Object.keys(annex) : []

  if (!selected) {
    return (
      <div className="animate-fadeIn">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-[var(--text-primary)] m-0">Compliance Assessment</h2>
          <p className="mt-1 text-[var(--text-secondary)]">Select a standard to begin clause-level compliance assessment</p>
        </div>
        <div className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)]">
          <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">ISO Standards</h3>
          <div className="grid gap-2 grid-cols-[repeat(auto-fill,minmax(280px,1fr))]">
            {allStandards.map(s => (
              <div key={s.id} className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs border border-[var(--border-color)] cursor-pointer hover:border-[var(--primary)] hover:bg-[var(--primary-light)] transition-all justify-between"
                   onClick={() => setSelected(s.id)}>
                <div>
                  <div className="font-semibold text-sm">{s.label}</div>
                  <div className="text-xs text-[var(--text-secondary)]">{s.desc}</div>
                </div>
                <span className="text-xl text-[var(--text-secondary)]">→</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  const currentStd = allStandards.find(s => s.id === selected)

  return (
    <div className="animate-fadeIn">
      <div className="mb-8 flex justify-between items-start">
        <div>
          <button className="bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200 dark:bg-gray-200 dark:text-gray-800 px-5 py-2.5 rounded-lg text-sm font-semibold inline-flex items-center justify-center transition-all duration-150 cursor-pointer whitespace-nowrap text-xs mb-2" onClick={() => setSelected(null)}>
            ← Back to Standards
          </button>
          <h2 className="text-3xl font-bold text-[var(--text-primary)] m-0">{currentStd?.label || selected}</h2>
          <p className="mt-1 text-[var(--text-secondary)]">{currentStd?.desc} — Clause-level compliance assessment</p>
        </div>
      </div>

      <div className="grid gap-5 mb-8 grid-cols-[repeat(auto-fit,minmax(220px,1fr))]">
        <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]">
          <h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">Compliance Score</h3>
          <div className={`text-3xl font-bold ${scoredClauses >= 80 ? 'text-green-600' : scoredClauses >= 50 ? 'text-amber-600' : 'text-red-600'}`}>
            {scoredClauses}%
          </div>
          <div className="text-xs mt-1 text-[var(--text-secondary)]">
            {compliantCount} compliant, {partialCount} partial, {nonCompliantCount} non-compliant
          </div>
        </div>
        <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]">
          <h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">Clauses</h3>
          <div className="text-3xl font-bold text-[var(--primary)]">{assessed.length}/{totalClauses}</div>
          <div className="text-xs mt-1 text-[var(--text-secondary)]">
            {totalClauses - assessed.length} remaining
          </div>
        </div>
        <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]">
          <h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">Non-Compliant</h3>
          <div className="text-3xl font-bold text-red-600">{nonCompliantCount}</div>
          {nonCompliantCount > 0 && (
            <div className="text-xs mt-1 text-red-600">
              Requires corrective action
            </div>
          )}
        </div>
        <div className="rounded-xl p-6 bg-[var(--bg-card)] border border-[var(--border-color)]">
          <h3 className="text-xs font-semibold uppercase tracking-wider mb-2 text-[var(--text-secondary)]">Progress Bar</h3>
          <div className="w-full h-2 rounded-full overflow-hidden mb-3 bg-gray-200 mt-2">
            <div className="h-full rounded-full transition-[width] duration-500 bg-[var(--primary)]" style={{
              width: `${scoredClauses}%`,
              background: scoredClauses >= 80 ? 'var(--green-600)' : scoredClauses >= 50 ? 'var(--amber-600)' : 'var(--red-600)',
            }} />
          </div>
        </div>
      </div>

      <div className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)]">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">Clause Checklist</h3>
          <div className="flex gap-2">
            {['all', 'compliant', 'partial', 'non_compliant', 'untouched'].map(f => (
              <button key={f} onClick={() => setFilter(f)}
                className={`${filter === f
                  ? 'bg-[var(--primary)] text-white hover:bg-[var(--primary-dark)] border-none'
                  : 'bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200 dark:bg-gray-200 dark:text-gray-800'}
                  px-2.5 py-1 rounded-md text-xs font-semibold inline-flex items-center justify-center transition-all duration-150 cursor-pointer whitespace-nowrap`}
                style={{ fontSize: 11, padding: '4px 8px' }}>
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="animate-fadeIn"><Skeleton variant="table-row" count={8} className="mb-2" /></div>
        ) : visible.length === 0 ? (
          <div className="text-center p-12 text-[var(--text-secondary)]">No clauses match the selected filter.</div>
        ) : (
          <div className="animate-slideIn">
            {visible.map(c => {
              const status = getStatus(c.id)
              return (
                <div key={c.id} className="border-b border-[var(--border-color)]" style={{
                  padding: 12,
                  background: status !== 'untouched' ? STATUS_COLORS[status]?.bg : 'transparent',
                  borderRadius: status !== 'untouched' ? 8 : 0,
                  marginBottom: status !== 'untouched' ? 4 : 0,
                }}>
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="font-semibold text-sm text-[var(--text-primary)]">
                        Clause {c.id}: {c.title}
                      </div>
                      {c.description && (
                        <div className="text-xs mt-1 text-[var(--text-secondary)]">
                          {c.description.substring(0, 200)}
                        </div>
                      )}
                    </div>
                    <div className="flex gap-1 ml-3 flex-wrap">
                      {STATUS_ORDER.map(s => (
                        <button key={s} onClick={() => setStatus(c.id, status === s ? 'untouched' : s)}
                          className="text-xs px-2.5 py-1 rounded-md font-semibold inline-flex items-center justify-center transition-all duration-150 cursor-pointer whitespace-nowrap"
                          style={{
                            fontSize: 10, padding: '3px 8px',
                            background: status === s ? STATUS_COLORS[s].bg : 'transparent',
                            color: status === s ? STATUS_COLORS[s].color : 'var(--text-secondary)',
                            border: `1px solid ${status === s ? STATUS_COLORS[s].color : 'var(--border-color)'}`,
                          }}>
                          {STATUS_LABELS[s]}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {annexKeys.length > 0 && (
        <div className="rounded-xl p-6 mb-5 bg-[var(--bg-card)] border border-[var(--border-color)]">
          <h3 className="text-base font-semibold mb-4 text-[var(--text-primary)] m-0">Annex A Controls</h3>
          <div className="text-sm mb-3 text-[var(--text-secondary)]">
            {selected === 'iso_27001' ? `${annexKeys.length} control themes from Annex A (93 controls)` :
             selected === 'iso_42001' ? `${annexKeys.length} control objectives from Annex A` :
             `${annexKeys.length} annex sections`}
          </div>
          <div className="grid gap-2 grid-cols-[repeat(auto-fill,minmax(280px,1fr))]">
            {annexKeys.map(key => (
              <div key={key} className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs border border-[var(--border-color)] cursor-default hover:border-[var(--primary)] hover:bg-[var(--primary-light)] transition-all">
                {key}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="text-center p-4 text-xs text-[var(--text-secondary)]">
        Assessment data synced to server (localStorage fallback).
      </div>
    </div>
  )
}
