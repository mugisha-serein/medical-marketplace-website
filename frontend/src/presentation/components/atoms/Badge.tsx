import type { ReactNode } from 'react'
import { motion } from 'framer-motion'

interface BadgeProps {
  children: ReactNode
  variant?: 'primary' | 'accent' | 'success' | 'warning' | 'error' | 'neutral'
  size?: 'sm' | 'md'
  className?: string
}

export function Badge({ children, variant = 'primary', size = 'sm', className = '' }: BadgeProps) {

  const variants = {
    primary: 'bg-primary/5 text-primary border-primary/10',
    accent: 'bg-accent/10 text-accent border-accent/20',
    success: 'bg-success/10 text-success border-success/20',
    warning: 'bg-warning/10 text-warning border-warning/20',
    error: 'bg-error/10 text-error border-error/20',
    neutral: 'bg-slate-100 text-slate-600 border-slate-200',
  }

  const sizes = {
    sm: 'px-2.5 py-0.5 text-[10px]',
    md: 'px-3.5 py-1 text-[12px]',
  }

  return (
    <motion.span 
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`inline-flex items-center justify-center font-bold rounded-full uppercase tracking-[0.05em] border ${variants[variant]} ${sizes[size]} ${className}`}
    >

      {children}
    </motion.span>
  )
}


