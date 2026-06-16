import { useCallback } from 'react'
import { useOrderStore } from '../../../core/store/orderSlice'
import { fetchOrders } from '../../../infrastructure/api/orderApi'

export function useOrderHistory() {
  const orders = useOrderStore((state) => state.orders)
  const setOrders = useOrderStore((state) => state.setOrders)
  const loading = useOrderStore((state) => state.loading)
  const setLoading = useOrderStore((state) => state.setLoading)
  const setError = useOrderStore((state) => state.setError)

  const loadOrders = useCallback(async () => {
    setLoading(true)
    setError(undefined)
    try {
      const response = await fetchOrders()
      setOrders(response)
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : 'Unable to load orders'
      setError(message)
    } finally {
      setLoading(false)
    }
  }, [setError, setLoading, setOrders])

  return { orders, loading, loadOrders }
}
