import { apiRequest } from './client'
import { API_V1_PATHS, apiPath } from './paths'
import type { Category } from '../domain/entities/Category'
import type { Equipment } from '../domain/entities/Equipment'
import type { Vendor } from '../domain/entities/Vendor'

export interface CatalogQuery {
  categoryId?: string
  minPrice?: number
  maxPrice?: number
  inStockOnly?: boolean
  search?: string
  page?: number
  pageSize?: number
}

interface BackendProductListItem {
  readonly id: string
  readonly name: string
  readonly slug: string
  readonly price: string
  readonly condition: 'new' | 'refurbished' | 'used'
  readonly short_description?: string
  readonly manufacturer?: string
  readonly model_number?: string
  readonly category_name?: string
  readonly vendor_name?: string
  readonly primary_image?: string | null
  readonly in_stock?: boolean
}

interface BackendProductDetail extends BackendProductListItem {
  readonly description?: string
  readonly specifications?: Record<string, string>
  readonly category?: { readonly id?: string; readonly name?: string; readonly slug?: string }
  readonly vendor?: { readonly id?: string; readonly company_name?: string }
  readonly images?: readonly { readonly image?: string; readonly alt_text?: string }[]
  readonly stock_quantity?: number
}

interface BackendProductPage {
  readonly count: number
  readonly page: number
  readonly page_size: number
  readonly results: readonly BackendProductListItem[]
}

interface BackendCategory {
  readonly id: string
  readonly name: string
  readonly slug?: string
  readonly parent?: string | null
  readonly children?: readonly BackendCategory[]
}

export interface CatalogResponse {
  readonly items: readonly Equipment[]
  readonly page: number
  readonly pageSize: number
  readonly total: number
}

interface ApiSuccessEnvelope<T> {
  readonly success: boolean
  readonly message: string
  readonly data: T
}

function priceToCents(price: string | number | undefined): number {
  const value = Number(price ?? 0)
  return Number.isFinite(value) ? Math.round(value * 100) : 0
}

function mapProduct(product: BackendProductListItem | BackendProductDetail): Equipment {
  const detail = product as BackendProductDetail
  const images = detail.images?.map((image) => image.image).filter(Boolean) as string[] | undefined
  const categoryId = detail.category?.slug ?? detail.category_name ?? ''
  const vendorId = detail.vendor?.id ?? detail.vendor_name ?? ''

  return {
    id: product.slug,
    productId: product.id,
    name: product.name,
    description: detail.description ?? product.short_description ?? product.name,
    priceCents: priceToCents(product.price),
    images: images?.length ? images : product.primary_image ? [product.primary_image] : [],
    categoryId,
    vendorId,
    stock: detail.stock_quantity ?? (product.in_stock ? 1 : 0),
    specifications: detail.specifications ?? {},
    condition: product.condition,
  }
}

function mapCategory(category: BackendCategory): Category {
  return {
    id: category.slug ?? category.id,
    name: category.name,
    parentId: category.parent ?? undefined,
  }
}

/** GET /api/v1/catalog/products/ */
export async function fetchCatalog(query: CatalogQuery): Promise<CatalogResponse> {
  const result = await apiRequest<BackendProductPage>({
    method: 'GET',
    url: apiPath(API_V1_PATHS.catalog.products),
    params: {
      category: query.categoryId,
      min_price: query.minPrice,
      max_price: query.maxPrice,
      q: query.search,
      page: query.page,
      page_size: query.pageSize,
    },
  })

  const items = result.data.results.map(mapProduct)
  return {
    items: query.inStockOnly ? items.filter((item) => item.stock > 0) : items,
    page: result.data.page,
    pageSize: result.data.page_size,
    total: result.data.count,
  }
}

/** GET /api/v1/catalog/categories/ */
export async function fetchCategories(): Promise<Category[]> {
  const result = await apiRequest<BackendCategory[]>({
    method: 'GET',
    url: apiPath(API_V1_PATHS.catalog.categories),
  })
  return result.data.map(mapCategory)
}

export async function fetchVendors(): Promise<Vendor[]> {
  return []
}

/** GET /api/v1/catalog/products/:slug/ */
export async function fetchProductBySlug(slug: string): Promise<Equipment> {
  const result = await apiRequest<ApiSuccessEnvelope<BackendProductDetail>>({
    method: 'GET',
    url: apiPath(API_V1_PATHS.catalog.productDetail(slug)),
  })
  return mapProduct(result.data.data)
}

/** @deprecated Use fetchProductBySlug */
export const fetchProductById = fetchProductBySlug
