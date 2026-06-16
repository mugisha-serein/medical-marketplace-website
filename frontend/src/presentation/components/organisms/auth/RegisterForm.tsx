import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { useRegister } from '../../../../application/hooks/auth/useRegister'
import { useAuth } from '../../../../application/hooks/auth/useAuth'
import { Input } from '../../atoms/Input'
import { Button } from '../../atoms/Button'
import { motion } from 'framer-motion'
import { authContent } from '../../../../presentation/pages/auth/authContent'

export function RegisterForm() {
  const register = useRegister()
  const { loading } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [name, setName] = useState('')
  const [agreed, setAgreed] = useState(false)
  const [_, setError] = useState<string | null>(null)

  const content = authContent.register

  const validatePassword = (pass: string) => {
    if (pass.length < 8) return 'Password must be at least 8 characters'
    return null
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError(null)

    const passwordIssue = validatePassword(password)
    if (passwordIssue) {
      setError(passwordIssue)
      return
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (!agreed) {
      setError('Please accept the Terms of Sale to continue')
      return
    }

    await register(email.trim(), password, name.trim())
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
      className="space-y-6 w-full max-w-[440px]"
    >
      <div className="space-y-4">
        <motion.div variants={itemVariants}>
          <Input
            id="name"
            label={content.nameLabel}
            placeholder={content.namePlaceholder}
            value={name}
            onChange={(e) => setName(e.target.value)}
            autoComplete="name"
            required
            leftIcon={(
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
            )}
          />
        </motion.div>

        <motion.div variants={itemVariants}>
          <Input
            id="email-reg"
            type="email"
            label={content.emailLabel}
            placeholder={content.emailPlaceholder}
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            required
            leftIcon={(
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
            )}
          />
        </motion.div>
        
        <motion.div variants={itemVariants} className="space-y-4">
          <Input
            id="password-reg"
            type="password"
            label={content.passwordLabel}
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="new-password"
            required
            leftIcon={(
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
            )}
          />
          <Input
            id="confirm-password"
            type="password"
            label={content.confirmLabel}
            placeholder="••••••••"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            autoComplete="new-password"
            required
            leftIcon={(
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
            )}
          />
        </motion.div>

        <motion.div variants={itemVariants} className="px-1 py-1">
          <label className="flex items-center gap-3 cursor-pointer group">
            <input 
              type="checkbox" 
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
              className="w-4 h-4 rounded border-slate-200 text-accent focus:ring-accent transition-all cursor-pointer"
            />
            <span className="text-[13px] font-medium text-text-muted leading-tight">
              I agree to the <Link to="/terms" className="text-accent font-bold hover:underline">{content.agreementTerms}</Link>
              {' '}and{' '}
              <Link to="/privacy" className="text-accent font-bold hover:underline">{content.agreementPrivacy}</Link>.
            </span>
          </label>
        </motion.div>
      </div>

      <motion.div variants={itemVariants} className="relative group">
        <Button type="submit" className="w-full relative z-10" isLoading={loading} size="lg" variant="primary">
          {content.submitButton}
        </Button>
        <div className="absolute -inset-1 bg-primary/20 rounded-[20px] blur opacity-0 group-hover:opacity-100 transition-opacity" />
      </motion.div>

      <motion.div variants={itemVariants} className="pt-2 text-center border-t border-slate-50 mt-6">
        <p className="text-[14px] text-text-muted font-medium">
          {content.alreadyMember}{' '}
          <Link to="/login" className="font-bold text-accent hover:text-accent-hover transition-colors underline decoration-2 underline-offset-4">
            Sign In
          </Link>
        </p>
      </motion.div>

    </motion.form>
  )
}


