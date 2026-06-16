import type { ReactNode } from 'react'
import { motion, type HTMLMotionProps } from 'framer-motion'

interface ButtonProps extends HTMLMotionProps<"button"> {
  children: ReactNode
  variant?: 'primary' | 'accent' | 'ghost' | 'error' | 'secondary'
  size?: 'sm' | 'md' | 'lg'
  isLoading?: boolean
  leftIcon?: ReactNode
  rightIcon?: ReactNode
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  leftIcon,
  rightIcon,
  className = '',
  disabled,
  ...props
}: ButtonProps) {
  const baseClasses = 'relative inline-flex items-center justify-center gap-2 rounded-xl font-heading font-semibold transition-ultra border border-transparent cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap outline-none select-none overflow-hidden'
  
  const variants = {
    primary: 'bg-primary text-white shadow-premium hover:bg-primary-hover',
    accent: 'bg-accent text-white shadow-premium hover:bg-accent-hover',
    ghost: 'bg-transparent text-text-muted hover:bg-surface-muted hover:text-primary border-transparent',
    secondary: 'bg-white text-primary border-slate-200 hover:border-accent hover:text-accent shadow-sm',
    error: 'bg-error/10 text-error border-error/20 hover:bg-error/20',
  }

  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  }

  return (
    <motion.button
      whileHover={{ y: -1 }}
      whileTap={{ scale: 0.98 }}
      className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && (
        <motion.span 
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="absolute inset-0 flex items-center justify-center bg-inherit"
        >
          <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
        </motion.span>
      )}
      
      <div className={`flex items-center gap-2 ${isLoading ? 'opacity-0' : 'opacity-100'}`}>
        {!isLoading && leftIcon && <span className="flex items-center">{leftIcon}</span>}
        <span>{children}</span>
        {!isLoading && rightIcon && <span className="flex items-center">{rightIcon}</span>}
      </div>
    </motion.button>
  )
}


