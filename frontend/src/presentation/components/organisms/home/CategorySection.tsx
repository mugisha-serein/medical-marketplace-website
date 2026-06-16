import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CATEGORIES } from '../../../pages/home/homeData';
import { Section, Container, Grid } from '../../atoms/layout/LayoutPrimitives';

export const CategorySection = () => {
  return (
    <Section variant="white">
      <Container>
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-12 mb-16 lg:mb-20">
          <div className="max-w-2xl">
            <h2 className="text-h2 font-black tracking-tighter text-primary mb-6 leading-tight text-balance">
              Specialized <br className="hidden md:block"/>
              <span className="text-accent italic">Orthopedic</span> Inventory.
            </h2>
            <p className="text-body-lg text-text-muted font-medium leading-relaxed max-w-xl">
              Precision-engineered orthopedic hardware and support systems across all major clinical disciplines.
            </p>
          </div>
          <Link 
            to="/catalog" 
            className="group flex items-center gap-4 text-label font-black text-primary transition-all uppercase tracking-[0.2em] pb-1 border-b-2 border-slate-100 hover:border-accent"
          >
            Full Global Catalog
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="text-accent group-hover:translate-x-1 transition-transform"><path d="M5 12h14m-7-7 7 7-7 7"/></svg>
          </Link>
        </div>

        <Grid cols={4} gap="lg">
          {CATEGORIES.map((cat, idx) => (
            <motion.div
              key={cat.slug}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.05, duration: 0.5, ease: [0.2, 0, 0, 1] }}
            >
              <Link 
                to={`/catalog/${cat.slug}`}
                className="group relative block aspect-[4/5] overflow-hidden rounded-[40px] bg-surface-muted border border-slate-100 shadow-sm hover:shadow-2xl hover:scale-[1.02] transition-all duration-500"
              >
                <img 
                  src={cat.image} 
                  alt={cat.label} 
                  className="w-full h-full object-cover grayscale-[0.3] group-hover:grayscale-0 transition-all duration-1000 group-hover:scale-105"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-primary/95 via-primary/30 to-transparent p-10 flex flex-col justify-end">
                  <div className="translate-y-4 group-hover:translate-y-0 transition-transform duration-500">
                    <span className="inline-block px-3 py-1 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-label font-black tracking-widest text-text-inverse uppercase mb-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                      {cat.count} Certified Items
                    </span>
                    <h3 className="text-2xl font-black text-text-inverse mb-2 leading-[0.9] pr-4">{cat.label}</h3>
                    <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-all duration-500 delay-100">
                      <span className="text-label font-black text-accent uppercase tracking-widest">Browse Series</span>
                    </div>
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </Grid>

      </Container>
    </Section>
  );
};
