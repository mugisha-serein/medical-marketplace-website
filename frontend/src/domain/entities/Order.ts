import { OrderStatus } from '../enums/OrderStatus'
import type { CartItem } from './CartItem'

export interface Order {
  readonly id: string;
  readonly buyerId: string;
  readonly vendorId: string;
  readonly items: readonly CartItem[];
  readonly subtotal: number;
  readonly shippingFee: number;
  readonly tax: number;
  readonly total: number;
  readonly status: OrderStatus;
  readonly placedAt: string;
  readonly updatedAt: string;
  readonly deliveryEstimate?: string;
}
