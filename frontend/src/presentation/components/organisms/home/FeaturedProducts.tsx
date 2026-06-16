import { Section, Container, Grid } from '../../atoms/layout/LayoutPrimitives';
import { ProductCard } from '../../molecules/ProductCard';
import { Button } from '../../atoms/Button';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FEATURED_PRODUCTS } from '../../../pages/home/homeData';

export const FeaturedProducts = () => {
  return (
    <Section variant="slate">
      <Container>
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-12 mb-16 lg:mb-20">
          <div className="max-w-2xl">
            <h2 className="text-h2 font-black tracking-tighter text-primary mb-6 leading-tight text-balance">
              Vetted <span className="text-accent italic">Clinical</span> <br className="hidden md:block"/>
              Surgical Supply.
            </h2>
            <p className="text-body-lg text-text-muted font-medium leading-relaxed max-w-xl">
              Precision-engineered orthopedic hardware vetted by our clinicians for performance and long-term stability.
            </p>
          </div>
          <Link to="/catalog">
            <Button variant="secondary" className="px-10 h-14 rounded-2xl border border-slate-200 bg-white text-label font-black uppercase tracking-widest hover:border-accent hover:text-accent active:scale-[0.98] transition-all">
              View All Equipment
            </Button>
          </Link>
        </div>

        <Grid cols={4} gap="lg">
          {FEATURED_PRODUCTS.map((product, idx) => (
            <motion.div
              key={product.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.1, duration: 0.4, ease: [0.2, 0, 0, 1] }}
            >
               <ProductCard product={product} />
            </motion.div>
          ))}
        </Grid>
      </Container>
    </Section>
  );
};
