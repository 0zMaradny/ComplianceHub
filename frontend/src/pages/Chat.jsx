import { useState, useEffect, useRef } from 'react'

function Chat({ API }) {
  const [jobs, setJobs] = useState([])
  const [selectedJob, setSelectedJob] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    const fetchJobs = () =>
      fetch(`${API}/jobs?limit=20`)
        .then(r => r.json())
        .then(data => setJobs(data.jobs || []))
        .catch(() => {})

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

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') continue
            try {
              const parsed = JSON.parse(data)
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
      setMessages(prev => [...prev, { role: 'assistant', text: 'Failed to reach AI chat service.' }])
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
    <div className="chat-page animate-fadeIn">
      <div className="page-header">
        <h1>AI Chat</h1>
        <p className="subtitle">Ask questions about generated audit documents</p>
      </div>

      <div className="chat-layout">
        {!selectedJob ? (
          <div className="chat-job-select">
            <h2>Select a Job</h2>
            {jobs.length === 0 && <p className="empty">No completed jobs found. Generate documents first.</p>}
            <div className="job-list">
              {jobs.map(job => (
                <button
                  key={job.job_id}
                  className="job-card"
                  onClick={() => setSelectedJob(job.job_id)}
                >
                  <strong>{job.job_id?.slice(0, 8)}...</strong>
                  <span style={job.status === 'done' ? { color: '#16a34a' } : job.status === 'error' ? { color: '#dc2626' } : { color: '#ca8a04' }}>{job.status}</span>
                  <small>{job.created_at ? new Date(job.created_at * 1000).toLocaleDateString() : ''}</small>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="chat-session">
            <div className="chat-header">
              <button className="btn-back" onClick={() => { setSelectedJob(null); setMessages([]) }}>
                ← Back
              </button>
              <span>Job: {selectedJob.slice(0, 8)}...</span>
            </div>

            <div className="chat-messages">
              {messages.length === 0 && (
                <div className="chat-welcome">
                  <p>Ask about the generated documents, findings, ISO clauses, or request field refinements.</p>
                  <div className="suggestions">
                    {['Summarize the audit findings', 'List all nonconformities', 'Refine the conclusion to be more thorough', 'Explain ISO 27001 Annex A controls'].map(s => (
                      <button key={s} className="chip" onClick={() => { setInput(s); setTimeout(() => document.querySelector('.chat-input textarea')?.focus(), 50) }}>
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              {messages.map((m, i) => (
                <div key={i} className={`chat-msg ${m.role}`}>
                  <div className="msg-bubble">{m.text}</div>
                </div>
              ))}
              {sending && <div className="chat-msg assistant"><div className="msg-bubble typing">Thinking...</div></div>}
              <div ref={bottomRef} />
            </div>

            <div className="chat-input">
              <textarea
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about the audit documents..."
                rows={2}
                disabled={sending}
              />
              <button onClick={sendMessage} disabled={!input.trim() || sending}>
                Send
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Chat
