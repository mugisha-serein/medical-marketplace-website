import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'

import { Badge } from '../../components/atoms/Badge'
import { identityContent, trustSignals, marketplaceFeatures } from './identityContent'

interface IdentityPanelProps {
  mode: 'login' | 'register'
}

export function IdentityPanel({ mode }: IdentityPanelProps) {
  const activeContent = identityContent[mode]

  const featureIcons: Record<string, React.ReactNode> = {
    search: <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>,
    file: <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>,
    'bar-chart': <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="20" x2="12" y2="10"></line><line x1="18" y1="20" x2="18" y2="4"></line><line x1="6" y1="20" x2="6" y2="16"></line></svg>,
    'credit-card': <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"></rect><line x1="1" y1="10" x2="23" y2="10"></line></svg>
  }

  return (
    <div className="relative h-full w-full flex flex-col justify-center px-12 lg:px-16 overflow-hidden bg-white">
      {/* Dynamic Glass Gradient Background */}
      <motion.div 
        animate={{ 
          scale: [1, 1.1, 1],
          opacity: [0.3, 0.4, 0.3],
        }}
        transition={{ duration: 15, repeat: Infinity, ease: 'easeInOut' }}
        className="absolute -top-1/3 -left-1/4 w-[80%] h-[80%] bg-accent/10 rounded-full blur-[120px]" 
      />
      <motion.div 
        animate={{ 
          scale: [1.1, 1, 1.1],
          opacity: [0.2, 0.3, 0.2],
        }}
        transition={{ duration: 12, repeat: Infinity, ease: 'easeInOut' }}
        className="absolute -bottom-1/3 -right-1/4 w-[80%] h-[80%] bg-primary/10 rounded-full blur-[120px]" 
      />

      <div className="relative z-10 w-full max-w-lg space-y-8">
        {/* 1. Header Section */}
        <div className="space-y-4">
          <AnimatePresence mode="wait">
            <motion.div
              key={mode}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.5, ease: [0.2, 0, 0, 1] }}
            >
              <Badge variant="accent" className="mb-4">{activeContent.badge}</Badge>
              <h1 className="text-h2 font-bold tracking-tight text-primary leading-tight mb-4">
                {activeContent.headline}
              </h1>
              <p className="text-body-lg text-text-muted leading-relaxed font-medium">
                {activeContent.description}
              </p>
            </motion.div>
          </AnimatePresence>
        </div>

        {/* 2. Trust Indicators Layer (NEW) */}
        <div className="pt-4 pb-2 border-t border-slate-100">
          <p className="text-label font-bold text-accent uppercase tracking-widest mb-4">REGULATORY & COMPLIANCE SIGNALS</p>
          <div className="flex flex-wrap gap-x-8 gap-y-4">
            {trustSignals.map((signal, idx) => (
              <div key={idx} className="flex items-center gap-2 opacity-60 hover:opacity-100 transition-opacity cursor-default">
                <div className="w-6 h-6 rounded bg-surface-muted flex items-center justify-center text-[9px] font-black text-slate-500 border border-slate-200">
                  {signal.symbol}
                </div>
                <span className="text-label font-bold text-primary tracking-tight">{signal.label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* 3. Marketplace Intelligence Features */}
        <div className="grid grid-cols-1 gap-5">
          {marketplaceFeatures.map((feature, index) => (
            <motion.div 
              key={index}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 + index * 0.1 }}
              whileHover={{ x: 5 }}
              className="group flex items-start gap-4 p-4 rounded-2xl transition-ultra hover:bg-surface-muted cursor-default border border-transparent hover:border-slate-100"
            >
              <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-white shadow-premium flex items-center justify-center text-accent group-hover:bg-accent group-hover:text-text-inverse transition-all">
                {featureIcons[feature.icon]}
              </div>
              <div className="space-y-1">
                <h3 className="text-body font-bold text-primary tracking-tight">
                  {feature.title}
                </h3>
                <p className="text-body-sm text-text-muted leading-snug font-medium">
                  {feature.text}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* 4. Brand Footer with Tagline */}
      <div className="absolute bottom-4 left-12 lg:left-16 flex items-center gap-4">
        <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-text-inverse font-bold text-lg shadow-lg">
          M
        </div>
        <div className="flex flex-col">
          <span className="text-body-sm font-black text-primary tracking-tighter leading-none">MEDIMARKET ELITE</span>
          <span className="text-label font-bold text-accent tracking-[0.2em] uppercase mt-1">Global Procurement OS</span>
        </div>
      </div>

    </div>
  )
}

