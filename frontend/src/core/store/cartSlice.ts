import { create } from 'zustand'
import type { CartItem } from '../../domain/entities/CartItem'

export interface CartState {
  items: readonly CartItem[]
  loading: boolean
  error?: string
}

export interface CartActions {
  setItems: (items: readonly CartItem[]) => void
  addItem: (item: CartItem) => void
  removeItem: (equipmentId: string) => void
  updateQuantity: (equipmentId: string, quantity: number) => void
  clearCart: () => void
  setLoading: (loading: boolean) => void
  setError: (error?: string) => void
}

export const useCartStore = create<CartState & CartActions>()((set, get) => ({
  items: [],
  loading: false,
  error: undefined,
  setItems: (items) => set({ items }),
  addItem: (item) => {
    const existing = get().items.find((it) => it.equipmentId === item.equipmentId)
    if (existing) {
      set({
        items: get().items.map((it) =>
          it.equipmentId === item.equipmentId
            ? { ...it, quantity: it.quantity + item.quantity }
            : it
        ),
      })
    } else {
      set({ items: [...get().items, item] })
    }
  },
  removeItem: (equipmentId) =>
    set({ items: get().items.filter((item) => item.equipmentId !== equipmentId) }),
  updateQuantity: (equipmentId, quantity) =>
    set({
      items: get().items.map((item) =>
        item.equipmentId === equipmentId
          ? { ...item, quantity: Math.max(1, quantity) }
          : item
      ),
    }),
  clearCart: () => set({ items: [] }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}))
