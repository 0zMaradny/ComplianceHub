import { useState, useEffect } from 'react'
import './App.css'
import Dashboard from './pages/Dashboard'
import Audit from './pages/Audit'
import Compliance from './pages/Compliance'
import Projects from './pages/Projects'
import ErrorBoundary from './components/ErrorBoundary'

const API = '/api'

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'audit', label: 'Audit Generator', icon: '📄' },
  { id: 'compliance', label: 'Compliance', icon: '✓' },
  { id: 'projects', label: 'Projects', icon: '📋' },
]

function App() {
  const [page, setPage] = useState('dashboard')
  const [standards, setStandards] = useState(null)

  useEffect(() => {
    fetch(`${API}/standards`)
      .then(r => r.json())
      .then(data => setStandards(data))
      .catch(() => {})
  }, [])

  useEffect(() => {
    const handler = (e) => setPage(e.detail)
    window.addEventListener('navigate', handler)
    return () => window.removeEventListener('navigate', handler)
  }, [])

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1>ComplianceHub</h1>
          <span>Audit & Compliance Platform</span>
        </div>
        <nav className="sidebar-nav">
          {NAV_ITEMS.map(item => (
            <button
              key={item.id}
              className={`nav-item ${page === item.id ? 'active' : ''}`}
              onClick={() => setPage(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>
      </aside>
      <main className="main-content">
        <ErrorBoundary>
          {page === 'dashboard' && <Dashboard API={API} />}
          {page === 'audit' && <Audit API={API} standards={standards} />}
          {page === 'compliance' && <Compliance API={API} />}
          {page === 'projects' && <Projects API={API} />}
        </ErrorBoundary>
      </main>
    </div>
  )
}

export default App
