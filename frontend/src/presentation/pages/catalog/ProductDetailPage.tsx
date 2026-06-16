import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { fetchProductBySlug } from '../../../api/catalog';
import { type Equipment } from '../../../domain/entities/Equipment';
import { Breadcrumbs } from '../../components/atoms/Breadcrumbs';
import { Badge } from '../../components/atoms/Badge';
import { Button } from '../../components/atoms/Button';
import { LoadingSpinner } from '../../components/atoms/LoadingSpinner';
import { Section, Container, Grid } from '../../components/atoms/layout/LayoutPrimitives';

export default function ProductDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const [product, setProduct] = useState<Equipment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeImage, setActiveImage] = useState(0);
  const [activeTab, setActiveTab] = useState<'specs' | 'regulatory' | 'shipping'>('specs');

  useEffect(() => {
    const loadProduct = async () => {
      if (!slug) return;
      setLoading(true);
      try {
        const data = await fetchProductBySlug(slug);
        setProduct(data);
      } catch (err: any) {
        setError(err.message || 'Equipment profile not found.');
      } finally {
        setLoading(false);
      }
    };
    loadProduct();
  }, [slug]);

  if (loading) return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
      <LoadingSpinner />
      <p className="text-label font-black uppercase tracking-widest text-text-muted animate-pulse">Retrieving Medical Profile...</p>
    </div>
  );

  if (error || !product) return (
    <div className="py-24 text-center max-w-xl mx-auto">
      <div className="w-20 h-20 bg-error/5 border border-error/10 rounded-full flex items-center justify-center mx-auto mb-8 text-error">
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>
      </div>
      <h1 className="text-h3 font-black text-primary mb-4 tracking-tighter">Profile Access Error</h1>
      <p className="text-text-muted font-medium mb-10">{error || 'This equipment is no longer in our active database.'}</p>
      <Button variant="primary" onClick={() => navigate('/catalog')} className="px-10 h-14 rounded-2xl">Return to Catalog</Button>
    </div>
  );

  const formattedPrice = (product.priceCents / 100).toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
  });

  return (
    <Section variant="white" className="min-h-screen">
      <Container>
        <Breadcrumbs />

        <Grid cols={12} gap="xl">
          {/* Left: Medical Gallery */}
          <div className="lg:col-span-7 space-y-6">
            <motion.div 
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              className="aspect-square rounded-[48px] overflow-hidden bg-surface-muted border border-slate-100 shadow-premium group relative"
            >
              <AnimatePresence mode="wait">
                <motion.img
                  key={activeImage}
                  src={product.images[activeImage]}
                  alt={product.name}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.5 }}
                  className="w-full h-full object-cover"
                />
              </AnimatePresence>
              
              {/* Certification Floating Badges */}
              <div className="absolute top-8 left-8 flex flex-col gap-3">
                <Badge variant="success" className="bg-emerald-500/90 backdrop-blur-md text-text-inverse border-white/20 font-black px-4 py-2 shadow-xl">ISO 13485 Certified</Badge>
                <Badge variant="accent" className="bg-primary/90 backdrop-blur-md text-text-inverse border-white/20 font-black px-4 py-2 shadow-xl">CE Medical Grade</Badge>
              </div>
            </motion.div>

            <div className="grid grid-cols-4 gap-4">
              {product.images.map((img, idx) => (
                <button
                  key={idx}
                  onClick={() => setActiveImage(idx)}
                  className={`aspect-square rounded-3xl overflow-hidden border-2 transition-all duration-300 ${
                    activeImage === idx ? 'border-accent shadow-lg scale-95' : 'border-transparent opacity-60 hover:opacity-100'
                  }`}
                >
                  <img src={img} alt={`${product.name} view ${idx}`} className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          </div>

          {/* Right: Procurement Panel */}
          <div className="lg:col-span-5 flex flex-col">
            <div className="mb-10">
              <div className="flex items-center gap-4 mb-6">
                <span className="text-label font-black text-slate-300 uppercase tracking-widest">Global Catalog / {product.categoryId.replace(/-/g, ' ')}</span>
                <div className="h-1 flex-1 bg-slate-100 rounded-full" />
              </div>
              <h1 className="text-h1 font-black tracking-tighter text-primary leading-tight mb-6 text-balance">
                {product.name}
              </h1>
              <div className="flex items-center gap-6">
                 <div className="flex items-center gap-2 px-4 py-2 bg-warning/5 border border-warning/10 rounded-full">
                    <span className="text-warning text-lg">★</span>
                    <span className="text-body-sm font-black text-primary">{product.rating || '5.0'}</span>
                 </div>
                 <span className="text-label font-bold text-text-muted">Certified Clinician Reviews</span>
              </div>
            </div>

            <p className="text-body-lg text-text-muted font-medium leading-relaxed mb-12">
              {product.description}
            </p>

            <div className="p-10 rounded-[40px] bg-surface-muted border border-slate-100 mb-12 shadow-sm">
              <div className="flex flex-col mb-10">
                <span className="text-label font-black text-text-muted uppercase tracking-widest mb-2">Institutional Pricing</span>
                <div className="flex items-baseline gap-2">
                  <span className="text-5xl font-black text-primary tracking-tighter">{formattedPrice}</span>
                  <span className="text-label font-bold text-text-muted uppercase tracking-widest">per unit</span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Button size="lg" className="h-16 rounded-2xl bg-primary text-text-inverse font-black uppercase text-label tracking-widest shadow-xl shadow-primary/20 hover:scale-[1.02] transition-all">
                  Add to Procurement
                </Button>
                <Button variant="secondary" className="h-16 rounded-2xl border-2 border-slate-200 text-primary font-black uppercase text-label tracking-widest hover:border-accent hover:text-accent transition-all">
                  Request Bulk Quote
                </Button>
              </div>
              
              <div className="mt-8 pt-8 border-t border-slate-200 flex items-center justify-between text-label font-bold text-text-muted uppercase tracking-widest">
                <div className="flex items-center gap-2">
                   <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                   In Stock: {product.stock} units
                </div>
                <span>Ships globally in 48h</span>
              </div>
            </div>

            {/* Technical Blueprint Tabs */}
            <div className="mt-auto">
              <div className="flex border-b border-slate-100 mb-8 overflow-x-auto whitespace-nowrap scrollbar-hide">
                {(['specs', 'regulatory', 'shipping'] as const).map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-8 py-4 text-label font-black uppercase tracking-widest transition-all relative ${
                      activeTab === tab ? 'text-accent' : 'text-text-muted hover:text-primary'
                    }`}
                  >
                    {tab}
                    {activeTab === tab && (
                      <motion.div layoutId="activeTab" className="absolute bottom-0 left-0 right-0 h-1 bg-accent rounded-full" />
                    )}
                  </button>
                ))}
              </div>

              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-4"
              >
                {activeTab === 'specs' && (
                  <div className="grid grid-cols-2 gap-y-4">
                    {Object.entries(product.specifications).map(([key, value]) => (
                      <div key={key}>
                        <p className="text-label font-black text-text-muted uppercase tracking-widest mb-1">{key}</p>
                        <p className="text-body-sm font-bold text-primary">{value}</p>
                      </div>
                    ))}
                  </div>
                )}
                {activeTab === 'regulatory' && (
                  <div className="space-y-4">
                     <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-100 flex gap-4 items-center">
                        <div className="w-10 h-10 rounded-full bg-emerald-500 text-text-inverse flex items-center justify-center shrink-0">✓</div>
                        <p className="text-body-sm font-bold text-emerald-800">Meets all European Commission MDR requirements for Class III Medical Devices.</p>
                     </div>
                     <p className="text-body-sm text-text-muted font-medium italic">Complete clinical evaluation report available upon institutional request.</p>
                  </div>
                )}
                {activeTab === 'shipping' && (
                  <p className="text-body-sm text-text-muted font-medium">Global temperature-controlled logistics available. Standard lead time: 3-5 business days for domestic, 7-14 days for international institutional orders.</p>
                )}
              </motion.div>
            </div>
          </div>
        </Grid>
      </Container>
    </Section>

  );
}
