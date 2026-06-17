import { useState, useEffect, useRef } from 'react'
import { useTranslation } from 'react-i18next'

function Chat({ API }) {
  const { t } = useTranslation()
  const [jobs, setJobs] = useState([])
  const [selectedJob, setSelectedJob] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    const fetchJobs = () =>
      fetch(`${API}/jobs?limit=20`)
        .then(r => r.json())
        .then(data => setJobs(data.jobs || []))
        .catch(e => console.error('Failed to fetch jobs:', e))

    fetchJobs()
    const interval = setInterval(fetchJobs, 10000)
    return () => clearInterval(interval)
  }, [API])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || !selectedJob || sending) return
    const userMsg = input.trim()
    setInput('')
    setSending(true)
    setMessages(prev => [...prev, { role: 'user', text: userMsg }])

    try {
      const history = messages.map(m => m.text)
      const res = await fetch(`${API}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_id: selectedJob, message: userMsg, history }),
      })

      const reader = res.body?.getReader()
      if (!reader) throw new Error('No response body')

      const decoder = new TextDecoder()
      let buffer = ''
      let assistantText = ''

      setMessages(prev => [...prev, { role: 'assistant', text: '' }])

      let streamError = false

      while (true) {
        const { done, value } = await reader.read()
        if (done || streamError) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]' || streamError) continue
            try {
              const parsed = JSON.parse(data)
              if (parsed.error) {
                setMessages(prev => {
                  const next = [...prev]
                  next[next.length - 1] = { role: 'assistant', text: assistantText + `\n[Error: ${parsed.error}]` }
                  return next
                })
                streamError = true
                break
              }
              if (parsed.token) {
                assistantText += parsed.token
                setMessages(prev => {
                  const next = [...prev]
                  next[next.length - 1] = { role: 'assistant', text: assistantText }
                  return next
                })
              }
            } catch { /* skip malformed JSON */ }
          }
        }
      }
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', text: t('chat.failed') }])
    }
    setSending(false)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="animate-fadeIn max-w-5xl mx-auto">
      <div className="page-header">
        <h1>{t('chat.title')}</h1>
        <p>{t('chat.subtitle')}</p>
      </div>

      <div>
        {!selectedJob ? (
          <div className="mb-4">
            <h2 className="text-xl font-semibold mb-3 text-[var(--text-primary)]">{t('chat.select_job')}</h2>
            {jobs.length === 0 && <p className="text-[var(--text-secondary)]">{t('chat.no_jobs')}</p>}
            <div className="flex flex-col gap-2 max-w-md">
              {jobs.map(job => (
                <button
                  key={job.job_id}
                  className="card cursor-pointer hover:border-[var(--primary)] w-full text-left"
                  onClick={() => setSelectedJob(job.job_id)}
                >
                  <strong>{job.job_id?.slice(0, 8)}...</strong>
                  <span className={`badge ${job.status === 'done' ? 'badge-success' : job.status === 'error' ? 'badge-error' : 'badge-warning'}`}>{job.status}</span>
                  <small>{job.created_at ? new Date(job.created_at * 1000).toLocaleDateString() : ''}</small>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="flex flex-col h-[70vh]">
            <div className="flex items-center gap-3 px-4 py-3 border-b border-[var(--border-color)] mb-2">
              <button className="btn btn-ghost" onClick={() => { setSelectedJob(null); setMessages([]) }}>
                {t('chat.back')}
              </button>
              <span>{t('chat.job_prefix')} {selectedJob.slice(0, 8)}...</span>
            </div>

            <div className="flex-1 overflow-y-auto px-4 py-2 flex flex-col gap-3">
              {messages.length === 0 && (
                <div className="text-center py-8 text-[var(--text-secondary)]">
                  <p>{t('chat.instructions')}</p>
                  <div className="flex flex-wrap gap-2 justify-center mt-3">
                    {[t('chat.suggest_summary'), t('chat.suggest_ncs'), t('chat.suggest_refine'), t('chat.suggest_annex')].map(s => (
                      <button key={s} className="btn btn-ghost" style={{ borderRadius: 9999, fontSize: 11, padding: '6px 14px' }} onClick={() => { setInput(s); setTimeout(() => inputRef.current?.focus(), 50) }}>
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              {messages.map((m, i) => (
                <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[70%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${m.role === 'user' ? 'bg-[var(--primary)] text-white rounded-br-md' : 'bg-gray-100 text-[var(--text-primary)] rounded-bl-md'}`}>{m.text}</div>
                </div>
              ))}
              {sending && <div className="flex justify-start"><div className="max-w-[70%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed bg-gray-100 text-[var(--text-primary)] rounded-bl-md italic">{t('chat.thinking')}</div></div>}
              <div ref={bottomRef} />
            </div>

            <div className="flex gap-2 px-4 py-3 border-t border-[var(--border-color)]">
              <textarea
                ref={inputRef}
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={t('chat.placeholder')}
                rows={2}
                disabled={sending}
                className="input flex-1 resize-none"
              />
              <button onClick={sendMessage} disabled={!input.trim() || sending} className="btn btn-primary">
                {t('chat.send')}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Chat
