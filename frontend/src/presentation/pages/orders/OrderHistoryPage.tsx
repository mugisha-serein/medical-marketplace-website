import { useEffect } from 'react'
import { useOrderHistory } from '../../../application/hooks/order/useOrderHistory'

export default function OrderHistoryPage() {
  const { orders, loading, loadOrders } = useOrderHistory()

  useEffect(() => {
    loadOrders()
  }, [loadOrders])

  return (
    <section className="order-history-page">
      <h1>Order History</h1>
      {loading ? (
        <div>Loading orders…</div>
      ) : orders.length === 0 ? (
        <p>No orders have been placed yet.</p>
      ) : (
        <ul>
          {orders.map((order) => (
            <li key={order.id}>
              <strong>{order.id}</strong> — {order.status}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
