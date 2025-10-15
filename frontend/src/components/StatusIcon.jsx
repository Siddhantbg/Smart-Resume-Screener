import { memo } from 'react'

function StatusIcon({ type, className = 'w-4 h-4', title, variant = 'stroke' }) {
  const strokeProps = {
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: 2.4,
    strokeLinecap: 'round',
    strokeLinejoin: 'round',
    vectorEffect: 'non-scaling-stroke',
  }

  if (type === 'shortlisted') {
    return (
      <svg viewBox="0 0 24 24" className={className} aria-hidden role="img">
        <path d="M6.5 12.5l3.5 3.5L17.5 8.5" {...strokeProps} />
        {title ? <title>{title}</title> : null}
      </svg>
    )
  }

  if (type === 'review') {
    return (
      <svg viewBox="0 0 24 24" className={className} aria-hidden role="img">
        <path d="M12 4.5l8 14h-16l8-14z" {...strokeProps} />
        <path d="M12 10v4.5M12 18h.01" {...strokeProps} />
        {title ? <title>{title}</title> : null}
      </svg>
    )
  }

  return (
    <svg viewBox="0 0 24 24" className={className} aria-hidden role="img">
      <path d="M8.5 8.5l7 7m0-7l-7 7" {...strokeProps} />
      {title ? <title>{title}</title> : null}
    </svg>
  )
}

export default memo(StatusIcon)
