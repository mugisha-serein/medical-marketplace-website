export interface NavLink {
  label: string;
  href: string;
}

export interface CatalogCategory {
  label: string;
  slug: string;
  description: string;
}

export const PRIMARY_NAV_LINKS: NavLink[] = [
  { label: 'Home', href: '/' },
  { label: 'Orders', href: '/orders' },
  { label: 'About Us', href: '/about' },
  { label: 'Contact Us', href: '/contact' },
];

export const CATALOG_CATEGORIES: CatalogCategory[] = [
  { 
    label: 'Braces & Supports', 
    slug: 'braces-supports',
    description: 'Stabilizing solutions for joints and muscles.'
  },
  { 
    label: 'Joint Implants', 
    slug: 'joint-implants',
    description: 'High-precision replacements for hips, knees, and shoulders.'
  },
  { 
    label: 'Rehabilitation Equipment', 
    slug: 'rehab-equipment',
    description: 'Tools for post-surgery and injury recovery.'
  },
  { 
    label: 'Mobility Aids', 
    slug: 'mobility-aids',
    description: 'Wheelchairs, walkers, and mobility enhancers.'
  },
  { 
    label: 'Orthopedic Instruments', 
    slug: 'orthopedic-instruments',
    description: 'Precision tools for surgical orthopedic procedures.'
  },
  { 
    label: 'Spine & Back Care', 
    slug: 'spine-back-care',
    description: 'Supportive systems for vertebral alignment and comfort.'
  },
  { 
    label: 'Pediatric Orthopedics', 
    slug: 'pediatric-orthopedics',
    description: 'Sized and designed specifically for children.'
  },
  { 
    label: 'Sports Injury Products', 
    slug: 'sports-injury',
    description: 'Elite-grade protection for active performance.'
  },
];
