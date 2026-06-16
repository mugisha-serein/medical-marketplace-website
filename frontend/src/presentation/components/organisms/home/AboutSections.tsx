import { motion } from 'framer-motion';
import { Section, Container, Grid } from '../../atoms/layout/LayoutPrimitives';

export const AboutSection = () => {
  const points = [
    { title: 'Clinical Precision', text: 'Vetted by orthopedic specialists for anatomical accuracy.' },
    { title: 'Global Compliance', text: 'Strictest adherence to international medical device regulations.' },
    { title: 'Surgical Outcomes', text: 'Designed to optimize recovery times and surgical success.' }
  ];

  return (
    <Section variant="white">
      <Container>
        <Grid cols={12} gap="xl" alignItems="center">
          <motion.div
             initial={{ opacity: 0, x: -30 }}
             whileInView={{ opacity: 1, x: 0 }}
             viewport={{ once: true }}
             transition={{ duration: 0.8, ease: [0.2, 0, 0, 1] }}
            className="lg:col-span-7 relative"
          >
            <div className="aspect-[16/10] rounded-[48px] overflow-hidden shadow-premium group border border-slate-100">
              <img 
                src="https://images.unsplash.com/photo-1516062423079-7ca13cdc7f5a?auto=format&fit=crop&q=80&w=1200" 
                alt="Medical Consultation"
                className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-105"
              />
            </div>
            
            <motion.div 
              whileHover={{ y: -5, scale: 1.02 }}
              className="absolute -bottom-10 -right-6 lg:-right-12 p-10 glass rounded-[40px] shadow-2xl border border-white/40 hidden md:block max-w-[340px] z-10 backdrop-blur-xl"
            >
              <p className="text-[17px] font-black tracking-tight text-primary leading-tight mb-4 italic">"We don't just supply equipment; we enable the movement of a global workforce."</p>
              <div className="flex items-center gap-3">
                 <div className="w-8 h-px bg-accent" />
                 <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Institutional Health Board</p>
              </div>
            </motion.div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, ease: [0.2, 0, 0, 1] }}
            className="lg:col-span-5"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface-muted border border-slate-100 mb-8 max-w-fit">
              <div className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
              <span className="text-label font-black tracking-[0.2em] uppercase text-text-muted">Corporate Integrity</span>
            </div>
            <h2 className="text-h2 font-black tracking-tighter text-primary mb-10 leading-tight text-balance">
              The Science of <br />
              <span className="text-accent italic">Movement</span> Restored.
            </h2>
            <p className="text-body-lg text-text-muted leading-relaxed font-medium mb-12 max-w-xl">
              Active Life Medical Ltd bridges the gap between surgical complexity and patient simplicity. Our supply chain is built on clinical vetting and global compliance.
            </p>
            
            <div className="space-y-10">
              {points.map((p, idx) => (
                <div key={idx} className="flex gap-6 items-start group">
                  <div className="w-10 h-10 rounded-2xl bg-surface-muted border border-slate-100 flex items-center justify-center shrink-0 text-accent group-hover:bg-accent/5 group-hover:border-accent/20 transition-all">
                     <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                  </div>
                  <div>
                    <h4 className="text-label font-black uppercase tracking-[0.15em] text-primary mb-2">{p.title}</h4>
                    <p className="text-body-sm text-text-muted font-medium leading-relaxed max-w-sm">{p.text}</p>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </Grid>
      </Container>
    </Section>
  );
};

export const WhyChooseUs = () => {
    const features = [
      { id: '01', title: 'Certified Quality', text: 'All products undergo rigorous testing according to ISO 13485 standards.' },
      { id: '02', title: 'Specialized Supply', text: 'Strictly orthopedic. We understand the nuances of joint dynamics.' },
      { id: '03', title: 'Global Logistics', text: 'Fast delivery for time-critical surgical hardware worldwide.' },
      { id: '04', title: 'Expert Consult', text: 'Direct access to equipment specialists for clinical procurement.' }
    ];

    return (
      <Section variant="primary" className="relative">
        {/* Glow effect */}
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-accent/10 rounded-full blur-[120px] -z-0 -translate-y-1/2 translate-x-1/2" />
        
        <Container className="relative z-10">
          <Grid cols={4} gap="xl" alignItems="end">
            <div className="lg:col-span-1 mb-8 lg:mb-0">
               <div className="inline-block px-3 py-1 rounded-full bg-white/5 border border-white/10 text-label font-black uppercase tracking-widest text-accent mb-6">Strategic Partner</div>
               <h2 className="text-h2 font-black tracking-tighter mb-8 leading-tight text-balance">The <br/><span className="text-accent italic">Edge</span> In <br/>Supply.</h2>
               <p className="text-text-inverse/40 text-[16px] font-medium leading-relaxed max-w-[240px]">
                 Optimizing clinical outcomes through high-fidelity hardware.
               </p>
            </div>
            {features.map((f, idx) => (
              <motion.div 
                key={f.id}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1, duration: 0.6, ease: [0.2, 0, 0, 1] }}
                className="lg:col-span-1 p-10 rounded-[40px] bg-white/[0.03] border border-white/[0.05] hover:bg-white/[0.07] hover:border-white/[0.1] transition-all duration-500 hover:scale-[1.02] group"
              >
                <p className="text-5xl font-black text-white/5 mb-8 group-hover:text-accent/20 transition-colors uppercase italic tracking-tighter">{f.id}</p>
                <h3 className="text-h4 font-black tracking-tight mb-4 group-hover:text-accent transition-colors">{f.title}</h3>
                <p className="text-text-inverse/50 text-body-sm font-medium leading-relaxed">{f.text}</p>
              </motion.div>
            ))}
          </Grid>

        </Container>
      </Section>
    );
};