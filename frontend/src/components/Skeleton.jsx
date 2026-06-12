export default function Skeleton({ variant = 'text', width, height, count = 1, className = '' }) {
  const variants = {
    text: { height: '14px', width: '100%', borderRadius: '4px' },
    title: { height: '24px', width: '60%', borderRadius: '6px' },
    avatar: { height: '40px', width: '40px', borderRadius: '50%' },
    card: { height: '120px', width: '100%', borderRadius: '12px' },
    'stat-card': { height: '100px', width: '100%', borderRadius: '12px' },
    'table-row': { height: '48px', width: '100%', borderRadius: '4px' },
    button: { height: '38px', width: '120px', borderRadius: '8px' },
  }

  const style = { ...variants[variant] || variants.text, ...(width ? { width } : {}), ...(height ? { height } : {}) }
  const items = Array.from({ length: count })

  return (
    <>
      {items.map((_, i) => (
        <div key={i} className={`skeleton ${className}`} style={style} />
      ))}
    </>
  )
}
