import { HeroSection } from '../../components/organisms/home/HeroSection';
import { TrustSection } from '../../components/organisms/home/TrustSection';
import { CategorySection } from '../../components/organisms/home/CategorySection';
import { FeaturedProducts } from '../../components/organisms/home/FeaturedProducts';
import { AboutSection, WhyChooseUs } from '../../components/organisms/home/AboutSections';
import { CTASection } from '../../components/organisms/home/CTASection';
import { motion } from 'framer-motion';

const HomePage = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex flex-col overflow-x-hidden"
    >
      <HeroSection />
      <TrustSection />
      <CategorySection />
      <FeaturedProducts />
      <AboutSection />
      <WhyChooseUs />
      <CTASection />
    </motion.div>
  );
};

export default HomePage;
