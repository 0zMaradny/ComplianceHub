import { useState, useCallback } from 'react'

const STORAGE_KEY = 'compliancehub-prefs'

const DEFAULTS = {
  defaultStandards: [],
  theme: 'light',
}

export default function usePreferences() {
  const [prefs, setPrefs] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      return stored ? { ...DEFAULTS, ...JSON.parse(stored) } : { ...DEFAULTS }
    } catch { /* localStorage unavailable */ return { ...DEFAULTS } }
  })

  const updatePref = useCallback((key, value) => {
    setPrefs(prev => {
      const next = { ...prev, [key]: value }
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(next)) } catch { /* localStorage full */ }
      return next
    })
  }, [])

  return [prefs, updatePref]
}
