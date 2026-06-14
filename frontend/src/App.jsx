import { useState, useEffect, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import './App.css'
import { useToast } from './components/Toast'
import usePreferences from './hooks/usePreferences'
import useNotifications from './hooks/useNotifications'
import NotificationBell from './components/NotificationBell'
import PreferencesModal from './components/PreferencesModal'
import Dashboard from './pages/Dashboard'
import Audit from './pages/Audit'
import Compliance from './pages/Compliance'
import Projects from './pages/Projects'
import AuditProgram from './pages/AuditProgram'
import AuditPlan from './pages/AuditPlan'
import Templates from './pages/Templates'
import History from './pages/History'
import Analytics from './pages/Analytics'
import Surveillance from './pages/Surveillance'
import Chat from './pages/Chat'
import Reporting from './pages/Reporting'
import ErrorBoundary from './components/ErrorBoundary'
import { ToastProvider } from './components/Toast'
import LanguageSwitcher from './components/LanguageSwitcher'

const API = '/api'

const ICONS = {
  dashboard: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="7" rx="1"/>
      <rect x="14" y="3" width="7" height="4" rx="1"/>
      <rect x="14" y="10" width="7" height="11" rx="1"/>
      <rect x="3" y="13" width="7" height="8" rx="1"/>
    </svg>
  ),
  audit: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
      <line x1="16" y1="13" x2="8" y2="13"/>
      <line x1="16" y1="17" x2="8" y2="17"/>
    </svg>
  ),
  compliance: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
      <polyline points="22 4 12 14.01 9 11.01"/>
    </svg>
  ),
  sun: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
    </svg>
  ),
  moon: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>
    </svg>
  ),
  menu: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/>
    </svg>
  ),
  x: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
    </svg>
  ),
  history: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
    </svg>
  ),
  templates: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
      <line x1="16" y1="13" x2="8" y2="13"/>
      <line x1="16" y1="17" x2="8" y2="17"/>
    </svg>
  ),
  projects: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/>
    </svg>
  ),
  analytics: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>
    </svg>
  ),
  chat: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
      <line x1="10" y1="9" x2="16" y2="9"/>
      <line x1="11" y1="13" x2="15" y2="13"/>
    </svg>
  ),
  download: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
    </svg>
  ),
  link: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/>
      <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/>
    </svg>
  ),
  settings: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/>
    </svg>
  ),
  copy: (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
    </svg>
  ),
}

const PAGE_ORDER = ['dashboard','audit','history','compliance','audit_plan','audit_program','surveillance','templates','projects','analytics','chat','reporting']

const NAV_SECTIONS = [
  {
    labelKey: 'nav.main',
    items: [
      { id: 'dashboard', labelKey: 'nav.dashboard', icon: 'dashboard' },
      { id: 'audit', labelKey: 'nav.audit_generator', icon: 'audit' },
      { id: 'history', labelKey: 'nav.history', icon: 'history' },
    ],
  },
  {
    labelKey: 'nav.compliance_section',
    items: [
      { id: 'compliance', labelKey: 'nav.compliance', icon: 'compliance' },
      { id: 'audit_plan', labelKey: 'nav.audit_plan', icon: 'audit' },
      { id: 'audit_program', labelKey: 'nav.audit_execution', icon: 'projects' },
      { id: 'surveillance', labelKey: 'nav.surveillance', icon: 'templates' },
    ],
  },
  {
    labelKey: 'nav.tools',
    items: [
      { id: 'templates', labelKey: 'nav.templates', icon: 'templates' },
      { id: 'projects', labelKey: 'nav.projects', icon: 'projects' },
      { id: 'analytics', labelKey: 'nav.analytics', icon: 'analytics' },
      { id: 'chat', labelKey: 'nav.ai_chat', icon: 'chat' },
      { id: 'reporting', labelKey: 'nav.reporting', icon: 'download' },
    ],
  },
]

function PageTransition({ children, direction }) {
  const anim = direction > 0 ? 'animate-slideIn' : 'animate-fadeIn'
  return <div className={anim}>{children}</div>
}

function App() {
  const { t, i18n } = useTranslation()
  const [page, setPage] = useState('dashboard')
  const [prevPage, setPrevPage] = useState('dashboard')
  const [standards, setStandards] = useState(null)
  const [hasApiKeys, setHasApiKeys] = useState(false)
  const [tunnelUrl, setTunnelUrl] = useState('')
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light')
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [copied, setCopied] = useState(false)
  const [tunnelMode, setTunnelMode] = useState('auto')
  const [prefs, updatePref] = usePreferences()
  const [showPrefs, setShowPrefs] = useState(false)
  const { notifications, unreadCount, dismissNotification, clearAll, markAllRead } = useNotifications(API)

  useEffect(() => {
    const load = () => {
      fetch(`${API}/standards`)
        .then(r => r.json())
        .then(data => setStandards(data))
        .catch(() => {})
      fetch(`${API}/config`)
        .then(r => r.json())
        .then(data => {
          setHasApiKeys(data.has_api_keys)
          if (data.tunnel_url) setTunnelUrl(data.tunnel_url)
        })
        .catch(() => {})
      fetch(`${API}/tunnel`)
        .then(r => r.json())
        .then(data => {
          if (data.tunnel_mode) setTunnelMode(data.tunnel_mode)
          if (data.tunnel_url) setTunnelUrl(data.tunnel_url)
        })
        .catch(() => {})
    }
    load()
    const interval = setInterval(load, 30000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    document.documentElement.dir = i18n.language?.startsWith('ar') ? 'rtl' : 'ltr'
    localStorage.setItem('theme', theme)
  }, [theme, i18n.language])

  useEffect(() => {
    const handler = (e) => { setPrevPage(page); setPage(e.detail); setSidebarOpen(false) }
    window.addEventListener('navigate', handler)
    return () => window.removeEventListener('navigate', handler)
  }, [page])

  const { showToast } = useToast()

  useEffect(() => {
    let gPressed = false
    const handler = (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.contentEditable === 'true') return

      if (e.key === 'Escape') {
        window.dispatchEvent(new CustomEvent('key-escape'))
        return
      }

      if (e.ctrlKey && e.key === 'k') {
        e.preventDefault()
        window.dispatchEvent(new CustomEvent('key-search'))
        return
      }

      if (e.key === 'g' && !e.ctrlKey && !e.metaKey) {
        gPressed = true
        setTimeout(() => { gPressed = false }, 500)
        return
      }

      if (gPressed) {
        gPressed = false
        const map = { d: 'dashboard', a: 'audit', h: 'history', c: 'compliance', t: 'templates', p: 'projects', n: 'analytics', x: 'chat', r: 'reporting', s: 'surveillance', l: 'audit_plan', m: 'audit_program' }
        if (map[e.key]) {
          e.preventDefault()
          showToast(`Go to ${map[e.key]}`, 'info')
          window.dispatchEvent(new CustomEvent('navigate', { detail: map[e.key] }))
        }
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [showToast])

  const toggleTheme = () => setTheme(prev => prev === 'light' ? 'dark' : 'light')

  const copyUrl = useCallback(() => {
    if (tunnelUrl) {
      navigator.clipboard.writeText(tunnelUrl).then(() => {
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      })
    }
  }, [tunnelUrl])

  const renderPage = () => {
    const props = { API, key: page }
    switch (page) {
      case 'dashboard': return <Dashboard {...props} tunnelUrl={tunnelUrl} onCopyUrl={copyUrl} copied={copied} />
      case 'audit': return <Audit {...props} standards={standards} hasApiKeys={hasApiKeys} />
      case 'history': return <History {...props} />
      case 'compliance': return <Compliance {...props} />
      case 'templates': return <Templates {...props} />
      case 'projects': return <Projects {...props} />
      case 'audit_plan': return <AuditPlan {...props} />
      case 'audit_program': return <AuditProgram {...props} />
      case 'analytics': return <Analytics {...props} />
      case 'surveillance': return <Surveillance {...props} />
      case 'chat': return <Chat {...props} />
      case 'reporting': return <Reporting {...props} />
      default: return <Dashboard {...props} />
    }
  }

  return (
    <ToastProvider>
    <div className="app-layout">
      <button className="hamburger" onClick={() => setSidebarOpen(!sidebarOpen)} aria-label={t('app.menu')}>
        {sidebarOpen ? ICONS.x : ICONS.menu}
      </button>
      {sidebarOpen && <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />}

      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
          <div className="sidebar-header">
            <div className="sidebar-logo">
              <div className="sidebar-logo-icon">CH</div>
              <div>
                <div className="sidebar-logo-text">{t('app.name')}</div>
                <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.45)', marginTop: 1 }}>{t('app.subtitle')}</div>
              </div>
            </div>
          </div>

        <nav className="sidebar-nav">
          {NAV_SECTIONS.map(section => (
            <div key={section.labelKey}>
              <div className="sidebar-section-label">{t(section.labelKey)}</div>
              {section.items.map(item => (
                <button
                  key={item.id}
                  className={`nav-item ${page === item.id ? 'active' : ''}`}
                  onClick={() => { setPage(item.id); setSidebarOpen(false) }}
                >
                  <span className="nav-icon">{ICONS[item.icon]}</span>
                  {t(item.labelKey)}
                </button>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '0 16px 8px' }}>
            <LanguageSwitcher />
            <NotificationBell
              notifications={notifications} unreadCount={unreadCount}
              onDismiss={dismissNotification} onClearAll={clearAll} onMarkAllRead={markAllRead} />
            <button onClick={() => setShowPrefs(true)}
              className="nav-item" style={{ width: 32, height: 32, padding: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
              title={t('preferences.title')}>
              <span className="nav-icon">{ICONS.settings}</span>
            </button>
            {tunnelUrl ? (
              <div className="sidebar-url" style={{ display: 'flex', alignItems: 'center', gap: 6, flex: 1, overflow: 'hidden' }}>
                <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#4ade80', flexShrink: 0 }} />
                <a href={tunnelUrl} target="_blank" rel="noopener noreferrer" style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{tunnelUrl.replace(/^https?:\/\//, '')}</a>
              </div>
            ) : (
              <div className="sidebar-url" style={{ display: 'flex', alignItems: 'center', gap: 6, flex: 1, overflow: 'hidden' }}>
                <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#6b7280', flexShrink: 0 }} />
                <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)' }}>{t('nav.offline')}</span>
              </div>
            )}
          </div>
          <div style={{ padding: '0 16px 4px', display: 'flex', gap: 6, alignItems: 'center' }}>
            <span style={{
              fontSize: 10, fontWeight: 600, textTransform: 'uppercase',
              letterSpacing: '0.06em',
              color: tunnelUrl ? 'rgba(74,222,128,0.7)' : 'rgba(255,255,255,0.3)',
              background: tunnelUrl ? 'rgba(74,222,128,0.1)' : 'transparent',
              padding: '1px 6px', borderRadius: 4,
            }}>{tunnelMode}</span>
            <span style={{ fontSize: 10, color: 'rgba(255,255,255,0.3)' }}>
              {tunnelUrl ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          <button
            onClick={toggleTheme}
            style={{
              display: 'flex', alignItems: 'center', gap: 10,
              padding: '10px 16px', width: '100%', textAlign: 'left',
              fontSize: 13, fontWeight: 500,
              color: 'var(--sidebar-text)', background: 'transparent',
              border: 'none', borderRadius: 8, cursor: 'pointer',
              transition: 'all 0.15s',
            }}
            onMouseEnter={e => { e.currentTarget.style.background = 'var(--sidebar-bg-hover)'; e.currentTarget.style.color = 'var(--sidebar-text-active)' }}
            onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--sidebar-text)' }}
          >
            <span className="nav-icon">{theme === 'light' ? ICONS.moon : ICONS.sun}</span>
            {theme === 'light' ? t('nav.dark_mode') : t('nav.light_mode')}
          </button>
        </div>
      </aside>

      <main className="main-content">
        <ErrorBoundary>
          <PageTransition direction={PAGE_ORDER.indexOf(page) - PAGE_ORDER.indexOf(prevPage)}>{renderPage()}</PageTransition>
        </ErrorBoundary>
      </main>

      {showPrefs && (
        <PreferencesModal
          prefs={prefs}
          onUpdate={updatePref}
          onClose={() => setShowPrefs(false)}
          standards={standards?.standards}
        />
      )}
    </div>
    </ToastProvider>
  )
}

export default App
