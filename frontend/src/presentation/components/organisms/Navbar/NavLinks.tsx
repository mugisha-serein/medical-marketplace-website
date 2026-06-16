import { useState } from 'react';
import { NavLink as RouterLink } from 'react-router-dom';
import { PRIMARY_NAV_LINKS } from './navConstants';
import { CatalogDropdown } from './CatalogDropdown';
import { AnimatePresence } from 'framer-motion';

export const NavLinks = () => {
  const [isCatalogOpen, setIsCatalogOpen] = useState(false);

  return (
    <div className="hidden md:flex items-center gap-1">
      {/* Home Link (Special handling if needed, but standard link for now) */}
      <RouterLink 
        to="/" 
        className={({ isActive }) => 
          `px-4 py-2 text-body-sm font-bold transition-all rounded-xl ${
            isActive ? 'text-accent bg-accent/5' : 'text-text-muted hover:text-primary hover:bg-surface-muted'
          }`
        }
      >
        Home
      </RouterLink>

      {/* Catalog Trigger */}
      <div 
        className="relative"
        onMouseEnter={() => setIsCatalogOpen(true)}
        onMouseLeave={() => setIsCatalogOpen(false)}
      >
        <button
          className={`flex items-center gap-1.5 px-4 py-2 text-[14px] font-bold transition-all rounded-xl ${
            isCatalogOpen ? 'text-accent bg-accent/5' : 'text-text-muted hover:text-primary hover:bg-slate-50'
          }`}
        >
          Catalog
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            width="14" 
            height="14" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="3" 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            className={`transition-transform duration-300 ${isCatalogOpen ? 'rotate-180' : ''}`}
          >
            <path d="m6 9 6 6 6-6"/>
          </svg>
        </button>

        <AnimatePresence>
          {isCatalogOpen && (
            <CatalogDropdown isOpen={isCatalogOpen} onClose={() => setIsCatalogOpen(false)} />
          )}
        </AnimatePresence>
      </div>

      {/* Dynamic Links from Constants */}
      {PRIMARY_NAV_LINKS.filter(link => link.label !== 'Home').map((link) => (
        <RouterLink 
          key={link.href}
          to={link.href} 
          className={({ isActive }) => 
            `px-4 py-2 text-[14px] font-bold transition-all rounded-xl ${
              isActive ? 'text-accent bg-accent/5' : 'text-text-muted hover:text-primary hover:bg-slate-50'
            }`
          }
        >
          {link.label}
        </RouterLink>
      ))}
    </div>
  );
};
