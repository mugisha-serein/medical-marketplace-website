import { useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { IdentityPanel } from './IdentityPanel'
import { LoginForm } from '../../components/organisms/auth/LoginForm'
import { RegisterForm } from '../../components/organisms/auth/RegisterForm'
import { authContent } from './authContent'

export default function AuthPage() {
  const location = useLocation()
  const mode = location.pathname.includes('register') ? 'register' : 'login'
  const isLogin = mode === 'login'
  const content = authContent[mode]

  return (
    <div className="h-screen w-full bg-white flex flex-col lg:flex-row overflow-hidden relative">
      {/* LEFT PANEL: Branding & Info (Hidden on mobile) */}
      <div className="hidden lg:block lg:w-[45%] xl:w-[40%] bg-white border-r border-slate-100 h-full">
        <IdentityPanel mode={mode} />
      </div>

      {/* RIGHT PANEL: Authentication Forms */}
      <div className="flex-1 relative flex flex-col items-center justify-center p-6 md:p-12 lg:p-20 bg-white">
        
        {/* Mobile Header: Trust + Branding (Visible only on <lg) */}
        <div className="lg:hidden absolute top-8 inset-x-0 px-8 flex flex-col items-center gap-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-text-inverse font-bold text-body-sm shadow-sm">
              M
            </div>
            <div className="flex flex-col">
              <span className="text-body-sm font-black text-primary tracking-tight leading-none italic">
                {authContent.mobileHeader.brand}
              </span>
              <span className="text-label font-bold text-accent tracking-[0.15em] uppercase mt-1">
                {authContent.mobileHeader.tagline}
              </span>
            </div>
          </div>
        </div>

        <motion.div 
          className="w-full max-w-[420px] z-10"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.2, 0, 0, 1] }}
        >
          {/* Headline Section */}
          <div className="mb-10 text-center lg:text-left space-y-3">
            <motion.h2 
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="text-h3 font-bold tracking-tight text-primary leading-tight font-heading"
            >
              {content.title}
            </motion.h2>
            <motion.p 
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="text-body text-text-muted font-medium leading-relaxed"
            >
              {content.subtitle}
            </motion.p>
          </div>

          {/* Form Section */}
          <AnimatePresence mode="wait">
            <motion.div
              key={mode}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.4, ease: [0.2, 0, 0, 1] }}
              className="flex justify-center lg:justify-start"
            >
              {isLogin ? <LoginForm /> : <RegisterForm />}
            </motion.div>
          </AnimatePresence>
        </motion.div>

        {/* Institutional Support Footer */}
        <div className="absolute bottom-8 lg:bottom-12 text-center w-full px-8">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
            className="inline-flex items-center gap-2 group cursor-default"
          >
            <p className="text-body-sm text-text-muted font-medium">
              {authContent.support.text} {' '}
              <a href="#" className="font-bold text-primary hover:text-accent transition-colors underline decoration-primary/20 underline-offset-4 group-hover:decoration-accent decoration-2">
                {authContent.support.link}
              </a>
            </p>
          </motion.div>
        </div>

      </div>
    </div>
  )
}

