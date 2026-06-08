import { useState, useEffect } from 'react'

const DOC_TYPE_LABELS = {
  Audit_Plan_Stage_1: 'Audit Plan Stage 1',
  Audit_Plan_Stage_2: 'Audit Plan Stage 2',
  Participation_List: 'Participation List',
  Audit_Report: 'Audit Report',
  Certificate_Text: 'Certificate Text',
  TNL: 'Test/Nonconformity Log',
  Certificate: 'Certificate',
  ISO_Checklist: 'ISO Compliance Checklist',
}

const STANDARD_LABELS = {
  iso_9001: 'ISO 9001:2015',
  iso_14001: 'ISO 14001:2015',
  iso_45001: 'ISO 45001:2018',
  iso_27001: 'ISO 27001:2022',
  iso_22301: 'ISO 22301:2019',
  iso_50001: 'ISO 50001:2018',
  iso_20000: 'ISO 20000:2018',
  iso_42001: 'ISO 42001:2023',
  iso_27701: 'ISO 27701:2019',
  iso_31000: 'ISO 31000:2018',
  iso_37301: 'ISO 37301:2021',
  iso_10002: 'ISO 10002:2018',
  iso_22000: 'ISO 22000:2018',
  iso_30401: 'ISO 30401:2018',
}

export default function Templates({ API }) {
  const [templates, setTemplates] = useState({ doc_templates: {}, checklist_templates: {} })
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    fetch(`${API}/templates`)
      .then(r => r.json())
      .then(d => { setTemplates(d); setLoading(false) })
      .catch(() => setLoading(false))
  }, [API])

  const docTemplates = Object.entries(templates.doc_templates || {})
  const checklistTemplates = Object.entries(templates.checklist_templates || {})

  const filteredChecklist = filter === 'all'
    ? checklistTemplates
    : checklistTemplates.filter(([key]) => key.includes(filter.replace('ISO ', 'iso_').split(':')[0]))

  return (
    <div>
      <div className="page-header">
        <h2>Template Manager</h2>
        <p>Browse and manage TÜV Austria document templates</p>
      </div>

      {loading ? (
        <div className="loading">Loading templates...</div>
      ) : (
        <>
          {/* Summary */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 12, marginBottom: 20 }}>
            <div className="stat-card">
              <div className="stat-number">{docTemplates.length}</div>
              <h3>Document Templates</h3>
            </div>
            <div className="stat-card">
              <div className="stat-number">{checklistTemplates.length}</div>
              <h3>Checklist Templates</h3>
            </div>
            <div className="stat-card">
              <div className="stat-number">{new Set(checklistTemplates.map(([k]) => k.split('_')[1])).size}</div>
              <h3>Standards</h3>
            </div>
          </div>

          {/* Document Templates */}
          <div className="card" style={{ marginBottom: 16 }}>
            <h3 style={{ marginBottom: 12 }}>📄 Document Templates</h3>
            {docTemplates.length === 0 ? (
              <div className="empty-state">No document templates found</div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {docTemplates.map(([docType, filename]) => (
                  <div key={docType} style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    padding: '10px 14px', borderRadius: 8, background: 'var(--gray-50)',
                    border: '1px solid var(--gray-200)',
                  }}>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: 14 }}>
                        {DOC_TYPE_LABELS[docType] || docType}
                      </div>
                      <div style={{ fontSize: 11, color: 'var(--gray-500)', marginTop: 2, fontFamily: 'monospace' }}>
                        {filename}
                      </div>
                    </div>
                    <span className="badge badge-blue">DOCX</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Checklist Templates */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <h3 style={{ margin: 0 }}>📋 Checklist Templates</h3>
              <select
                value={filter}
                onChange={e => setFilter(e.target.value)}
                style={{ padding: '4px 10px', borderRadius: 4, border: '1px solid var(--gray-300)', fontSize: 12 }}
              >
                <option value="all">All Standards</option>
                {[...new Set(checklistTemplates.map(([k]) => k.split('_')[1]))].sort().map(std => (
                  <option key={std} value={std}>{STANDARD_LABELS[std] || std}</option>
                ))}
              </select>
            </div>
            {filteredChecklist.length === 0 ? (
              <div className="empty-state">No checklist templates found</div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 8 }}>
                {filteredChecklist.map(([key, filename]) => {
                  const parts = key.split('_')
                  const std = parts[1]
                  return (
                    <div key={key} style={{
                      padding: '10px 14px', borderRadius: 8, background: 'var(--gray-50)',
                      border: '1px solid var(--gray-200)',
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <div style={{ fontWeight: 600, fontSize: 13 }}>
                          {STANDARD_LABELS[std] || std}
                        </div>
                        <span className="badge" style={{
                          fontSize: 10,
                          background: filename.endsWith('.xlsx') ? '#E8F5E9' : '#E3F2FD',
                          color: filename.endsWith('.xlsx') ? '#2E7D32' : '#1565C0',
                        }}>
                          {filename.endsWith('.xlsx') ? 'XLSX' : 'DOCX'}
                        </span>
                      </div>
                      <div style={{ fontSize: 10, color: 'var(--gray-500)', marginTop: 4, fontFamily: 'monospace' }}>
                        {filename}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
