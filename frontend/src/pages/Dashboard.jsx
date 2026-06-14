import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import Skeleton from '../components/Skeleton'

function formatDate(ts, t) {
  if (!ts) return '—'
  const d = new Date(ts * 1000)
  const now = new Date()
  const diff = (now - d) / 1000
  if (diff < 60) return t('dashboard.just_now')
  if (diff < 3600) return `${Math.floor(diff / 60)}${t('dashboard.m_ago')}`
  if (diff < 86400) return `${Math.floor(diff / 3600)}${t('dashboard.h_ago')}`
  return d.toLocaleDateString()
}

function getStandardsLabel(standards) {
  if (!standards) return '—'
  const arr = Array.isArray(standards) ? standards : [standards]
  return arr.map(s => s.replace('iso_', 'ISO ').replace('_', ':')).join(', ')
}

function healthColor(score) {
  if (score >= 85) return '#16a34a'
  if (score >= 60) return '#22c55e'
  if (score >= 40) return '#d97706'
  return '#dc2626'
}

function healthLabel(score, t) {
  if (score >= 85) return t('dashboard.excellent')
  if (score >= 60) return t('dashboard.good_label')
  if (score >= 40) return t('dashboard.at_risk')
  return t('dashboard.critical')
}

function RingGauge({ value, size = 140, strokeWidth = 10, color, label, sublabel }) {
  const r = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * r
  const offset = circumference - (Math.min(value, 100) / 100) * circumference

  return (
    <div className="flex flex-col items-center justify-center">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="var(--border-color)" strokeWidth={strokeWidth} />
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth={strokeWidth}
          strokeDasharray={circumference} strokeDashoffset={offset}
          strokeLinecap="round" transform={`rotate(-90 ${size/2} ${size/2})`}
          style={{ transition: 'stroke-dashoffset 1s cubic-bezier(0.4, 0, 0.2, 1)' }} />
        <text x={size/2} y={size/2 - 4} textAnchor="middle" dominantBaseline="central"
          fontSize="28" fontWeight="700" fill="var(--text-primary)">{value}%</text>
        <text x={size/2} y={size/2 + 18} textAnchor="middle" dominantBaseline="central"
          fontSize="11" fill="var(--text-secondary)">{label}</text>
      </svg>
      {sublabel && <div className="text-xs text-[var(--text-secondary)] mt-1">{sublabel}</div>}
    </div>
  )
}

function BarChart({ data, colors, labels, height = 120 }) {
  const { t } = useTranslation()
  const { months, ...series } = data
  if (!months || months.length === 0) return <div className="text-center py-12 text-[var(--text-secondary)]">{t('dashboard.no_trend_data')}</div>

  const allValues = Object.values(series).flat()
  const maxVal = Math.max(...allValues, 1)

  return (
    <div className="mt-3">
      <div className="flex items-end gap-1 px-1" style={{ height }}>
        {months.map((m, i) => {
          const stacked = Object.entries(series).map(([key, vals]) => ({ key, val: vals[i] || 0 }))
          return (
            <div key={m} className="flex-1 flex flex-col items-center gap-0.5">
              <div className="flex flex-col-reverse w-full items-center">
                {stacked.map(d => {
                  const h = d.val > 0 ? Math.max((d.val / maxVal) * (height - 20), 4) : 0
                  return h > 0 ? (
                    <div key={d.key} style={{ width: '80%', height: h, background: colors[d.key] || '#999', borderRadius: '2px 2px 0 0', minHeight: 2 }}
                      title={`${d.key}: ${d.val}`} />
                  ) : null
                })}
              </div>
              <span className="text-[9px] text-[var(--text-secondary)]" style={{ writingMode: 'vertical-rl', textOrientation: 'mixed', maxHeight: 40 }}>
                {m.slice(5)}
              </span>
            </div>
          )
        })}
      </div>
      <div className="flex gap-3 justify-center mt-2 flex-wrap">
        {Object.entries(colors).map(([key, color]) => (
          <div key={key} className="flex items-center gap-1 text-[11px]">
            <div className="w-2.5 h-2.5 rounded-[2px]" style={{ background: color }} />
            <span style={{ color: 'var(--text-secondary)' }}>{labels[key] || key}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function PieChart({ data, size = 100 }) {
  const { t } = useTranslation()
  const entries = Object.entries(data).filter(([, v]) => v > 0)
  const total = entries.reduce((s, [, v]) => s + v, 0)
  if (total === 0) return <div className="text-center py-12 text-[var(--text-secondary)]">{t('dashboard.no_data')}</div>

  const chartColors = ['var(--primary)', 'var(--accent)', 'var(--emerald)', 'var(--warm)', '#8E44AD', '#3498DB', '#E67E22', '#1ABC9C']
  let cumAngle = 0

  return (
    <div className="flex items-center gap-4 mt-2">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {entries.map(([key, val], i) => {
          const angle = (val / total) * 360
          const startAngle = cumAngle
          cumAngle += angle
          const startRad = (startAngle - 90) * Math.PI / 180
          const endRad = (cumAngle - 90) * Math.PI / 180
          const largeArc = angle > 180 ? 1 : 0
          const r = size / 2 - 4
          const cx = size / 2, cy = size / 2
          const x1 = cx + r * Math.cos(startRad), y1 = cy + r * Math.sin(startRad)
          const x2 = cx + r * Math.cos(endRad), y2 = cy + r * Math.sin(endRad)
          const d = `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2} Z`
          return <path key={key} d={d} fill={chartColors[i % chartColors.length]} opacity={0.85} />
        })}
        <circle cx={size/2} cy={size/2} r={size/4} fill="var(--bg-card)" />
        <text x={size/2} y={size/2} textAnchor="middle" dominantBaseline="central" fontSize="14" fontWeight="700" fill="var(--text-primary)">{total}</text>
      </svg>
      <div className="flex flex-col gap-1">
        {entries.map(([key, val], i) => (
          <div key={key} className="flex items-center gap-1.5 text-[11px]">
            <div className="w-2 h-2 rounded-[2px]" style={{ background: chartColors[i % chartColors.length] }} />
            <span style={{ color: 'var(--text-secondary)' }}>{key}: {val} ({Math.round(val/total*100)}%)</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function QuickAction({ icon, label, onClick, gradient }) {
  return (
    <button onClick={onClick}
      className="flex flex-col items-center justify-center gap-2 p-5 rounded-xl cursor-pointer border-0 transition-all duration-200"
      style={{
        background: gradient || 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        minWidth: 120,
      }}
      onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-3px)'; e.currentTarget.style.boxShadow = 'var(--shadow-lg)' }}
      onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'var(--shadow-sm)' }}>
      <div className="w-10 h-10 rounded-xl flex items-center justify-center"
        style={{ background: 'rgba(255,255,255,0.2)' }}>
        {icon}
      </div>
      <span className="text-xs font-semibold text-center leading-tight">{label}</span>
    </button>
  )
}

export default function Dashboard({ API, tunnelUrl, onCopyUrl, copied }) {
  const { t } = useTranslation()
  const [stats, setStats] = useState(null)
  const [recentJobs, setRecentJobs] = useState([])
  const [standards, setStandards] = useState(null)
  const [ncTrends, setNcTrends] = useState(null)
  const [projectHealth, setProjectHealth] = useState(null)
  const [aiUsage, setAiUsage] = useState(null)
  const [capaMetrics, setCapaMetrics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [tunnelRetrying, setTunnelRetrying] = useState(false)

  const retryTunnel = async () => {
    setTunnelRetrying(true)
    try {
      await fetch(`${API}/tunnel-retry`, { method: 'POST' })
    } catch (e) { console.warn('Tunnel retry failed:', e) }
    setTimeout(() => setTunnelRetrying(false), 5000)
  }

  useEffect(() => {
    Promise.all([
      fetch(`${API}/stats`).then(r => r.json()).catch(e => { console.error('Failed to fetch stats:', e); return {} }),
      fetch(`${API}/jobs?limit=5`).then(r => r.json()).catch(e => { console.error('Failed to fetch jobs:', e); return { jobs: [] } }),
      fetch(`${API}/standards`).then(r => r.json()).catch(e => { console.error('Failed to fetch standards:', e); return null }),
      fetch(`${API}/analytics/nc-trends?months=6`).then(r => r.json()).catch(e => { console.error('Failed to fetch NC trends:', e); return null }),
      fetch(`${API}/analytics/project-health`).then(r => r.json()).catch(e => { console.error('Failed to fetch project health:', e); return null }),
      fetch(`${API}/analytics/ai-usage`).then(r => r.json()).catch(e => { console.error('Failed to fetch AI usage:', e); return null }),
      fetch(`${API}/analytics/capa-metrics`).then(r => r.json()).catch(e => { console.error('Failed to fetch CAPA metrics:', e); return null }),
    ]).then(([s, j, st, trends, health, ai, capa]) => {
      setStats(s)
      setRecentJobs(j.jobs || [])
      setStandards(st?.standards ? Object.values(st.standards) : null)
      setNcTrends(trends)
      setProjectHealth(health)
      setAiUsage(ai)
      setCapaMetrics(capa)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [API])

  if (loading) return (
    <div className="animate-fadeIn">
      <div className="page-header"><Skeleton variant="title" width="200px" /><Skeleton variant="text" width="320px" className="mt-2" /></div>
      <div className="grid gap-4 mb-8 grid-cols-[repeat(auto-fit,minmax(160px,1fr))]">
        {[1,2,3,4].map(i => <Skeleton key={i} variant="stat-card" />)}
      </div>
      <div className="grid gap-5 mb-8 grid-cols-[repeat(auto-fit,minmax(200px,1fr))]">
        {[1,2,3,4,5].map(i => <Skeleton key={i} variant="stat-card" />)}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        <Skeleton variant="card" height="240px" />
        <Skeleton variant="card" height="240px" />
      </div>
      <Skeleton variant="card" height="160px" />
      <Skeleton variant="card" height="120px" />
    </div>
  )

  const successRate = stats?.success_rate ?? 0
  const openNcs = stats?.open_ncs ?? 0
  const pendingCapas = stats?.pending_capas ?? 0
  const healthScore = projectHealth?.overall_score ?? successRate

  const navigate = (page) => {
    window.dispatchEvent(new CustomEvent('navigate', { detail: page }))
  }

  return (
    <div className="animate-pageIn">
      <div className="page-header">
        <h2>{t('nav.dashboard')}</h2>
        <p>{t('dashboard.title')}</p>
      </div>

      {/* ── Hero area: ring gauge + quick actions ── */}
      <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-5 mb-6">
        <div className="stat-card flex flex-col items-center justify-center py-6">
          <RingGauge value={healthScore} size={150} strokeWidth={12}
            color={healthColor(healthScore)} label={healthLabel(healthScore, t)}
            sublabel={t('dashboard.overall_compliance')} />
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <QuickAction
            icon={<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
            </svg>}
            label={t('dashboard.new_audit')}
            gradient="linear-gradient(135deg, var(--primary) 0%, #0050A0 100%)"
            onClick={() => navigate('audit')} />
          <QuickAction
            icon={<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
            </svg>}
            label={t('dashboard.view_reports')}
            gradient="linear-gradient(135deg, var(--teal) 0%, #0F766E 100%)"
            onClick={() => navigate('history')} />
          <QuickAction
            icon={<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
            </svg>}
            label={t('dashboard.compliance')}
            gradient="linear-gradient(135deg, var(--warm) 0%, #B8860B 100%)"
            onClick={() => navigate('compliance')} />
          <QuickAction
            icon={<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>
            </svg>}
            label={t('dashboard.analytics')}
            gradient="linear-gradient(135deg, var(--purple) 0%, #6D28D9 100%)"
            onClick={() => navigate('analytics')} />
        </div>
      </div>

      {/* ── Tunnel URL banner ── */}
      {tunnelUrl ? (
        <div className="stat-card mb-6" style={{ background: 'linear-gradient(135deg, var(--bg-card) 0%, var(--primary-light) 100%)', border: '1px solid var(--border-color)' }}>
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div className="flex items-center gap-3">
              <div className="stat-card-icon" style={{ background: 'rgba(0,61,122,0.1)' }}>
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="var(--primary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/>
                  <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/>
                </svg>
              </div>
              <div>
                <div className="badge badge-success mb-1">{t('nav.live')}</div>
                <div className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{tunnelUrl}</div>
                <div className="stat-card-label">{t('nav.tunnel_url')}</div>
              </div>
            </div>
            <div className="flex gap-2">
              <button className="btn btn-secondary" onClick={onCopyUrl} style={{ fontSize: 12, padding: '8px 16px' }}>
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
                </svg>
                {copied ? t('nav.copied') : t('nav.copy')}
              </button>
              <button className="btn btn-secondary" onClick={retryTunnel} disabled={tunnelRetrying} style={{ fontSize: 12, padding: '8px 16px' }}>
                {tunnelRetrying ? t('audit.generating') : t('nav.reconnect')}
              </button>
              <a href={tunnelUrl} target="_blank" rel="noopener noreferrer" className="btn btn-primary" style={{ fontSize: 12, padding: '8px 16px' }}>
                {t('nav.open_new_tab')}
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
                </svg>
              </a>
            </div>
          </div>
        </div>
      ) : (
        <div className="stat-card mb-6" style={{ background: 'linear-gradient(135deg, #fef2f2 0%, #fff 100%)', border: '1px solid #fecaca' }}>
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div className="flex items-center gap-3">
              <div className="stat-card-icon" style={{ background: 'rgba(220,38,38,0.1)' }}>
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#dc2626" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/>
                  <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/>
                </svg>
              </div>
              <div>
                <div className="badge badge-error mb-1">{t('nav.disconnected')}</div>
                <div className="text-sm text-[var(--text-secondary)]">{t('nav.tunnel_offline')}</div>
              </div>
            </div>
            <button className="btn btn-primary" onClick={retryTunnel} disabled={tunnelRetrying} style={{ fontSize: 12, padding: '8px 16px' }}>
              {tunnelRetrying ? t('audit.generating') : t('nav.reconnect')}
            </button>
          </div>
        </div>
      )}

      {/* ── Stat cards ── */}
      <div className="grid gap-4 mb-8 grid-cols-[repeat(auto-fit,minmax(180px,1fr))]">
        <div className="stat-card">
          <div className="stat-card-icon" style={{ background: 'rgba(0,61,122,0.1)' }}>
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="var(--primary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/>
            </svg>
          </div>
          <div className="stat-card-value">{stats?.total_jobs ?? 0}</div>
          <div className="stat-card-label">{t('dashboard.total_jobs')}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-icon" style={{ background: successRate >= 80 ? 'rgba(22,163,74,0.12)' : successRate >= 50 ? 'rgba(217,119,6,0.12)' : 'rgba(220,38,38,0.12)' }}>
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke={successRate >= 80 ? '#16a34a' : successRate >= 50 ? '#d97706' : '#dc2626'} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
          </div>
          <div className="stat-card-value" style={{ color: successRate >= 80 ? 'var(--green-700)' : successRate >= 50 ? 'var(--amber-700)' : 'var(--red-700)' }}>{successRate}%</div>
          <div className="stat-card-label">{t('dashboard.success_rate')}</div>
          <div className={`stat-card-trend ${successRate >= 80 ? 'badge-success' : successRate >= 50 ? 'badge-warning' : 'badge-error'}`}>
            {successRate >= 80 ? t('dashboard.good') : successRate >= 50 ? t('dashboard.fair') : t('dashboard.low')}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-card-icon" style={{ background: openNcs > 0 ? 'rgba(225,29,72,0.1)' : 'rgba(22,163,74,0.1)' }}>
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke={openNcs > 0 ? 'var(--rose)' : '#16a34a'} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          </div>
          <div className="stat-card-value" style={{ color: openNcs > 0 ? 'var(--rose)' : undefined }}>{openNcs}</div>
          <div className="stat-card-label">{t('dashboard.open_ncs')}</div>
          {openNcs > 0 && <div className="stat-card-trend" style={{ background: 'var(--rose-light)', color: 'var(--rose)', borderRadius: 20, padding: '2px 8px', fontSize: 11, fontWeight: 600 }}>{t('dashboard.need_attention')}</div>}
        </div>
        <div className="stat-card">
          <div className="stat-card-icon" style={{ background: 'rgba(217,119,6,0.1)' }}>
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#d97706" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          </div>
          <div className="stat-card-value">{pendingCapas}</div>
          <div className="stat-card-label">{t('dashboard.pending_capas')}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-icon" style={{ background: 'rgba(0,61,122,0.1)' }}>
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="var(--primary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
            </svg>
          </div>
          <div className="stat-card-value">{capaMetrics?.avg_closure_days ?? '—'}<span style={{ fontSize: 14, fontWeight: 400, color: 'var(--text-secondary)' }}>d</span></div>
          <div className="stat-card-label">{t('dashboard.avg_capa_closure')}</div>
        </div>
      </div>

      {/* ── Charts grid ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-5">
        <div className="card">
          <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>{t('dashboard.nc_trends')}</span>
            <a href={`${API}/export/csv?dataset=nc_trends&months=6`} download="nc_trends.csv" className="btn btn-ghost" style={{ fontSize: 11, padding: '4px 10px' }}>{t('dashboard.csv')}</a>
          </div>
          <div className="card-body">
            {ncTrends ? (
              <BarChart
                data={ncTrends}
                colors={{ major_nc: 'var(--accent)', minor_nc: 'var(--warm)', ofi: '#3498DB', closed: 'var(--emerald)' }}
                labels={{ major_nc: t('dashboard.major_nc'), minor_nc: t('dashboard.minor_nc'), ofi: t('dashboard.ofi'), closed: t('dashboard.closed') }}
              />
            ) : <div className="text-center py-12 text-[var(--text-secondary)]">{t('dashboard.no_nc_data')}</div>}
          </div>
        </div>
        <div className="card">
          <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>{t('dashboard.ai_usage')}</span>
            <a href={`${API}/export/csv?dataset=ai_usage`} download="ai_usage.csv" className="btn btn-ghost" style={{ fontSize: 11, padding: '4px 10px' }}>{t('dashboard.csv')}</a>
          </div>
          <div className="card-body">
            {aiUsage?.by_provider && Object.keys(aiUsage.by_provider).length > 0 ? (
              <PieChart data={aiUsage.by_provider} />
            ) : <div className="text-center py-12 text-[var(--text-secondary)]">{t('dashboard.no_ai_data')}</div>}
            {aiUsage?.total_generations != null && (
              <div className="mt-2 text-xs text-[var(--text-secondary)]">
                {aiUsage.total_generations} {t('dashboard.generations')} · {aiUsage.cache_hit_rate ?? 0}{t('dashboard.cache_hit')}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── Project Health ── */}
      <div className="card mb-5">
        <div className="card-header">{t('dashboard.project_health')}</div>
        <div className="card-body">
          {projectHealth?.projects && projectHealth.projects.length > 0 ? (
            <div className="flex flex-col gap-2">
              {projectHealth.projects.map(p => (
                <div key={p.id} className="flex items-center gap-3 px-4 py-3 rounded-lg" style={{ background: 'var(--gray-50)' }}>
                  <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: healthColor(p.healthScore) }} />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold truncate">{p.title}</div>
                    <div className="text-xs text-[var(--text-secondary)]">
                      {p.client}{t('dashboard.health_separator')}{t('dashboard.gate')}{p.current_gate}{t('dashboard.health_separator')}{p.days_in_gate}{t('dashboard.d_in_gate')}
                    </div>
                  </div>
                  <div className="w-20 h-2 rounded-full overflow-hidden" style={{ background: 'var(--gray-200)' }}>
                    <div className="h-full rounded-full transition-[width] duration-500" style={{ width: `${p.healthScore}%`, background: healthColor(p.healthScore) }} />
                  </div>
                  <span className="text-xs font-semibold min-w-[80px] text-right" style={{ color: healthColor(p.healthScore) }}>
                    {p.healthScore}{t('dashboard.health_separator')}{healthLabel(p.healthScore, t)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-[var(--text-secondary)]">{t('dashboard.no_active_projects')}</div>
          )}
        </div>
      </div>

      {/* ── CAPA Metrics ── */}
      {capaMetrics && (
        <div className="grid gap-4 grid-cols-2 lg:grid-cols-4 mb-5">
          <div className="stat-card">
            <div className="stat-card-label">{t('dashboard.total_capas')}</div>
            <div className="stat-card-value">{capaMetrics.total_capas ?? 0}</div>
          </div>
          <div className="stat-card">
            <div className="stat-card-label">{t('dashboard.closure_rate')}</div>
            <div className="stat-card-value"><span style={{ color: 'var(--green-700)' }}>{capaMetrics.closure_rate_pct ?? 0}%</span></div>
          </div>
          <div className="stat-card">
            <div className="stat-card-label">{t('dashboard.avg_days')}</div>
            <div className="stat-card-value">{capaMetrics.avg_closure_days ?? '—'}</div>
          </div>
          <div className="stat-card">
            <div className="stat-card-label">{t('dashboard.overdue')}</div>
            <div className="stat-card-value" style={{ color: (capaMetrics.overdue_count ?? 0) > 0 ? 'var(--red-700)' : undefined }}>
              {capaMetrics.overdue_count ?? 0}
            </div>
          </div>
        </div>
      )}

      {/* ── Recent Jobs ── */}
      <div className="card mb-5">
        <div className="card-header">{t('dashboard.recent_jobs')}</div>
        <div className="card-body">
          {recentJobs.length > 0 ? recentJobs.map(j => (
            <div key={j.job_id} className="flex justify-between items-center py-2 text-sm border-b border-[var(--border-color)] last:border-b-0">
              <div className="flex-1 truncate font-medium">{getStandardsLabel(j.standards)}</div>
              <div className="flex items-center gap-3">
                <span className={`badge ${{uploaded:'badge-info',generating:'badge-warning',done:'badge-success',error:'badge-error'}[j.status] || 'badge-info'}`}>{j.status}</span>
                <span className="text-xs text-[var(--text-secondary)]">{formatDate(j.created_at, t)}</span>
              </div>
            </div>
          )) : (
            <div className="text-center py-8 text-[var(--text-secondary)]">{t('dashboard.no_jobs_yet')}</div>
          )}
          {recentJobs.length > 0 && (
            <a href="#history" onClick={e => { e.preventDefault(); navigate('history') }}
               className="inline-block mt-3 text-sm font-medium" style={{ color: 'var(--primary)' }}>
              {t('dashboard.view_all_jobs')}
            </a>
          )}
        </div>
      </div>

      {/* ── Standards ── */}
      <div className="card">
        <div className="card-header">{t('dashboard.supported_standards')}</div>
        <div className="card-body">
          <div className="grid gap-2 grid-cols-[repeat(auto-fill,minmax(280px,1fr))]">
            {(standards || []).map(s => {
              const key = (s || '').replace(/[^a-z0-9]/g, '').toLowerCase()
              const color = `var(--standard-${key})`
              return (
                <div key={s}
                  className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm border cursor-default transition-all"
                  style={{
                    borderColor: 'var(--border-color)',
                    borderLeft: `3px solid ${color}`,
                  }}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = color; e.currentTarget.style.background = 'var(--bg-card-hover)' }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border-color)'; e.currentTarget.style.background = 'transparent' }}>
                  {s}
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
