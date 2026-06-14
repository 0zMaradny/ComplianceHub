import { useState, useEffect, useCallback, useRef } from 'react'

const STORAGE_KEY = 'compliancehub-notifications'

export default function useNotifications(API) {
  const [notifications, setNotifications] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      return stored ? JSON.parse(stored) : []
    } catch { return [] }
  })
  const lastCheck = useRef(null)
  const intervalRef = useRef(null)

  useEffect(() => { lastCheck.current = Date.now() }, [])

  const addNotification = useCallback((n) => {
    setNotifications(prev => {
      const next = [n, ...prev].slice(0, 20)
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(next)) } catch { /* localStorage full */ }
      return next
    })
  }, [])

  const dismissNotification = useCallback((id) => {
    setNotifications(prev => {
      const next = prev.filter(n => n.id !== id)
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(next)) } catch { /* localStorage full */ }
      return next
    })
  }, [])

  const clearAll = useCallback(() => {
    setNotifications([])
    try { localStorage.setItem(STORAGE_KEY, '[]') } catch { /* localStorage full */ }
  }, [])

  const unreadCount = notifications.filter(n => !n.read).length

  const markAllRead = useCallback(() => {
    setNotifications(prev => {
      const next = prev.map(n => ({ ...n, read: true }))
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(next)) } catch { /* localStorage full */ }
      return next
    })
  }, [])

  useEffect(() => {
    const handler = (e) => {
      const { jobId, standards, status } = e.detail
      if (status === 'done' || status === 'error') {
        addNotification({
          id: jobId + '-' + Date.now(),
          jobId,
          standards: standards || [],
          status,
          timestamp: Date.now(),
          read: false,
        })
      }
    }
    window.addEventListener('job-complete', handler)

    // Poll for recent completed jobs every 30s
    const poll = async () => {
      try {
        const res = await fetch(`${API}/jobs?limit=5&status=done`)
        const data = await res.json()
        if (data.jobs) {
          data.jobs.forEach(j => {
            if (j.created_at && j.created_at * 1000 > lastCheck.current - 30000) {
              addNotification({
                id: j.job_id + '-poll-' + Date.now(),
                jobId: j.job_id,
                standards: j.standards || [],
                status: 'done',
                timestamp: Date.now(),
                read: false,
              })
            }
          })
        }
      } catch { /* fetch failed silently */ }
      lastCheck.current = Date.now()
    }

    intervalRef.current = setInterval(poll, 30000)
    return () => {
      window.removeEventListener('job-complete', handler)
      clearInterval(intervalRef.current)
    }
  }, [API, addNotification])

  return { notifications, unreadCount, dismissNotification, clearAll, markAllRead }
}
