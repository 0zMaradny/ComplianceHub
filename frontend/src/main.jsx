import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import './i18n'
import App from './App.jsx'

const saved = localStorage.getItem('i18nextLng')
if (saved?.startsWith('ar') || (!saved && navigator.language?.startsWith('ar'))) {
  document.documentElement.dir = 'rtl'
  document.documentElement.lang = 'ar'
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
