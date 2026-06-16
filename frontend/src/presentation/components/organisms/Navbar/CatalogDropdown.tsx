import { Link } from 'react-router-dom';
import { CATALOG_CATEGORIES } from './navConstants';
import { motion } from 'framer-motion';

export const CatalogDropdown = ({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) => {
  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 15, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 10, scale: 0.98 }}
      transition={{ duration: 0.2, ease: [0.2, 0, 0, 1] }}
      className="absolute left-1/2 -translate-x-1/2 top-full pt-4 w-[760px] z-50 pointer-events-auto"
    >
      <div className="glass rounded-[24px] p-8 shadow-premium border border-white/20">
        <div className="grid grid-cols-2 gap-x-10 gap-y-8">
          {CATALOG_CATEGORIES.map((category) => (
            <Link
              key={category.slug}
              to={`/catalog/${category.slug}`}
              onClick={onClose}
              className="group flex flex-col gap-1 p-3 -m-3 rounded-2xl hover:bg-slate-50 transition-colors"
            >
              <span className="text-[15px] font-bold text-primary group-hover:text-accent transition-colors flex items-center gap-2">
                {category.label}
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
                  className="opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all"
                >
                  <path d="m9 18 6-6-6-6"/>
                </svg>
              </span>
              <span className="text-[13px] text-text-muted leading-relaxed">
                {category.description}
              </span>
            </Link>
          ))}
        </div>

        {/* Bottom CTA or Info */}
        <div className="mt-10 pt-6 border-t border-slate-100 flex items-center justify-between">
          <p className="text-[12px] font-bold text-text-muted uppercase tracking-widest italic opacity-60">
            Professional Grade Orthopedic Solutions
          </p>
          <Link 
            to="/catalog" 
            onClick={onClose}
            className="text-[13px] font-black text-accent hover:underline decoration-2 underline-offset-4"
          >
            View Full Inventory →
          </Link>
        </div>
      </div>
    </motion.div>
  );
};
