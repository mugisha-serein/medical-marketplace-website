import { Outlet } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Navbar } from '../components/organisms/Navbar/Navbar'
import { Footer } from '../components/organisms/Footer/Footer'

export default function MainLayout() {
  return (
    <div className="min-h-screen bg-surface flex flex-col">
      {/* Premium Modular Navigation */}
      <Navbar />

      {/* Main Content with Transition */}
      <motion.main
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1, duration: 0.5, ease: [0.2, 0, 0, 1] }}
        className="flex-1 w-full"
      >
        <Outlet />
      </motion.main>

      {/* Global Footer */}
      <Footer />
    </div>
  )
}
