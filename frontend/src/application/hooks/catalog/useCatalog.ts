import { useCallback } from 'react'
import { fetchCatalog, fetchCategories, fetchVendors } from '../../../infrastructure/api/productApi'
import { useProductStore, type ProductState, type ProductActions } from '../../../core/store/productSlice'
import { type Equipment } from '../../../domain/entities/Equipment'
import { type Category } from '../../../domain/entities/Category'
import { type Vendor } from '../../../domain/entities/Vendor'
import { type ProductFilterState } from '../../../core/store/productSlice'

export function useCatalog(): {
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
  fetchCatalog: () => Promise<void>
  loadMetadata: () => Promise<void>
} {
  const catalog = useProductStore((state: ProductState) => state.catalog)
  const categories = useProductStore((state: ProductState) => state.categories)
  const vendors = useProductStore((state: ProductState) => state.vendors)
  const filters = useProductStore((state: ProductState) => state.filters)
  const pagination = useProductStore((state: ProductState) => state.pagination)
  const loading = useProductStore((state: ProductState) => state.loading)
  const error = useProductStore((state: ProductState) => state.error)
  const setCatalog = useProductStore((state: ProductState & ProductActions) => state.setCatalog)
  const setCategories = useProductStore((state: ProductState & ProductActions) => state.setCategories)
  const setVendors = useProductStore((state: ProductState & ProductActions) => state.setVendors)
  const setPagination = useProductStore((state: ProductState & ProductActions) => state.setPagination)
  const setLoading = useProductStore((state: ProductState & ProductActions) => state.setLoading)
  const setError = useProductStore((state: ProductState & ProductActions) => state.setError)

  const fetchCatalogItems = useCallback(async () => {
    setLoading(true)
    setError(undefined)

    try {
      const items = await fetchCatalog({
        categoryId: filters.categoryId,
        minPrice: filters.minPrice,
        maxPrice: filters.maxPrice,
        inStockOnly: filters.inStockOnly,
        search: filters.query,
        page: pagination.page,
        pageSize: pagination.pageSize,
      })

      setCatalog(items.items)
      setPagination(items.page, items.pageSize, items.total)
    } catch (err: unknown) {
      // Production-grade error handling
      const apiError = err as { message: string; code?: string };
      setError(apiError.message || 'An unexpected error occurred while loading the catalog.')
    } finally {
      setLoading(false)
    }
  }, [filters, pagination.page, pagination.pageSize, setCatalog, setError, setLoading, setPagination])


  const loadMetadata = useCallback(async () => {
    setLoading(true)
    try {
      const [categoryResult, vendorResult] = await Promise.all([fetchCategories(), fetchVendors()])
      setCategories(categoryResult)
      setVendors(vendorResult)
    } catch {
      // metadata is optional; ignore failures here
    } finally {
      setLoading(false)
    }
  }, [setCategories, setVendors, setLoading])

  return {
    catalog,
    categories,
    vendors,
    filters,
    pagination,
    loading,
    error,
    fetchCatalog: fetchCatalogItems,
    loadMetadata,
  }
}
