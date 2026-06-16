import type { Equipment } from '../../../domain/entities/Equipment';

export interface CategoryCard {
  label: string;
  slug: string;
  count: number;
  image: string;
}

export const CATEGORIES: CategoryCard[] = [
  { label: 'Braces & Supports', slug: 'braces-supports', count: 124, image: 'https://images.unsplash.com/photo-1597452485669-2c7bb5fef90d?auto=format&fit=crop&q=80&w=400' },
  { label: 'Joint Implants', slug: 'joint-implants', count: 86, image: 'https://images.unsplash.com/photo-1579154235884-332c24afb56d?auto=format&fit=crop&q=80&w=400' },
  { label: 'Rehabilitation Equipment', slug: 'rehab-equipment', count: 54, image: 'https://images.unsplash.com/photo-1576091160399-112df8d25d1d?auto=format&fit=crop&q=80&w=400' },
  { label: 'Mobility Aids', slug: 'mobility-aids', count: 92, image: 'https://images.unsplash.com/photo-1591033594798-33227a05780d?auto=format&fit=crop&q=80&w=400' },
  { label: 'Orthopedic Instruments', slug: 'orthopedic-instruments', count: 42, image: 'https://images.unsplash.com/photo-1583324113626-70df0f4ecdac?auto=format&fit=crop&q=80&w=400' },
  { label: 'Spine & Back Care', slug: 'spine-back-care', count: 75, image: 'https://images.unsplash.com/photo-1532938911079-1b06ac7ceec7?auto=format&fit=crop&q=80&w=400' },
  { label: 'Pediatric Orthopedics', slug: 'pediatric-orthopedics', count: 38, image: 'https://images.unsplash.com/photo-1516627145497-ae6b5869137c?auto=format&fit=crop&q=80&w=400' },
  { label: 'Sports Injury Products', slug: 'sports-injury', count: 110, image: 'https://images.unsplash.com/photo-1593114144299-2b24da72c009?auto=format&fit=crop&q=80&w=400' },
];

export const FEATURED_PRODUCTS: Equipment[] = [
  {
    id: 'prod-1',
    name: 'PrecisionFlex Titanium Knee System',
    description: 'Elite grade titanium alloy knee implant for high-activity patients.',
    priceCents: 1250000,
    images: ['https://images.unsplash.com/photo-1583324113626-70df0f4ecdac?auto=format&fit=crop&q=80&w=800'],
    categoryId: 'joint-implants',
    vendorId: 'active-life',
    stock: 12,
    specifications: { material: 'Titanium Ti-6Al-4V', finish: 'Mirror Polished' },
    rating: 4.9
  },
  {
    id: 'prod-2',
    name: 'AeroPostural Back Support',
    description: 'Advanced breathable mesh back support with ergonomic alignment struts.',
    priceCents: 18500,
    images: ['https://images.unsplash.com/photo-1532938911079-1b06ac7ceec7?auto=format&fit=crop&q=80&w=800'],
    categoryId: 'spine-back-care',
    vendorId: 'active-life',
    stock: 45,
    specifications: { weight: '1.2kg', material: 'Breathable Mesh' },
    rating: 4.8
  },
  {
    id: 'prod-3',
    name: 'UltraGrip Walker Pro',
    description: 'Lightweight aluminum walker with high-traction solid rubber feet.',
    priceCents: 32000,
    images: ['https://images.unsplash.com/photo-1591033594798-33227a05780d?auto=format&fit=crop&q=80&w=800'],
    categoryId: 'mobility-aids',
    vendorId: 'active-life',
    stock: 28,
    specifications: { capacity: '150kg', material: 'Anodized Aluminum' },
    rating: 4.7
  },
  {
    id: 'prod-4',
    name: 'StabiloForce Compression Sleeve',
    description: 'Professional grade compression for acute injury management.',
    priceCents: 4500,
    images: ['https://images.unsplash.com/photo-1597452485669-2c7bb5fef90d?auto=format&fit=crop&q=80&w=800'],
    categoryId: 'braces-supports',
    vendorId: 'active-life',
    stock: 156,
    specifications: { compression: '20-30 mmHg', sizes: 'S, M, L, XL' },
    rating: 4.6
  }
];
