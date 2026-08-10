import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import en from './locales/en.json'
import ar from './locales/ar.json'

// Be defensive at module-evaluation time: the test environment may import
// this file before jsdom has finished installing `localStorage` / `navigator`,
// so guard every global read with a typeof check. In the browser these are
// always defined; in tests the stubs come from test-setup.js.
const safeStorage = (() => {
  try {
    return typeof localStorage !== 'undefined' ? localStorage : null
  } catch {
    return null
  }
})()
const safeNav = (() => {
  try {
    return typeof navigator !== 'undefined' ? navigator : { language: 'en-US' }
  } catch {
    return { language: 'en-US' }
  }
})()

const saved = safeStorage ? safeStorage.getItem('i18nextLng') : null
const detected = (safeNav.language || '').startsWith('ar') ? 'ar' : 'en'

i18n.use(initReactI18next).init({
  resources: { en: { translation: en }, ar: { translation: ar } },
  lng: saved || detected,
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
})

export default i18n
