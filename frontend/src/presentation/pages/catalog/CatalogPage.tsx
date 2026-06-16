import { Section, Container, Grid } from '../../components/atoms/layout/LayoutPrimitives';
import { Breadcrumbs } from '../../components/atoms/Breadcrumbs';
import { Badge } from '../../components/atoms/Badge';
import { Button } from '../../components/atoms/Button';
import { LoadingSpinner } from '../../components/atoms/LoadingSpinner';
import { ProductCard } from '../../components/molecules/ProductCard';
import { CatalogSort } from '../../components/molecules/catalog/CatalogSort';
import { CatalogSidebar } from '../../components/organisms/catalog/CatalogSidebar';
import { useCatalog } from '../../../application/hooks/catalog/useCatalog';
import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useState } from 'react';

export default function CatalogPage() {
  const { catalog, loading, error, fetchCatalog } = useCatalog()
  const [isFilterDrawerOpen, setIsFilterDrawerOpen] = useState(false)

  useEffect(() => {
    fetchCatalog()
  }, [fetchCatalog])

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 15 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.2, 0, 0, 1] as const } },
  }

  return (
    <Section variant="white">
      <Container>
        <Breadcrumbs />
        
        <header className="flex flex-col lg:flex-row lg:items-end justify-between gap-8 mb-16">
          <div className="max-w-3xl">
            <Badge variant="accent" className="mb-6 bg-primary/90 backdrop-blur-md text-text-inverse border-white/20 font-black px-4 py-2 uppercase tracking-widest text-label">Professional Inventory</Badge>
            <h1 className="text-h1 font-black tracking-tighter text-primary leading-tight mb-6">
              Elite Orthopedic <br />
              <span className="text-accent underline decoration-primary/5 decoration-8 underline-offset-4">Equipment</span>.
            </h1>
            <p className="text-body-lg text-text-muted font-medium leading-relaxed max-w-2xl text-balance">
              Sourcing the world's most advanced medical technology for professional healthcare institutions. 
              Vetted for surgical precision and patient safety.
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row items-center gap-6">
            <CatalogSort />
            
            <div className="flex items-center gap-3 px-6 py-3 bg-surface-muted border border-slate-100 rounded-2xl shadow-sm">
              <span className="text-body font-black text-primary uppercase tracking-widest">{catalog.length}</span>
              <span className="text-label font-bold text-text-muted uppercase tracking-widest">Available Products</span>
            </div>
            
            <Button 
              variant="secondary" 
              className="lg:hidden w-full sm:w-auto px-8 h-12 rounded-xl border border-slate-200"
              onClick={() => setIsFilterDrawerOpen(true)}
            >
              Filters
            </Button>
          </div>
        </header>

        <div className="flex flex-col lg:flex-row gap-16">
          {/* Desktop Sidebar */}
          <aside className="hidden lg:block w-72 shrink-0">
             <div className="sticky top-32">
                <CatalogSidebar />
             </div>
          </aside>

          {/* Mobile Filter Drawer */}
          <AnimatePresence>
            {isFilterDrawerOpen && (
              <>
                <motion.div 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  onClick={() => setIsFilterDrawerOpen(false)}
                  className="fixed inset-0 bg-primary/20 backdrop-blur-sm z-[110] lg:hidden"
                />
                <motion.div 
                  initial={{ x: '100%' }}
                  animate={{ x: 0 }}
                  exit={{ x: '100%' }}
                  transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                  className="fixed right-0 top-0 bottom-0 w-[85%] max-w-[400px] bg-white z-[120] p-8 shadow-2xl lg:hidden overflow-y-auto"
                >
                  <div className="flex items-center justify-between mb-12">
                    <h2 className="text-xl font-black text-primary uppercase tracking-tight">Refine Discovery</h2>
                    <button onClick={() => setIsFilterDrawerOpen(false)} className="p-2 text-text-muted">
                      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
                    </button>
                  </div>
                  <CatalogSidebar />
                </motion.div>
              </>
            )}
          </AnimatePresence>

          {/* Global Catalog Main Area */}
          <main className="flex-1">
            {loading ? (
              <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
                <LoadingSpinner />
                <p className="text-label font-black uppercase tracking-widest text-text-muted animate-pulse">
                  Syncing Global Inventory...
                </p>
              </div>
            ) : error ? (
              <motion.div 
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                className="p-12 bg-error/5 border border-error/10 rounded-[40px] text-center" 
              >
                <div className="w-20 h-20 bg-error/5 border border-error/10 rounded-full flex items-center justify-center mx-auto mb-8 text-error">
                   <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>
                </div>
                <h3 className="text-h3 font-black text-primary mb-4 tracking-tighter">Service Interruption</h3>
                <p className="text-text-muted font-medium mb-10 max-w-sm mx-auto">{error || 'Unable to establish connection with the medical database.'}</p>
                <Button 
                  onClick={() => fetchCatalog()} 
                  variant="primary"
                  className="px-10 h-14 rounded-2xl font-black uppercase tracking-widest"
                >
                  Retry Connection
                </Button>
              </motion.div>
            ) : (
              <>
                <motion.div 
                  variants={containerVariants}
                  initial="hidden"
                  animate="visible"
                >
                  <Grid cols={3} gap="lg">
                    {catalog.map((item) => (
                      <motion.div key={item.id} variants={itemVariants}>
                        <ProductCard 
                          product={item} 
                        />
                      </motion.div>
                    ))}
                  </Grid>
                </motion.div>
                
                {!loading && catalog.length === 0 && (
                  <div className="py-32 text-center bg-surface-muted rounded-[48px] border border-dashed border-slate-200">
                    <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center mx-auto mb-8 text-4xl shadow-sm">🔍</div>
                    <h3 className="text-h3 font-black text-primary mb-4 tracking-tighter">No Matching Equipment</h3>
                    <p className="text-text-muted font-medium max-w-sm mx-auto mb-10">We couldn't find any results for your current filter selection. Try adjusting your parameters.</p>
                    <Button 
                      variant="secondary"
                      onClick={() => fetchCatalog()} 
                      className="px-10 h-14 rounded-2xl font-black uppercase tracking-widest border-2"
                    >
                      Reset All Filters
                    </Button>
                  </div>
                )}
              </>
            )}
          </main>
        </div>
      </Container>
    </Section>
  )
}
