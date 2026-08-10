// Vitest setup — runs before every test file.
//
// Order matters: the global mocks must be installed before any application
// module is imported, because `src/i18n.js` reads `localStorage` and
// `navigator` at module-evaluation time.
//
// We use jsdom as the test environment (configured in vite.config.js), which
// already provides `window`, `localStorage`, and `navigator`. But vitest's
// jsdom environment is initialized lazily — if a test file imports
// `./i18n` (directly or via a component) before the environment is fully
// ready, those globals can be undefined.
//
// The safe pattern: explicitly install a minimal storage stub on `globalThis`
// before any application import.

if (typeof globalThis.localStorage === 'undefined') {
  const store = new Map()
  globalThis.localStorage = {
    getItem: (key) => (store.has(key) ? store.get(key) : null),
    setItem: (key, value) => store.set(String(key), String(value)),
    removeItem: (key) => store.delete(key),
    clear: () => store.clear(),
    key: (index) => Array.from(store.keys())[index] ?? null,
    get length() { return store.size },
  }
}

if (typeof globalThis.navigator === 'undefined') {
  globalThis.navigator = { language: 'en-US', languages: ['en-US'] }
}

if (typeof globalThis.matchMedia === 'undefined') {
  globalThis.matchMedia = (query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {}, removeListener: () => {},
    addEventListener: () => {}, removeEventListener: () => {},
    dispatchEvent: () => false,
  })
}

import '@testing-library/jest-dom'
import './i18n'
