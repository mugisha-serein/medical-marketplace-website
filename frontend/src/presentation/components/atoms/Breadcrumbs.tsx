import { Link, useLocation } from 'react-router-dom';

export const Breadcrumbs = () => {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter((x) => x);

  return (
    <nav className="flex mb-8 items-center gap-2 overflow-x-auto whitespace-nowrap scrollbar-hide pb-2">
      <Link 
        to="/" 
        className="text-[11px] font-black uppercase tracking-widest text-text-muted hover:text-accent transition-colors"
      >
        Home
      </Link>
      
      {pathnames.map((name, index) => {
        const routeTo = `/${pathnames.slice(0, index + 1).join('/')}`;
        const isLast = index === pathnames.length - 1;

        return (
          <div key={name} className="flex items-center gap-2">
            <span className="text-slate-300 font-bold select-none">/</span>
            {isLast ? (
              <span className="text-[11px] font-black uppercase tracking-widest text-accent">
                {name.replace(/-/g, ' ')}
              </span>
            ) : (
              <Link 
                to={routeTo} 
                className="text-[11px] font-black uppercase tracking-widest text-text-muted hover:text-accent transition-colors"
              >
                {name.replace(/-/g, ' ')}
              </Link>
            )}
          </div>
        );
      })}
    </nav>
  );
};
