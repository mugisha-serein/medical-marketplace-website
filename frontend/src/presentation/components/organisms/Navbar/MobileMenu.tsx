import { useState } from 'react';
import { NavLink, Link } from 'react-router-dom';
import { PRIMARY_NAV_LINKS, CATALOG_CATEGORIES } from './navConstants';
import { useAuth } from '../../../../application/hooks/auth/useAuth';
import { useAuthStore } from '../../../../core/store/authSlice';
import { motion, AnimatePresence } from 'framer-motion';

interface MobileMenuProps {
  isOpen: boolean;
  onClose: () => void;
}

export const MobileMenu = ({ isOpen, onClose }: MobileMenuProps) => {
  const [isCatalogExpanded, setIsCatalogExpanded] = useState(false);
  const { isAuthenticated, user } = useAuth();
  const logout = useAuthStore((state) => state.logout);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-[60] bg-primary/20 backdrop-blur-sm md:hidden"
          />

          {/* Drawer */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed top-0 right-0 z-[70] h-screen w-[85%] max-w-[400px] bg-white shadow-2xl md:hidden overflow-y-auto"
          >
            <div className="p-6 flex flex-col h-full">
              {/* Header */}
              <div className="flex items-center justify-between mb-10">
                <Link to="/" onClick={onClose} className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center text-white font-black">A</div>
                  <span className="text-[18px] font-black tracking-tighter text-primary">Active Life</span>
                </Link>
                <button 
                  onClick={onClose}
                  className="p-2 text-text-muted hover:text-primary transition-colors bg-slate-50 rounded-full"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
                </button>
              </div>

              {/* Main Nav */}
              <nav className="flex flex-col gap-2 mb-10">
                <NavLink 
                  to="/" 
                  onClick={onClose}
                  className={({ isActive }) => `px-4 py-3 rounded-2xl text-[16px] font-bold transition-all ${isActive ? 'bg-accent/5 text-accent' : 'text-primary'}`}
                >
                   Home
                </NavLink>

                {/* Catalog Accordion */}
                <div className="flex flex-col">
                  <button
                    onClick={() => setIsCatalogExpanded(!isCatalogExpanded)}
                    className={`flex items-center justify-between px-4 py-3 rounded-2xl text-[16px] font-bold transition-all ${isCatalogExpanded ? 'text-accent' : 'text-primary'}`}
                  >
                    Medical Catalog
                    <svg 
                      xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"
                      className={`transition-transform duration-300 ${isCatalogExpanded ? 'rotate-180' : ''}`}
                    >
                      <path d="m6 9 6 6 6-6"/>
                    </svg>
                  </button>
                  
                  <AnimatePresence>
                    {isCatalogExpanded && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="overflow-hidden bg-slate-50/50 rounded-2xl mx-2 mb-2"
                      >
                        <div className="py-2 flex flex-col">
                          {CATALOG_CATEGORIES.map((cat) => (
                            <Link
                              key={cat.slug}
                              to={`/catalog/${cat.slug}`}
                              onClick={onClose}
                              className="px-6 py-2.5 text-[14px] font-bold text-text-muted hover:text-accent transition-colors"
                            >
                              {cat.label}
                            </Link>
                          ))}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>

                {PRIMARY_NAV_LINKS.filter(l => l.label !== 'Home').map((link) => (
                  <NavLink 
                    key={link.href}
                    to={link.href} 
                    onClick={onClose}
                    className={({ isActive }) => `px-4 py-3 rounded-2xl text-[16px] font-bold transition-all ${isActive ? 'bg-accent/5 text-accent' : 'text-primary'}`}
                  >
                    {link.label}
                  </NavLink>
                ))}
              </nav>

              {/* User Section (Sticky Bottom) */}
              <div className="mt-auto pt-8 border-t border-slate-100">
                {isAuthenticated ? (
                  <div className="flex flex-col gap-4">
                    <div className="px-4">
                      <p className="text-[12px] font-black text-text-muted uppercase tracking-widest mb-1">Signed in as</p>
                      <p className="text-[15px] font-black text-primary truncate">{user?.name || user?.email}</p>
                    </div>
                    <Link to="/account" onClick={onClose} className="mx-2 px-4 py-3 rounded-2xl bg-primary text-white text-center font-black text-[14px]">
                      Manage Account
                    </Link>
                    <button 
                      onClick={() => { logout(); onClose(); }}
                      className="mx-2 px-4 py-3 rounded-2xl border-2 border-slate-100 text-text-muted text-center font-bold text-[14px] hover:bg-slate-50"
                    >
                      Sign Out
                    </button>
                  </div>
                ) : (
                  <div className="flex flex-col gap-3 px-2">
                    <Link to="/login" onClick={onClose} className="w-full py-4 rounded-2xl bg-accent text-white text-center font-black text-[15px] shadow-lg shadow-accent/20">
                      Sign In
                    </Link>
                    <Link to="/register" onClick={onClose} className="w-full py-4 rounded-2xl border-2 border-slate-100 text-primary text-center font-black text-[15px]">
                      Create Account
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
