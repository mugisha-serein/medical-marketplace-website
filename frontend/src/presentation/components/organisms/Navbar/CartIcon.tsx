import { Link } from 'react-router-dom';
import { useCart } from '../../../../application/hooks/cart/useCart';
import { motion, AnimatePresence } from 'framer-motion';

export const CartIcon = () => {
  const { itemCount } = useCart();

  return (
    <Link to="/cart" className="relative p-2 text-text-muted hover:text-accent transition-colors group">
      <svg 
        xmlns="http://www.w3.org/2000/svg" 
        width="24" 
        height="24" 
        viewBox="0 0 24 24" 
        fill="none" 
        stroke="currentColor" 
        strokeWidth="2" 
        strokeLinecap="round" 
        strokeLinejoin="round" 
        className="transition-transform group-hover:scale-110"
      >
        <circle cx="8" cy="21" r="1"></circle>
        <circle cx="19" cy="21" r="1"></circle>
        <path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"></path>
      </svg>
      
      <AnimatePresence>
        {itemCount > 0 && (
          <motion.span 
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.5, opacity: 0 }}
            className="absolute top-0 right-0 flex h-5 w-5 items-center justify-center rounded-full bg-accent text-[10px] font-black text-white ring-2 ring-white"
          >
            {itemCount > 99 ? '99+' : itemCount}
          </motion.span>
        )}
      </AnimatePresence>
    </Link>
  );
};
