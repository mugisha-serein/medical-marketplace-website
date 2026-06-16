import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export const CatalogSort = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [selected, setSelected] = useState('Newest Arrival');

  const options = [
    'Newest Arrival',
    'Price: Low to High',
    'Price: High to Low',
    'Most Popular',
    'Availability'
  ];

  return (
    <div className="relative">
      <div className="flex items-center gap-3">
        <span className="text-[11px] font-black uppercase tracking-widest text-text-muted">Sort By:</span>
        <button 
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-4 px-5 h-12 bg-white border border-slate-100 rounded-xl hover:border-accent transition-all duration-300"
        >
          <span className="text-[13px] font-bold text-primary">{selected}</span>
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
            className={`text-accent transition-transform duration-300 ${isOpen ? 'rotate-180' : ''}`}
          >
            <path d="m6 9 6 6 6-6"/>
          </svg>
        </button>
      </div>

      <AnimatePresence>
        {isOpen && (
          <>
            <div 
              className="fixed inset-0 z-10" 
              onClick={() => setIsOpen(false)} 
            />
            <motion.div
              initial={{ opacity: 0, y: 10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 10, scale: 0.95 }}
              transition={{ duration: 0.2, ease: [0.2, 0, 0, 1] }}
              className="absolute right-0 mt-3 w-64 bg-white rounded-2xl shadow-premium border border-slate-100 p-2 z-20"
            >
              {options.map((opt) => (
                <button
                  key={opt}
                  onClick={() => {
                    setSelected(opt);
                    setIsOpen(false);
                  }}
                  className={`w-full text-left px-5 py-3 rounded-xl text-[13px] font-bold transition-all duration-200 ${
                    selected === opt 
                      ? 'bg-accent/5 text-accent' 
                      : 'text-text-muted hover:bg-slate-50 hover:text-primary'
                  }`}
                >
                  {opt}
                </button>
              ))}
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};
