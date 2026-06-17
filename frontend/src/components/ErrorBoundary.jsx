import { Component } from 'react'
import { withTranslation } from 'react-i18next'

class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, info) {
    console.error('[ErrorBoundary]', error, info)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null })
  }

  render() {
    const { t } = this.props
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center',
          justifyContent: 'center', minHeight: '60vh', padding: 24, textAlign: 'center',
        }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>⚠️</div>
          <h2 style={{ marginBottom: 8 }}>{t('error.something_wrong')}</h2>
          <p style={{ color: 'var(--gray-600)', marginBottom: 20, maxWidth: 400 }}>
            {t('error.description')}
          </p>
          {this.state.error && (
            <pre style={{
              background: 'var(--gray-100)', padding: 12, borderRadius: 8,
              fontSize: 12, maxWidth: 500, overflow: 'auto', marginBottom: 20,
              color: 'var(--red-600)',
            }}>
              {this.state.error.toString()}
            </pre>
          )}
          <div style={{ display: 'flex', gap: 12 }}>
            <button className="btn btn-primary" onClick={this.handleReset}>
              {t('error.try_again')}
            </button>
            <button className="btn btn-secondary" onClick={() => window.location.reload()}>
              {t('error.refresh')}
            </button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}

export default withTranslation()(ErrorBoundary)
