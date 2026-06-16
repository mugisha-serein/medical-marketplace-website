import { motion } from 'framer-motion';
import { Section, Container, Grid } from '../../atoms/layout/LayoutPrimitives';

export const TrustSection = () => {
  const indicators = [
    {
      label: 'MDR Compliant',
      description: 'Fully compliant with EU Medical Device Regulation and ISO 13485 standards.',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
      )
    },
    {
      label: 'Institutional Supply',
      description: 'Preferred fulfillment partner for surgical clinics and secondary care units.',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M22 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
      )
    },
    {
      label: 'Biocompatible Grade',
      description: 'Advanced testing for implant safety, performance, and hardware load-bearing.',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
      )
    }
  ];

  return (
    <Section variant="white" className="border-y border-slate-100">
      <Container>
        <Grid cols={3} gap="xl">
          {indicators.map((item, idx) => (
            <motion.div
              key={item.label}
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.1, duration: 0.4, ease: [0.2, 0, 0, 1] }}
              className="flex items-start gap-6 group"
            >
              <div className="w-12 h-12 shrink-0 rounded-2xl bg-slate-50 border border-slate-100 flex items-center justify-center text-accent/60 group-hover:text-accent group-hover:bg-accent/5 group-hover:border-accent/20 transition-all duration-500">
                {item.icon}
              </div>
              <div className="pt-1">
                <h3 className="text-label font-black text-primary uppercase tracking-[0.2em] mb-3">{item.label}</h3>
                <p className="text-body-sm text-text-muted leading-relaxed font-medium max-w-[260px]">{item.description}</p>
              </div>
            </motion.div>
          ))}
        </Grid>
      </Container>
    </Section>
  );
};
