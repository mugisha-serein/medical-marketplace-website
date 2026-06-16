import { useMemo } from 'react'
import { useCart } from '../../../application/hooks/cart/useCart'

export default function CartPage() {
  const { items } = useCart()
  const total = useMemo(
    () => items.reduce((sum, item) => sum + item.unitPrice * item.quantity, 0),
    [items]
  )

  return (
    <section className="cart-page">
      <h1>Your Cart</h1>
      {items.length === 0 ? (
        <p>Your cart is empty.</p>
      ) : (
        <div>
          <ul>
            {items.map((item) => (
              <li key={item.equipmentId}>
                {item.name} × {item.quantity} — ${(item.unitPrice * item.quantity) / 100}
              </li>
            ))}
          </ul>
          <strong>Total: ${(total / 100).toFixed(2)}</strong>
        </div>
      )}
    </section>
  )
}
