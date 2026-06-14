import { useState, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'

function formatTime(ts, t) {
  const diff = Math.floor((Date.now() - ts) / 1000)
  if (diff < 60) return t('dashboard.just_now')
  if (diff < 3600) return `${Math.floor(diff / 60)}${t('dashboard.m_ago')}`
  if (diff < 86400) return `${Math.floor(diff / 3600)}${t('dashboard.h_ago')}`
  return new Date(ts).toLocaleDateString()
}

export default function NotificationBell({ notifications, unreadCount, onDismiss, onClearAll, onMarkAllRead }) {
  const { t } = useTranslation()
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const navigate = (page) => {
    window.dispatchEvent(new CustomEvent('navigate', { detail: page }))
    setOpen(false)
  }

  return (
    <div ref={ref} style={{ position: 'relative' }}>
      <button onClick={() => { setOpen(!open); if (!open && unreadCount > 0) onMarkAllRead() }}
        style={{
          background: 'transparent', border: 'none', cursor: 'pointer',
          width: 32, height: 32, display: 'flex', alignItems: 'center', justifyContent: 'center',
          borderRadius: 8, color: 'var(--sidebar-text)', position: 'relative',
        }}
        onMouseEnter={e => { e.currentTarget.style.background = 'var(--sidebar-bg-hover)'; e.currentTarget.style.color = 'var(--sidebar-text-active)' }}
        onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--sidebar-text)' }}>
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/>
        </svg>
        {unreadCount > 0 && (
          <span style={{
            position: 'absolute', top: 2, right: 2,
            width: 16, height: 16, borderRadius: '50%',
            background: 'var(--accent)', color: '#fff',
            fontSize: 9, fontWeight: 700,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            lineHeight: 1,
          }}>{unreadCount > 9 ? '9+' : unreadCount}</span>
        )}
      </button>

      {open && (
        <div style={{
          position: 'absolute', left: 0, bottom: '100%', marginBottom: 8,
          width: 280, maxHeight: 320, overflowY: 'auto',
          background: 'var(--bg-card)', borderRadius: 12,
          boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
          border: '1px solid var(--border-color)',
          zIndex: 100,
        }}>
          <div style={{ padding: '10px 14px', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="text-xs font-semibold" style={{ color: 'var(--text-primary)' }}>{t('notifications.title')}</span>
            {notifications.length > 0 && (
              <button onClick={onClearAll} style={{ fontSize: 11, color: 'var(--text-secondary)', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>
                {t('notifications.clear_all')}
              </button>
            )}
          </div>
          {notifications.length === 0 ? (
            <div className="text-sm text-center py-8" style={{ color: 'var(--text-secondary)' }}>{t('notifications.empty')}</div>
          ) : (
            notifications.map(n => (
              <div key={n.id} onClick={() => { onDismiss(n.id); navigate('history') }}
                style={{
                  padding: '10px 14px', cursor: 'pointer',
                  borderBottom: '1px solid var(--border-color)',
                  background: n.read ? 'transparent' : 'var(--primary-light)',
                  transition: 'background 0.15s',
                }}
                onMouseEnter={e => { e.currentTarget.style.background = 'var(--bg-card-hover)' }}
                onMouseLeave={e => { e.currentTarget.style.background = n.read ? 'transparent' : 'var(--primary-light)' }}>
                <div className="flex items-center gap-1.5 mb-0.5">
                  <span style={{
                    width: 6, height: 6, borderRadius: '50%',
                    background: n.status === 'done' ? 'var(--green-600)' : 'var(--red-600)',
                    flexShrink: 0
                  }} />
                  <span className="text-xs font-medium" style={{ color: 'var(--text-primary)' }}>
                    {n.status === 'done' ? t('notifications.job_done') : t('notifications.job_error')}
                  </span>
                </div>
                {n.standards.length > 0 && (
                  <div className="text-xs ml-2.5" style={{ color: 'var(--text-secondary)' }}>
                    {n.standards.map(s => s.replace('iso_', 'ISO ').replace('_', ':')).join(', ')}
                  </div>
                )}
                <div className="text-xs ml-2.5 mt-0.5" style={{ color: 'var(--gray-400)' }}>{formatTime(n.timestamp, t)}</div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}
