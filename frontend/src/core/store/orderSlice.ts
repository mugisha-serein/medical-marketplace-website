import { create } from 'zustand'
import type { Order } from '../../domain/entities/Order'

export interface OrderState {
  orders: readonly Order[]
  currentOrder?: Order
  loading: boolean
  error?: string
}

export interface OrderActions {
  setOrders: (orders: readonly Order[]) => void
  setCurrentOrder: (order?: Order) => void
  addOrder: (order: Order) => void
  setLoading: (loading: boolean) => void
  setError: (error?: string) => void
}

export const useOrderStore = create<OrderState & OrderActions>()((set, get) => ({
  orders: [],
  currentOrder: undefined,
  loading: false,
  error: undefined,
  setOrders: (orders) => set({ orders }),
  setCurrentOrder: (order) => set({ currentOrder: order }),
  addOrder: (order) => set({ orders: [...get().orders, order] }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}))
