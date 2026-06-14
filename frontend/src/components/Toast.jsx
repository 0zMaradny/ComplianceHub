import { useState, useCallback, useEffect, useRef } from 'react'
import { ToastContext } from '../hooks/useToast'

function ToastItem({ toast, onRemove }) {
  const barRef = useRef(null)

  useEffect(() => {
    if (barRef.current) {
      barRef.current.style.animationDuration = toast.duration + 'ms'
    }
    const timer = setTimeout(() => onRemove(toast.id), toast.duration)
    return () => clearTimeout(timer)
  }, [toast, onRemove])

  const icons = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' }

  return (
    <div className={`toast toast-${toast.type}`} onClick={() => onRemove(toast.id)}>
      <span className="toast-icon">{icons[toast.type] || 'ℹ'}</span>
      <span className="toast-message">{toast.message}</span>
      <div ref={barRef} className="toast-bar" />
    </div>
  )
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const showToast = useCallback((message, type = 'info', duration = 4000) => {
    const id = Date.now() + Math.random()
    setToasts(prev => [...prev, { id, message, type, duration }])
  }, [])

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  return (
    <ToastContext.Provider value={showToast}>
      {children}
      <div className="toast-container">
        {toasts.map(t => (
          <ToastItem key={t.id} toast={t} onRemove={removeToast} />
        ))}
      </div>
    </ToastContext.Provider>
  )
}
