import type { ReactNode } from 'react'
import { motion } from 'framer-motion'

interface CardProps {
  children: ReactNode
  className?: string
  glass?: boolean
  padding?: 'none' | 'sm' | 'md' | 'lg'
  onClick?: () => void
}

export function Card({
  children,
  className = '',
  glass = false,
  padding = 'md',
  onClick,
}: CardProps) {
  const paddings = {
    none: 'p-0',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  }

  const Component = onClick ? motion.div : 'div'
  const motionProps = onClick ? {
    whileHover: { y: -4, transition: { duration: 0.3, ease: [0.2, 0, 0, 1] } },
    whileTap: { scale: 0.99 },
  } : {}

  return (
    <Component
      className={`bg-white rounded-[24px] overflow-hidden transition-ultra ${
        glass ? 'glass' : 'border border-slate-100 shadow-premium'
      } ${paddings[padding]} ${
        onClick ? 'cursor-pointer hover:border-accent/40' : ''
      } ${className}`}
      onClick={onClick}
      {...(motionProps as object)}
    >
      {children}
    </Component>

  )
}


