const icons = {
  search: (
    <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
  ),
  file: (
    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
  ),
  folder: (
    <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z" />
  ),
  error: (
    <><circle cx="12" cy="12" r="10" /><line x1="15" y1="9" x2="9" y2="15" /><line x1="9" y1="9" x2="15" y2="15" /></>
  ),
  inbox: (
    <><polyline points="22 12 16 12 14 15 10 15 8 12 2 12" /><path d="M5.45 5.11L2 12v6a2 2 0 002 2h16a2 2 0 002-2v-6l-3.45-6.89A2 2 0 0016.76 4H7.24a2 2 0 00-1.79 1.11z" /></>
  ),
  chart: (
    <><line x1="18" y1="20" x2="18" y2="10" /><line x1="12" y1="20" x2="12" y2="4" /><line x1="6" y1="20" x2="6" y2="14" /></>
  ),
  history: (
    <><circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" /></>
  ),
  clipboard: (
    <><path d="M16 4h2a2 2 0 012 2v14a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 012-2h2" /><rect x="8" y="2" width="8" height="4" rx="1" ry="1" /></>
  ),
}

export default function EmptyState({ icon = 'inbox', title, description, action, compact }) {
  if (compact) {
    return (
      <div className="flex items-center justify-center gap-4 py-8 px-6 rounded-xl border border-dashed border-[var(--border-color)] bg-[var(--bg-card)]">
        <svg viewBox="0 0 24 24" width="36" height="36" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--gray-300)', flexShrink: 0 }}>
          {icons[icon] || icons.inbox}
        </svg>
        <div className="text-center">
          {title && <div className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>{title}</div>}
          {description && <div className="text-xs mt-1" style={{ color: 'var(--gray-400)' }}>{description}</div>}
          {action && (
            <button className="btn btn-primary mt-2" style={{ fontSize: 12, padding: '6px 14px' }} onClick={action.onClick}>
              {action.label}
            </button>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center justify-center py-12 px-6 text-center">
      <div className="w-20 h-20 rounded-full flex items-center justify-center mb-4"
        style={{ background: 'var(--primary-light)' }}>
        <svg viewBox="0 0 24 24" width="36" height="36" fill="none" stroke="var(--primary)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ opacity: 0.6 }}>
          {icons[icon] || icons.inbox}
        </svg>
      </div>
      {title && <h3 className="text-lg font-semibold m-0" style={{ color: 'var(--text-primary)' }}>{title}</h3>}
      {description && <p className="text-sm mt-1 mb-0" style={{ color: 'var(--text-secondary)', maxWidth: 400 }}>{description}</p>}
      {action && (
        <button className="btn btn-primary mt-4" onClick={action.onClick}>
          {action.label}
        </button>
      )}
    </div>
  )
}
