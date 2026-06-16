import { useNavigate } from 'react-router-dom'
import type { Equipment } from '../../../domain/entities/Equipment'
import { Card } from '../atoms/Card'
import { Badge } from '../atoms/Badge'
import { Button } from '../atoms/Button'
import { motion } from 'framer-motion'

interface ProductCardProps {
  product: Equipment
  onAddToCart?: (id: string) => void
  onViewDetails?: (id: string) => void
}

export function ProductCard({ product, onAddToCart, onViewDetails }: ProductCardProps) {
  const navigate = useNavigate()
  const isOutOfStock = product.stock === 0
  const formattedPrice = (product.priceCents / 100).toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
  })

  const handleViewDetails = () => {
    if (onViewDetails) {
      onViewDetails(product.id)
    } else {
      navigate(`/catalog/${product.id}`)
    }
  }

  return (
    <Card 
      className="flex flex-col h-full group bg-white border border-slate-100 rounded-[32px] overflow-hidden hover:shadow-premium hover:scale-[1.02] transition-all duration-300" 
      padding="none" 
      onClick={handleViewDetails}
    >
      {/* High-End Image Container */}
      <div className="relative w-full aspect-square overflow-hidden bg-slate-50">
        <motion.img
          src={product.images[0] ?? 'https://placehold.co/400x300?text=No+Image'}
          alt={product.name}
          className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
        />
        <div className="absolute top-6 left-6 flex flex-col gap-2">
          <Badge variant="accent" className="bg-accent/90 backdrop-blur-md border border-white/20 text-[10px] uppercase font-black px-3 py-1.5 shadow-sm">{product.categoryId.replace(/-/g, ' ')}</Badge>
          {product.condition === 'new' && <Badge variant="success" className="bg-emerald-500/90 backdrop-blur-md border border-white/20 text-[10px] uppercase font-black px-3 py-1.5 shadow-sm">New</Badge>}
        </div>
        
        {isOutOfStock && (
          <div className="absolute inset-0 bg-white/60 flex items-center justify-center backdrop-blur-[6px]">
            <Badge variant="error" size="md" className="font-black">Inventory Exhausted</Badge>
          </div>
        )}

        <div className="absolute bottom-6 right-6 p-3 bg-white/90 backdrop-blur-sm rounded-full opacity-0 group-hover:opacity-100 transition-all duration-300 shadow-xl border border-white/40">
           <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-primary"><path d="M5 12h14m-7-7 7 7-7 7"/></svg>
        </div>
      </div>
      
      {/* Content Area */}
      <div className="flex flex-col flex-1 p-8">
        <div className="flex justify-between items-center mb-6">
          <span className="text-[10px] font-black text-slate-300 uppercase tracking-widest">
             Ref: {product.id.split('-')[1]?.toUpperCase() ?? '0912'}
          </span>
          <div className="flex items-center gap-1.5 px-3 py-1 bg-warning/5 border border-warning/10 rounded-full">
            <span className="text-[10px] font-black text-warning uppercase tracking-widest leading-none pt-0.5">Rating</span>
            <span className="text-[13px] font-black text-primary leading-none">{product.rating ?? '5.0'}</span>
          </div>
        </div>
        
        <h3 className="text-[19px] font-black leading-tight text-primary mb-3 group-hover:text-accent transition-colors text-balance">
          {product.name}
        </h3>
        
        <p className="text-[14px] text-text-muted font-medium mb-10 line-clamp-2 leading-relaxed">
          {product.description}
        </p>
        
        {/* Footer with Price and Action */}
        <div className="mt-auto pt-8 border-t border-slate-50 flex items-center justify-between">
          <div className="flex flex-col">
            <span className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mb-1">Price</span>
            <span className="text-2xl font-black text-primary tracking-tighter">
              {formattedPrice}
            </span>
          </div>
          
          <Button
            size="lg"
            variant="primary"
            disabled={isOutOfStock}
            className="rounded-2xl h-14 px-6 shadow-md hover:shadow-xl transition-all"
            onClick={(e) => {
              e.stopPropagation()
              onAddToCart?.(product.id)
            }}
          >
            Add to Cart
          </Button>
        </div>
      </div>
    </Card>
  )
}


