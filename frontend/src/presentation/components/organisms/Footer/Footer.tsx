import { Link } from 'react-router-dom';


export const Footer = () => {
  const currentYear = new Date().getFullYear();

  const footerLinks = [
    {
      title: 'Solutions',
      links: [
        { label: 'Braces & Supports', href: '/catalog/braces-supports' },
        { label: 'Joint Implants', href: '/catalog/joint-implants' },
        { label: 'Spine & Back Care', href: '/catalog/spine-back-care' },
        { label: 'Rehabilitation', href: '/catalog/rehab-equipment' },
      ],
    },
    {
      title: 'Support',
      links: [
        { label: 'Customer Service', href: '/support' },
        { label: 'Delivery Info', href: '/delivery' },
        { label: 'Returns & Refunds', href: '/returns' },
        { label: 'Medical Resources', href: '/resources' },
      ],
    },
    {
      title: 'Company',
      links: [
        { label: 'About Us', href: '/about' },
        { label: 'Partnerships', href: '/partners' },
        { label: 'Compliance', href: '/compliance' },
        { label: 'Contact', href: '/contact' },
      ],
    },
  ];

  return (
    <footer className="bg-primary text-white pt-24 pb-12">
      <div className="w-full px-4 md:px-12 lg:px-24">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-12 mb-20">
          <div className="lg:col-span-2">
            <Link to="/" className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-accent flex items-center justify-center text-white font-black shadow-lg">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M11 2a2 2 0 0 0-2 2v5H4a2 2 0 0 0-2 2v2c0 1.1.9 2 2 2h5v5c0 1.1.9 2 2 2h2a2 2 0 0 0 2-2v-5h5a2 2 0 0 0 2-2v-2a2 2 0 0 0-2-2h-5V4a2 2 0 0 0-2-2h-2z"/></svg>
              </div>
              <span className="text-2xl font-black tracking-tighter uppercase">Active Life</span>
            </Link>
            <p className="text-text-muted text-sm leading-relaxed max-w-sm mb-8">
              Pioneering orthopedic excellence since 1998. We provide world-class medical devices and rehabilitation solutions to healthcare professionals and individuals worldwide.
            </p>
            <div className="flex gap-4">
              {/* Social Placeholders */}
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="w-9 h-9 rounded-full bg-white/5 border border-white/10 flex items-center justify-center hover:bg-accent/20 hover:border-accent/40 transition-colors cursor-pointer">
                  <div className="w-4 h-4 bg-white/40 rounded-sm" />
                </div>
              ))}
            </div>
          </div>

          {footerLinks.map((section) => (
            <div key={section.title}>
              <h4 className="text-[13px] font-black uppercase tracking-widest text-accent mb-6">
                {section.title}
              </h4>
              <ul className="space-y-4">
                {section.links.map((link) => (
                  <li key={link.label}>
                    <Link 
                      to={link.href} 
                      className="text-white/60 hover:text-white transition-colors text-[14px] font-medium"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="pt-12 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2 opacity-40">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
            <span className="text-[10px] font-black tracking-[0.2em] uppercase text-white">ISO 13485 CERTIFIED</span>
          </div>
          
          <p className="text-white/30 text-[12px] font-bold">
            &copy; {currentYear} Active Life Medical Ltd. All rights reserved.
          </p>

          <div className="flex gap-8 text-[12px] font-bold text-white/30">
            <Link to="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link>
            <Link to="/terms" className="hover:text-white transition-colors">Terms of Service</Link>
          </div>
        </div>
      </div>
    </footer>
  );
};
