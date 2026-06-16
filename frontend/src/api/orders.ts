import { apiRequest } from './client'
import { API_V1_PATHS, apiPath } from './paths'
import { OrderStatus } from '../domain/enums/OrderStatus'
import type { Order } from '../domain/entities/Order'

interface BackendOrderListItem {
  readonly id: string
  readonly order_number?: string
  readonly status: string
  readonly total_amount: string
  readonly item_count?: number
  readonly created_at: string
}

interface BackendOrderDetail extends BackendOrderListItem {
  readonly shipping_cost?: string
  readonly tax_amount?: string
  readonly subtotal?: string
  readonly updated_at?: string
  readonly estimated_delivery?: string
  readonly items?: readonly unknown[]
}

interface BackendOrderPage {
  readonly count: number
  readonly page: number
  readonly page_size: number
  readonly results: readonly BackendOrderListItem[]
}

export interface PlaceOrderPayload {
  readonly shipping_address: string
  readonly billing_address: string
  readonly contact_phone?: string
  readonly notes?: string
}

function mapStatus(status: string): OrderStatus {
  const normalized = status.toLowerCase()
  if (normalized === 'shipped') return OrderStatus.SHIPPED
  if (normalized === 'delivered') return OrderStatus.DELIVERED
  if (normalized === 'cancelled' || normalized === 'refunded') return OrderStatus.CANCELLED
  return OrderStatus.PENDING
}

function money(value: string | undefined): number {
  const parsed = Number(value ?? 0)
  return Number.isFinite(parsed) ? Math.round(parsed * 100) : 0
}

function mapOrder(order: BackendOrderListItem | BackendOrderDetail): Order {
  const detail = order as BackendOrderDetail
  return {
    id: order.id,
    buyerId: '',
    vendorId: '',
    items: [],
    subtotal: money(detail.subtotal ?? order.total_amount),
    shippingFee: money(detail.shipping_cost),
    tax: money(detail.tax_amount),
    total: money(order.total_amount),
    status: mapStatus(order.status),
    placedAt: order.created_at,
    updatedAt: detail.updated_at ?? order.created_at,
    deliveryEstimate: detail.estimated_delivery,
  }
}

/** GET /api/v1/orders/ */
export async function fetchOrders(page = 1, pageSize = 20): Promise<Order[]> {
  const result = await apiRequest<BackendOrderPage>({
    method: 'GET',
    url: apiPath(API_V1_PATHS.orders.root),
    params: { page, page_size: pageSize },
  })
  return result.data.results.map(mapOrder)
}

/** POST /api/v1/orders/ */
export async function createOrder(payload: PlaceOrderPayload): Promise<Order> {
  const result = await apiRequest<BackendOrderDetail>({
    method: 'POST',
    url: apiPath(API_V1_PATHS.orders.root),
    data: payload,
  })
  return mapOrder(result.data)
}

/** GET /api/v1/orders/:orderId/ */
export async function fetchOrderById(orderId: string): Promise<Order> {
  const result = await apiRequest<BackendOrderDetail>({
    method: 'GET',
    url: apiPath(API_V1_PATHS.orders.detail(orderId)),
  })
  return mapOrder(result.data)
}
