import { useProductStore } from '../../../../core/store/productSlice';
import { CATEGORIES } from '../../../pages/home/homeData';


export const CatalogSidebar = () => {
  const { filters, setFilters, resetFilters } = useProductStore();

  const handleCategoryChange = (slug: string) => {
    setFilters({ categoryId: filters.categoryId === slug ? undefined : slug });
  };

  const conditions = ['New', 'Refurbished', 'Open Box'];

  return (
    <div className="space-y-10 group">
      {/* Categories Section */}
      <div>
        <h3 className="text-[13px] font-black uppercase tracking-widest text-primary mb-6 flex items-center justify-between">
          Specialties
          <span className="w-8 h-px bg-slate-200" />
        </h3>
        <div className="space-y-2">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.slug}
              onClick={() => handleCategoryChange(cat.slug)}
              className={`w-full flex items-center justify-between p-3 rounded-xl transition-all duration-300 ${
                filters.categoryId === cat.slug 
                  ? 'bg-accent text-white shadow-lg shadow-accent/20' 
                  : 'text-text-muted hover:bg-slate-50'
              }`}
            >
              <span className="text-[13px] font-bold">{cat.label}</span>
              <span className={`text-[10px] font-black px-2 py-0.5 rounded-full ${
                filters.categoryId === cat.slug ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-400'
              }`}>
                {cat.count}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Condition Filter */}
      <div>
        <h3 className="text-[13px] font-black uppercase tracking-widest text-primary mb-6 flex items-center justify-between">
          Condition
          <span className="w-8 h-px bg-slate-200" />
        </h3>
        <div className="space-y-3">
          {conditions.map((condition) => (
            <label key={condition} className="flex items-center gap-3 cursor-pointer group/label">
              <div className="relative flex items-center justify-center w-5 h-5 rounded-md border-2 border-slate-200 group-hover/label:border-accent transition-colors">
                <input type="checkbox" className="sr-only p-0" />
                <div className="w-2.5 h-2.5 rounded-sm bg-accent opacity-0 transition-opacity" />
              </div>
              <span className="text-[14px] font-medium text-text-muted group-hover/label:text-primary transition-colors">{condition}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Availability */}
      <div>
        <h3 className="text-[13px] font-black uppercase tracking-widest text-primary mb-6 flex items-center justify-between">
          Stock Status
          <span className="w-8 h-px bg-slate-200" />
        </h3>
        <button 
          onClick={() => setFilters({ inStockOnly: !filters.inStockOnly })}
          className="flex items-center gap-3 w-full group/toggle"
        >
          <div className={`w-10 h-6 rounded-full transition-colors relative flex items-center ${filters.inStockOnly ? 'bg-accent' : 'bg-slate-200'}`}>
            <div className={`w-4 h-4 rounded-full bg-white shadow-sm transition-transform mx-1 ${filters.inStockOnly ? 'translate-x-4' : 'translate-x-0'}`} />
          </div>
          <span className="text-[14px] font-bold text-text-muted">In Stock Only</span>
        </button>
      </div>

      {/* Reset Action */}
      <div className="pt-6">
        <button 
          onClick={resetFilters}
          className="w-full py-4 rounded-2xl border-2 border-dashed border-slate-200 text-[12px] font-black uppercase tracking-widest text-text-muted hover:border-accent hover:text-accent transition-all duration-300"
        >
          Clear All Filters
        </button>
      </div>
    </div>
  );
};
