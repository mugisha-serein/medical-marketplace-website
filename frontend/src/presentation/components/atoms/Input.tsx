import { useState, type InputHTMLAttributes, type ReactNode } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  leftIcon?: ReactNode
  rightIcon?: ReactNode
}

export function Input({
  label,
  error,
  leftIcon,
  rightIcon,
  className = '',
  id,
  type = 'text',
  ...props
}: InputProps) {
  const [showPassword, setShowPassword] = useState(false)
  const isPassword = type === 'password'
  const inputType = isPassword ? (showPassword ? 'text' : 'password') : type

  return (
    <div className={`flex flex-col gap-2 w-full text-left ${className}`}>
      {label && (
        <label htmlFor={id} className="text-[13px] font-semibold text-text-muted font-heading uppercase tracking-wider ml-1">
          {label}
        </label>
      )}
      <div 
        className={`group flex items-center gap-3 px-4 border rounded-xl bg-surface-muted transition-ultra focus-within:border-accent focus-within:bg-white focus-within:ring-4 focus-within:ring-accent/5 ${
          error ? 'border-error/50 bg-error/5' : 'border-slate-200'
        }`}
      >
        {leftIcon && <span className="flex text-text-muted transition-colors group-focus-within:text-accent font-bold">{leftIcon}</span>}
        
        <input
          id={id}
          type={inputType}
          className="flex-1 py-3.5 bg-transparent text-text-main text-[15px] outline-none placeholder:text-slate-400 font-medium"
          {...props}
        />

        {isPassword && (
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="flex items-center justify-center p-2 text-text-muted hover:text-accent transition-colors"
          >
            {showPassword ? (
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
            )}
          </button>
        )}

        {rightIcon && !isPassword && <span className="flex text-text-muted transition-colors group-focus-within:text-accent">{rightIcon}</span>}
      </div>
      
      <AnimatePresence>
        {error && (
          <motion.p 
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -5 }}
            className="text-[12px] font-semibold text-error px-1 mt-0.5"
          >
            {error}
          </motion.p>
        )}
      </AnimatePresence>
    </div>
  )
}


