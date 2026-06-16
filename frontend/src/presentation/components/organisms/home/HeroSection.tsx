import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Section, Container, Grid } from '../../atoms/layout/LayoutPrimitives';
import { Button } from '../../atoms/Button';

export const HeroSection = () => {
  return (
    <Section variant="white" noPadding className="relative min-h-[90vh] flex items-center">
      {/* Structural Backdrop */}
      <div className="absolute top-0 right-0 w-2/3 h-full opacity-[0.03] pointer-events-none overflow-hidden -z-0">
        <svg viewBox="0 0 400 400" className="w-full h-full text-accent" fill="currentColor">
          <circle cx="300" cy="100" r="200" fill="none" stroke="currentColor" strokeWidth="0.5" />
          <path d="M0 400 Q200 200 400 400" stroke="currentColor" strokeWidth="1" fill="none" />
        </svg>
      </div>

      <Container>
        <Grid cols={2} gap="xl" alignItems="center" className="lg:grid-cols-2">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: [0.2, 0, 0, 1] }}
            className="z-10 relative"
          >
            <div className="inline-flex items-center gap-3 px-3 py-1.5 rounded-full bg-slate-50 border border-slate-100 mb-8 max-w-fit">
              <div className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
              <span className="text-[10px] font-black tracking-[0.2em] uppercase text-slate-500">Inventory Status: Certified Active</span>
            </div>

            <h1 className="text-[clamp(2.5rem,7vw,4.5rem)] font-black tracking-tighter text-primary leading-[0.85] mb-8 max-w-2xl">
              Precision <span className="text-accent italic">Joint Implants</span> <br className="hidden md:block" />
              & Advanced Recovery Support.
            </h1>

            <p className="text-lg md:text-xl text-text-muted leading-relaxed max-w-xl mb-6 font-medium">
              Supplying certified orthopedic equipment to hospitals, clinics, and individuals. From spine supports to specialized surgical hardware.
            </p>

            <div className="flex flex-col sm:flex-row gap-5 mb-14">
              <Link to="/catalog">
                <Button
                  size="lg"
                  variant="primary"
                  className="w-full sm:w-auto px-10 h-16 rounded-2xl shadow-xl shadow-primary/10 transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl active:scale-[0.98]"
                >
                  Shop Orthopedic Equipment
                </Button>
              </Link>
              <Link to="/catalog">
                <Button
                  size="lg"
                  variant="secondary"
                  className="w-full sm:w-auto px-10 h-16 rounded-2xl border border-slate-200 bg-white text-primary/70 hover:text-primary transition-all duration-300 hover:border-slate-300 active:scale-[0.98]"
                >
                  Explore Categories
                </Button>
              </Link>
            </div>

            {/* Trust Strip */}
            <div className="flex flex-wrap items-center gap-x-10 gap-y-4 pt-10 border-t border-slate-100">
              <div className="flex items-center gap-3 opacity-60">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-accent"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" /></svg>
                <span className="text-[11px] font-black uppercase tracking-widest text-primary">ISO Certified</span>
              </div>
              <div className="flex items-center gap-3 opacity-60">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-accent"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" /></svg>
                <span className="text-[11px] font-black uppercase tracking-widest text-primary">Medical-Grade</span>
              </div>
              <div className="flex items-center gap-3 opacity-60">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-accent"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M22 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" /></svg>
                <span className="text-[11px] font-black uppercase tracking-widest text-primary">Trusted by Clinics</span>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.98, x: 20 }}
            animate={{ opacity: 1, scale: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.1, ease: [0.2, 0, 0, 1] }}
            className="relative hidden lg:block h-[600px]"
          >
            {/* Layered Composition */}
            <motion.div
              whileHover={{ scale: 1.02, y: -5 }}
              transition={{ duration: 0.4 }}
              className="absolute top-0 right-0 w-[85%] aspect-square rounded-[40px] overflow-hidden shadow-2xl z-10 border border-slate-100"
            >
              <img
                src="https://images.unsplash.com/photo-1579154235884-332c24afb56d?auto=format&fit=crop&q=80&w=1000"
                alt="Advanced Implant Technology"
                className="w-full h-full object-cover grayscale-[0.2] hover:grayscale-0 transition-all duration-700"
              />
            </motion.div>

            <motion.div
              whileHover={{ y: 5, x: -5 }}
              className="absolute -bottom-8 -left-8 w-[60%] aspect-[4/3] rounded-[32px] overflow-hidden shadow-2xl z-20 border-4 border-white"
            >
              <img
                src="https://images.unsplash.com/photo-1583324113626-70df0f4ecdac?auto=format&fit=crop&q=80&w=600"
                alt="Orthopedic Support Product"
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-primary/10" />
            </motion.div>

            {/* Minimalist Glass Card */}
            <div className="absolute top-12 -left-12 p-6 glass rounded-2xl border border-white/40 shadow-xl z-30 max-w-[190px] backdrop-blur-md">
              <p className="text-[11px] font-black text-primary uppercase tracking-widest mb-2">Specifications</p>
              <p className="text-[12px] font-bold text-text-muted leading-tight">High-fidelity Titanium Alloy Grade 5</p>
            </div>

            <div className="absolute bottom-12 right-12 p-6 glass rounded-2xl border border-white/40 shadow-xl z-30 backdrop-blur-md">
              <p className="text-2xl font-black text-accent leading-none">ISO</p>
              <p className="text-[10px] font-bold text-text-muted uppercase tracking-tighter mt-1">13485:2016</p>
            </div>
          </motion.div>
        </Grid>
      </Container>
    </Section>
  );
};
