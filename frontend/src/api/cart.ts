import { apiRequest } from './client'
import { API_V1_PATHS, apiPath } from './paths'
import type { CartItem } from '../domain/entities/CartItem'

interface BackendCartLine {
  readonly qty: number
  readonly price_snapshot: string
  readonly name: string
  readonly sku: string
  readonly product_id: string
  readonly subtotal?: string
}

interface BackendCart {
  readonly items: Record<string, BackendCartLine>
  readonly total: string
  readonly item_count: number
}

function mapCartItems(cart: BackendCart): CartItem[] {
  return Object.entries(cart.items).map(([productId, line]) => ({
    equipmentId: line.product_id ?? productId,
    name: line.name,
    vendorId: '',
    quantity: line.qty,
    unitPrice: Math.round(Number(line.price_snapshot) * 100),
  }))
}

/** GET /api/v1/cart/ */
export async function fetchCart(): Promise<CartItem[]> {
  const result = await apiRequest<BackendCart>({
    method: 'GET',
    url: apiPath(API_V1_PATHS.cart.root),
  })
  return mapCartItems(result.data)
}

/** DELETE /api/v1/cart/ */
export async function clearCart(): Promise<void> {
  await apiRequest<{ message: string }>({
    method: 'DELETE',
    url: apiPath(API_V1_PATHS.cart.root),
  })
}

/** POST /api/v1/cart/items/ */
export async function addCartItem(productId: string, quantity: number): Promise<CartItem[]> {
  const result = await apiRequest<BackendCart>({
    method: 'POST',
    url: apiPath(API_V1_PATHS.cart.items),
    data: { product_id: productId, quantity },
  })
  return mapCartItems(result.data)
}

/** PATCH /api/v1/cart/items/:productId/ */
export async function updateCartItem(productId: string, quantity: number): Promise<CartItem[]> {
  const result = await apiRequest<BackendCart>({
    method: 'PATCH',
    url: apiPath(API_V1_PATHS.cart.item(productId)),
    data: { quantity },
  })
  return mapCartItems(result.data)
}

/** DELETE /api/v1/cart/items/:productId/ */
export async function removeCartItem(productId: string): Promise<CartItem[]> {
  const result = await apiRequest<BackendCart>({
    method: 'DELETE',
    url: apiPath(API_V1_PATHS.cart.item(productId)),
  })
  return mapCartItems(result.data)
}
