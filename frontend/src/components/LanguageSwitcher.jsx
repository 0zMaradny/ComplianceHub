import { useTranslation } from 'react-i18next'

export default function LanguageSwitcher() {
  const { i18n } = useTranslation()
  const current = i18n.language?.startsWith('ar') ? 'ar' : 'en'

  const toggle = () => {
    const next = current === 'ar' ? 'en' : 'ar'
    i18n.changeLanguage(next)
    localStorage.setItem('i18nextLng', next)
    document.documentElement.dir = next === 'ar' ? 'rtl' : 'ltr'
    document.documentElement.lang = next
  }

  return (
    <button
      onClick={toggle}
      aria-label={current === 'ar' ? 'Switch to English' : 'التبديل إلى العربية'}
      style={{
        display: 'flex', alignItems: 'center', gap: 6,
        padding: '6px 12px',
        fontSize: 13, fontWeight: 600,
        color: 'var(--sidebar-text)',
        background: 'rgba(255,255,255,0.08)',
        border: '1px solid rgba(255,255,255,0.1)',
        borderRadius: 8, cursor: 'pointer',
        transition: 'all 0.15s',
        lineHeight: 1,
      }}
      onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.15)' }}
      onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.08)' }}
    >
      <span style={{ fontSize: 16 }}>{current === 'ar' ? '🇬🇧' : '🇸🇦'}</span>
      {current === 'ar' ? 'EN' : 'AR'}
    </button>
  )
}
