import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { NavLinks } from './NavLinks';
import { CartIcon } from './CartIcon';
import { ProfileDropdown } from './ProfileDropdown';
import { MobileMenu } from './MobileMenu';
import { AnimatePresence } from 'framer-motion';

import { Container } from '../../atoms/layout/LayoutPrimitives';

export const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header 
      className={`fixed top-0 left-0 right-0 z-[100] transition-all duration-500 border-b ${
        isScrolled 
          ? 'py-3 glass shadow-premium border-white/40' 
          : 'py-6 bg-transparent border-transparent'
      }`}
    >
      <Container className="flex items-center justify-between">
        
        {/* Left: Logo */}
        <Link to="/" className="flex items-center gap-2 group">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-accent flex items-center justify-center text-white shadow-lg shadow-accent/20 transition-transform group-hover:scale-105 group-hover:rotate-3">
              <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M11 2a2 2 0 0 0-2 2v5H4a2 2 0 0 0-2 2v2c0 1.1.9 2 2 2h5v5c0 1.1.9 2 2 2h2a2 2 0 0 0 2-2v-5h5a2 2 0 0 0 2-2v-2a2 2 0 0 0-2-2h-5V4a2 2 0 0 0-2-2h-2z"/></svg>
            </div>
          </div>
          <div className="flex flex-col -gap-1">
            <span className="text-body font-black tracking-tighter text-primary leading-none uppercase">Active Life</span>
            <span className="text-label font-black tracking-[0.2em] text-accent uppercase leading-none opacity-80">Orthopedic Ltd</span>
          </div>
        </Link>

        {/* Center: Desktop Links */}
        <NavLinks />

        {/* Right: Actions */}
        <div className="flex items-center gap-2 md:gap-4">
          <CartIcon />
          
          <div className="hidden md:block relative">
            <button 
              onClick={() => setIsProfileOpen(!isProfileOpen)}
              className={`p-2 rounded-xl transition-all ${isProfileOpen ? 'bg-accent/10 text-accent' : 'text-text-muted hover:text-primary hover:bg-surface-muted'}`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </button>
            
            <AnimatePresence>
              {isProfileOpen && (
                <ProfileDropdown isOpen={isProfileOpen} onClose={() => setIsProfileOpen(false)} />
              )}
            </AnimatePresence>
          </div>

          {/* Mobile Menu Toggle */}
          <button 
            onClick={() => setIsMobileMenuOpen(true)}
            className="md:hidden p-2 text-text-muted hover:text-primary transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>
          </button>
        </div>
      </Container>

      {/* Mobile Drawer */}
      <MobileMenu isOpen={isMobileMenuOpen} onClose={() => setIsMobileMenuOpen(false)} />
    </header>
  );
};
