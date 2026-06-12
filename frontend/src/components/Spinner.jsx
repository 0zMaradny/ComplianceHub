const sizes = { sm: '16px', md: '24px', lg: '40px' }

export default function Spinner({ size = 'md', className = '' }) {
  const dim = sizes[size] || sizes.md
  return (
    <svg className={`spinner ${className}`} width={dim} height={dim} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
      <circle cx="12" cy="12" r="10" opacity="0.25" />
      <path d="M12 2a10 10 0 0 1 10 10" />
    </svg>
  )
}
