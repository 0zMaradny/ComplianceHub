import { useState, useEffect, useRef } from 'react'

function Chat({ API }) {
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
    <div className="animate-fadeIn max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-[var(--text-primary)]">AI Chat</h1>
        <p className="mt-1 text-[var(--text-secondary)]">Ask questions about generated audit documents</p>
      </div>

      <div>
        {!selectedJob ? (
          <div className="mb-4">
            <h2 className="text-xl font-semibold mb-3 text-[var(--text-primary)]">Select a Job</h2>
            {jobs.length === 0 && <p className="text-[var(--text-secondary)]">No completed jobs found. Generate documents first.</p>}
            <div className="flex flex-col gap-2 max-w-md">
              {jobs.map(job => (
                <button
                  key={job.job_id}
                  className="flex items-center justify-between px-4 py-3 rounded-lg border border-[var(--border-color)] cursor-pointer hover:border-[var(--primary)] transition-colors w-full text-left bg-[var(--bg-card)]"
                  onClick={() => setSelectedJob(job.job_id)}
                >
                  <strong>{job.job_id?.slice(0, 8)}...</strong>
                  <span className={job.status === 'done' ? 'text-green-600' : job.status === 'error' ? 'text-red-600' : 'text-amber-600'}>{job.status}</span>
                  <small>{job.created_at ? new Date(job.created_at * 1000).toLocaleDateString() : ''}</small>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="flex flex-col h-[70vh]">
            <div className="flex items-center gap-3 px-4 py-3 border-b border-[var(--border-color)] mb-2">
              <button className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded-md text-sm cursor-pointer border-none transition-colors" onClick={() => { setSelectedJob(null); setMessages([]) }}>
                ← Back
              </button>
              <span>Job: {selectedJob.slice(0, 8)}...</span>
            </div>

            <div className="flex-1 overflow-y-auto px-4 py-2 flex flex-col gap-3">
              {messages.length === 0 && (
                <div className="text-center py-8 text-[var(--text-secondary)]">
                  <p>Ask about the generated documents, findings, ISO clauses, or request field refinements.</p>
                  <div className="flex flex-wrap gap-2 justify-center mt-3">
                    {['Summarize the audit findings', 'List all nonconformities', 'Refine the conclusion to be more thorough', 'Explain ISO 27001 Annex A controls'].map(s => (
                      <button key={s} className="px-3 py-1.5 rounded-full text-xs cursor-pointer bg-gray-100 hover:bg-gray-200 text-[var(--text-primary)] border-none transition-colors" onClick={() => { setInput(s); setTimeout(() => inputRef.current?.focus(), 50) }}>
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
              {sending && <div className="flex justify-start"><div className="max-w-[70%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed bg-gray-100 text-[var(--text-primary)] rounded-bl-md italic">Thinking...</div></div>}
              <div ref={bottomRef} />
            </div>

            <div className="flex gap-2 px-4 py-3 border-t border-[var(--border-color)]">
              <textarea
                ref={inputRef}
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about the audit documents..."
                rows={2}
                disabled={sending}
                className="flex-1 px-3 py-2 rounded-lg border border-[var(--border-color)] resize-none text-sm bg-[var(--input-bg)] text-[var(--text-primary)]"
              />
              <button onClick={sendMessage} disabled={!input.trim() || sending} className="px-5 py-2 rounded-lg bg-[var(--primary)] text-white font-semibold text-sm cursor-pointer disabled:opacity-50 border-none transition-colors">
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
