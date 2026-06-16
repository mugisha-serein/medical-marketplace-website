/**
 * MVP API v1 contract — path segments relative to VITE_API_BASE_URL (/api/v1).
 * No leading slashes (axios merges safely with baseURL).
 */
export const API_V1_PATHS = {
  auth: {
    token: 'auth/token',
    tokenRefresh: 'auth/token/refresh',
    register: 'auth/register',
    logout: 'auth/logout',
  },
  catalog: {
    products: 'catalog/products',
    categories: 'catalog/categories',
    productDetail: (slug: string) => `catalog/products/${encodeURIComponent(slug)}`,
  },
  cart: {
    root: 'cart',
    items: 'cart/items',
    item: (productId: string) => `cart/items/${productId}`,
  },
  orders: {
    root: 'orders',
    detail: (orderId: string) => `orders/${orderId}`,
  },
} as const

/** Join path segments into a trailing-slash URL safe for axios baseURL. */
export function apiPath(...segments: string[]): string {
  const path = segments
    .map((segment) => segment.replace(/^\/+|\/+$/g, ''))
    .filter(Boolean)
    .join('/')
  if (!path) {
    throw new Error('API path must include at least one segment')
  }
  return `${path}/`
}
