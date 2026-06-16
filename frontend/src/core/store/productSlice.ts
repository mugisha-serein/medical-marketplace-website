import { create } from 'zustand'
import type { Equipment } from '../../domain/entities/Equipment'
import type { Category } from '../../domain/entities/Category'
import type { Vendor } from '../../domain/entities/Vendor'

export interface ProductFilterState {
  categoryId?: string
  minPrice?: number
  maxPrice?: number
  inStockOnly: boolean
  query: string
}

export interface ProductState {
  catalog: readonly Equipment[]
  categories: readonly Category[]
  vendors: readonly Vendor[]
  filters: ProductFilterState
  pagination: {
    page: number
    pageSize: number
    total: number
  }
  loading: boolean
  error?: string
}

export interface ProductActions {
  setCatalog: (items: readonly Equipment[]) => void
  setCategories: (categories: readonly Category[]) => void
  setVendors: (vendors: readonly Vendor[]) => void
  setFilters: (filters: Partial<ProductFilterState>) => void
  setPagination: (page: number, pageSize: number, total: number) => void
  setLoading: (loading: boolean) => void
  setError: (error?: string) => void
  resetFilters: () => void
}

export const useProductStore = create<ProductState & ProductActions>()((set) => ({
  catalog: [],
  categories: [],
  vendors: [],
  filters: {
    categoryId: undefined,
    minPrice: undefined,
    maxPrice: undefined,
    inStockOnly: false,
    query: '',
  },
  pagination: {
    page: 1,
    pageSize: 20,
    total: 0,
  },
  loading: false,
  error: undefined,
  setCatalog: (items) => set({ catalog: items }),
  setCategories: (categories) => set({ categories }),
  setVendors: (vendors) => set({ vendors }),
  setFilters: (filters) => set((state) => ({ filters: { ...state.filters, ...filters } })),
  setPagination: (page, pageSize, total) => set({ pagination: { page, pageSize, total } }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  resetFilters: () =>
    set({
      filters: {
        categoryId: undefined,
        minPrice: undefined,
        maxPrice: undefined,
        inStockOnly: false,
        query: '',
      },
    }),
}))
