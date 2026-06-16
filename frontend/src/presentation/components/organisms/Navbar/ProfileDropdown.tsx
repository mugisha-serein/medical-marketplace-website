import { Link } from 'react-router-dom';
import { useAuth } from '../../../../application/hooks/auth/useAuth';
import { useAuthStore } from '../../../../core/store/authSlice';
import { motion } from 'framer-motion';

export const ProfileDropdown = ({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) => {
  const { isAuthenticated, user } = useAuth();
  const logout = useAuthStore((state) => state.logout);

  if (!isOpen) return null;

  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/5" onClick={onClose} />
      
      <motion.div
        initial={{ opacity: 0, y: 10, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 10, scale: 0.95 }}
        className="absolute right-0 top-full mt-4 w-64 z-50 glass rounded-2xl p-2 shadow-premium"
      >
        <div className="flex flex-col">
          {isAuthenticated ? (
            <>
              <div className="px-4 py-3 border-b border-slate-100 mb-2">
                <p className="text-[14px] font-black text-primary truncate">{user?.name || 'My Account'}</p>
                <p className="text-[12px] text-text-muted truncate">{user?.email}</p>
              </div>
              
              <Link to="/account" onClick={onClose} className="px-4 py-2.5 text-[14px] font-bold text-text-muted hover:text-accent hover:bg-slate-50 rounded-xl transition-all">
                User Dashboard
              </Link>
              <Link to="/orders" onClick={onClose} className="px-4 py-2.5 text-[14px] font-bold text-text-muted hover:text-accent hover:bg-slate-50 rounded-xl transition-all">
                Order History
              </Link>
              <div className="h-[1px] bg-slate-100 my-2 mx-2" />
              <button
                onClick={() => {
                  logout();
                  onClose();
                }}
                className="w-full text-left px-4 py-2.5 text-[14px] font-bold text-error hover:bg-error/5 rounded-xl transition-all"
              >
                Sign Out
              </button>
            </>
          ) : (
            <>
              <div className="px-4 py-3 border-b border-slate-100 mb-2">
                <p className="text-[13px] font-bold text-text-muted uppercase tracking-widest">Identify Yourself</p>
              </div>
              <Link to="/login" onClick={onClose} className="px-4 py-2.5 text-[14px] font-bold text-primary hover:text-accent hover:bg-slate-50 rounded-xl transition-all">
                Login
              </Link>
              <Link to="/register" onClick={onClose} className="mx-2 mt-2 mb-2">
                <div className="bg-accent text-white rounded-xl px-4 py-2.5 text-center text-[14px] font-black hover:bg-accent-hover transition-colors">
                  Create Account
                </div>
              </Link>
            </>
          )}
        </div>
      </motion.div>
    </>
  );
};
