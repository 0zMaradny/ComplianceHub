import { useState } from 'react'
import { useTranslation } from 'react-i18next'

export default function PreferencesModal({ prefs, onUpdate, onClose, standards }) {
  const { t, i18n } = useTranslation()
  const [tab, setTab] = useState('general')

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/50 backdrop-blur-sm animate-fadeIn"
      onClick={onClose}>
      <div className="rounded-xl w-full max-w-lg max-h-[80vh] flex flex-col bg-[var(--bg-card)] shadow-xl animate-scaleIn"
        onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border-color)]">
          <h3 className="m-0 text-base font-semibold text-[var(--text-primary)]">{t('preferences.title')}</h3>
          <button className="w-8 h-8 flex items-center justify-center rounded-md cursor-pointer border-none bg-transparent text-[var(--text-secondary)] hover:bg-[var(--gray-100)]"
            onClick={onClose}>✕</button>
        </div>
        <div className="flex gap-0 border-b border-[var(--border-color)]">
          {['general', 'standards'].map(t => (
            <button key={t} onClick={() => setTab(t)}
              className={`flex-1 py-2.5 text-xs font-semibold cursor-pointer border-none bg-transparent transition-all ${
                tab === t ? 'text-[var(--primary)] border-b-2 border-[var(--primary)]' : 'text-[var(--text-secondary)]'
              }`}>
              {t(`preferences.${t}`)}
            </button>
          ))}
        </div>
        <div className="flex-1 overflow-y-auto p-6">
          {tab === 'general' && (
            <div className="flex flex-col gap-4">
              <div>
                <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('preferences.language')}</label>
                <select value={i18n.language} onChange={e => i18n.changeLanguage(e.target.value)}
                  className="input">
                  <option value="en">English</option>
                  <option value="ar">العربية</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('preferences.theme')}</label>
                <div className="flex gap-2">
                  {['light', 'dark'].map(t => (
                    <button key={t} onClick={() => onUpdate('theme', t)}
                      className={`flex-1 py-2.5 px-4 rounded-lg text-sm font-medium cursor-pointer border transition-all ${
                        prefs.theme === t
                          ? 'border-[var(--primary)] bg-[var(--primary-light)] text-[var(--primary)]'
                          : 'border-[var(--border-color)] bg-[var(--bg-card)] text-[var(--text-secondary)]'
                      }`}>
                      {t === 'light' ? '☀️ Light' : '🌙 Dark'}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
          {tab === 'standards' && standards && (
            <div>
              <label className="block text-xs font-semibold mb-1.5 text-[var(--text-secondary)]">{t('preferences.default_standards')}</label>
              <p className="text-xs mb-3 text-[var(--text-secondary)]">{t('preferences.default_standards_hint')}</p>
              <div className="grid gap-2 grid-cols-[repeat(auto-fill,minmax(220px,1fr))]">
                {Object.entries(standards).map(([id, label]) => {
                  const selected = (prefs.defaultStandards || []).includes(id)
                  return (
                    <div key={id}
                      className={`flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer text-sm border transition-all ${
                        selected ? 'border-[var(--primary)] bg-[var(--primary-light)]' : 'border-[var(--border-color)]'
                      }`}
                      onClick={() => {
                        const next = selected
                          ? (prefs.defaultStandards || []).filter(s => s !== id)
                          : [...(prefs.defaultStandards || []), id]
                        onUpdate('defaultStandards', next)
                      }}>
                      <input type="checkbox" className="w-4 h-4 accent-[var(--primary)]" checked={selected} onChange={() => {}} />
                      <span>{label}</span>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
