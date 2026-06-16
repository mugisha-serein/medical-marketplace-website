import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { useLogin } from '../../../../application/hooks/auth/useLogin'
import { useAuth } from '../../../../application/hooks/auth/useAuth'
import { Input } from '../../atoms/Input'
import { Button } from '../../atoms/Button'
import { motion } from 'framer-motion'
import { authContent } from '../../../../presentation/pages/auth/authContent'

export function LoginForm() {
  const login = useLogin()
  const { loading } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [rememberMe, setRememberMe] = useState(false)
  
  const content = authContent.login

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    await login(email.trim(), password)
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0 }
  }

  return (
    <motion.form 
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      onSubmit={handleSubmit} 
      noValidate 
      className="space-y-7 w-full max-w-[420px]"
    >
      <div className="space-y-5">
        <motion.div variants={itemVariants}>
          <Input
            id="email"
            type="email"
            label={content.emailLabel}
            placeholder={content.emailPlaceholder}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            required
            leftIcon={(
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
            )}
          />
        </motion.div>
        
        <motion.div variants={itemVariants} className="space-y-4">
          <Input
            id="password"
            type="password"
            label={content.passwordLabel}
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
            leftIcon={(
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
            )}
          />
          <div className="flex items-center justify-between px-1">
            <label className="flex items-center gap-2 cursor-pointer group">
              <input 
                type="checkbox" 
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="w-4 h-4 rounded border-slate-200 text-accent focus:ring-accent transition-all cursor-pointer"
              />
              <span className="text-[13px] font-bold text-text-muted group-hover:text-primary transition-colors select-none">
                {content.rememberMe}
              </span>
            </label>
            <Link to="/forgot-password" className="text-xs font-black text-accent hover:text-accent-hover transition-colors uppercase tracking-[0.1em] border-b-2 border-transparent hover:border-accent/30 pb-0.5">
              {content.forgotPassword}
            </Link>
          </div>
        </motion.div>
      </div>

      <motion.div variants={itemVariants} className="space-y-5">
        <div className="relative group">
          <Button type="submit" className="w-full relative z-10" isLoading={loading} size="lg" variant="primary">
            {content.submitButton}
          </Button>
          <div className="absolute -inset-1 bg-primary/20 rounded-[20px] blur opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>

        {/* Security Reassurance Row */}
        <div className="flex items-center justify-center gap-6 px-4 py-3 bg-slate-50/50 rounded-2xl border border-slate-100/50">
          <div className="flex items-center gap-1.5 opacity-50">
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
            <span className="text-[10px] font-black tracking-widest uppercase">SSL SECURED</span>
          </div>
          <div className="w-[1px] h-3 bg-slate-200" />
          <div className="flex items-center gap-1.5 opacity-50">
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
            <span className="text-[10px] font-black tracking-widest uppercase">ENCRYPTED DATA</span>
          </div>
        </div>
      </motion.div>

      <motion.div variants={itemVariants} className="pt-2 text-center border-t border-slate-50 mt-4">
        <p className="text-[14px] text-text-muted font-medium">
          New to the MediMarket Ecosystem?{' '}
          <Link to="/register" className="font-bold text-accent hover:text-accent-hover transition-colors underline decoration-2 underline-offset-4">
            Join Now
          </Link>
        </p>
      </motion.div>

    </motion.form>
  )
}

