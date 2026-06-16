import { Section, Container } from '../../atoms/layout/LayoutPrimitives';
import { Button } from '../../atoms/Button';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

export const CTASection = () => {
  return (
    <Section variant="white">
      <Container>
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, ease: [0.2, 0, 0, 1] }}
          className="relative bg-primary rounded-[56px] p-10 md:p-20 lg:p-32 overflow-hidden shadow-2xl border border-white/5"
        >
          {/* Decorative Mesh Background */}
          <div className="absolute inset-0 opacity-[0.1] pointer-events-none">
            <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
              <pattern id="cta-grid" width="80" height="80" patternUnits="userSpaceOnUse">
                <path d="M 80 0 L 0 0 0 80" fill="none" stroke="white" strokeWidth="0.5" />
              </pattern>
              <rect width="100%" height="100%" fill="url(#cta-grid)" />
            </svg>
          </div>

          <div className="relative z-10 flex flex-col items-center text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-label font-black uppercase tracking-[0.2em] text-accent mb-10">Institutional Supply</div>
            
            <h2 className="text-h1 font-black tracking-tighter text-text-inverse mb-8 leading-tight text-balance">
              Enable the <span className="text-accent italic">Future</span> of <br className="hidden md:block"/> Clinical Procurement.
            </h2>
            
            <p className="text-text-inverse/50 text-body-lg font-medium leading-relaxed mb-14 max-w-2xl">
              Join thousands of healthcare institutions who trust Active Life Medical Ltd for their core surgical supply chain. Certified quality, global logistics, and professional-grade support.
            </p>
            
            <div className="flex flex-col sm:flex-row justify-center gap-6 w-full sm:w-auto">
              <Link to="/catalog">
                <Button size="lg" variant="primary" className="w-full sm:w-auto px-12 h-16 rounded-2xl bg-accent text-text-inverse font-black uppercase tracking-widest text-label shadow-2xl shadow-accent/40 transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]">
                  Browse Procurement Catalog
                </Button>
              </Link>
              <Link to="/register">
                <Button size="lg" className="w-full sm:w-auto px-12 h-16 rounded-2xl bg-white/5 border border-white/10 text-text-inverse font-black uppercase tracking-widest text-label hover:bg-white/10 transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]">
                  Open Professional Account
                </Button>
              </Link>
            </div>
          </div>

          {/* Strategic atmospheric shapes */}
          <div className="absolute top-0 right-0 -translate-y-1/2 translate-x-1/2 w-[600px] h-[600px] bg-accent/30 rounded-full blur-[160px] pointer-events-none opacity-50" />
          <div className="absolute bottom-0 left-0 translate-y-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-accent/10 rounded-full blur-[160px] pointer-events-none" />
        </motion.div>
      </Container>
    </Section>
  );
};
