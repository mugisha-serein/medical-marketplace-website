import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import './index.css'

type Product = {
  id: string
  name: string
  slug: string
  price: string
  condition: string
  short_description?: string
  manufacturer?: string
  model_number?: string
  category_name?: string
  vendor_name?: string
  in_stock?: boolean
  stock_quantity?: number
}

type ProductPage = {
  count: number
  page: number
  page_size: number
  results: Product[]
}

type InquiryForm = {
  buyer_name: string
  buyer_email: string
  buyer_phone: string
  organization: string
  quantity: number
  message: string
}

const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1').replace(/\/+$/, '')

const emptyInquiry: InquiryForm = {
  buyer_name: '',
  buyer_email: '',
  buyer_phone: '',
  organization: '',
  quantity: 1,
  message: '',
}

function formatPrice(value: string) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(Number(value || 0))
}

export default function App() {
  const [products, setProducts] = useState<Product[]>([])
  const [query, setQuery] = useState('')
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)
  const [inquiry, setInquiry] = useState<InquiryForm>(emptyInquiry)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  async function loadProducts(search = '') {
    setLoading(true)
    setError('')
    try {
      const params = new URLSearchParams({ page_size: '50' })
      if (search.trim()) params.set('q', search.trim())
      const response = await fetch(`${API_BASE}/catalog/products/?${params.toString()}`)
      if (!response.ok) throw new Error(`Backend returned ${response.status}`)
      const data = (await response.json()) as ProductPage
      setProducts(data.results)
      if (!selectedProduct && data.results.length) setSelectedProduct(data.results[0])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not connect to the backend API')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadProducts()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const stats = useMemo(() => {
    const vendors = new Set(products.map((product) => product.vendor_name).filter(Boolean))
    const categories = new Set(products.map((product) => product.category_name).filter(Boolean))
    const stock = products.reduce((sum, product) => sum + Number(product.stock_quantity ?? 0), 0)
    return { vendors: vendors.size, categories: categories.size, stock }
  }, [products])

  async function submitInquiry(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!selectedProduct) return
    setSubmitting(true)
    setNotice('')
    setError('')
    try {
      const response = await fetch(`${API_BASE}/inquiries/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...inquiry,
          product_slug: selectedProduct.slug,
          product_name: selectedProduct.name,
        }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data?.message || 'Could not send inquiry')
      setInquiry(emptyInquiry)
      setNotice(`Inquiry sent for ${selectedProduct.name}. Vendor can follow up immediately.`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not send inquiry')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="app-shell">
      <section className="hero">
        <nav className="topbar">
          <div className="brand-mark">MedEquip</div>
          <div className="api-pill">SQLite MVP · {API_BASE}</div>
        </nav>

        <div className="hero-grid">
          <div>
            <p className="eyebrow">Medical marketplace presentation MVP</p>
            <h1>Buy clinic-ready medical equipment without marketplace complexity.</h1>
            <p className="hero-copy">
              Browse equipment, check stock, select a product and send a supplier inquiry. The frontend is connected directly to the Django REST API using SQLite demo data.
            </p>
            <div className="hero-actions">
              <button onClick={() => loadProducts(query)} className="primary-button">Refresh inventory</button>
              <a href={`${API_BASE}/health/`} target="_blank" rel="noreferrer" className="ghost-button">Backend health</a>
            </div>
          </div>

          <div className="stats-card">
            <span>Live demo snapshot</span>
            <strong>{products.length}</strong>
            <p>listed products</p>
            <div className="stats-row">
              <div><b>{stats.categories}</b><small>Categories</small></div>
              <div><b>{stats.vendors}</b><small>Vendors</small></div>
              <div><b>{stats.stock}</b><small>Units</small></div>
            </div>
          </div>
        </div>
      </section>

      <section className="content-grid">
        <div className="catalog-panel">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Inventory</p>
              <h2>Available equipment</h2>
            </div>
            <form className="search-form" onSubmit={(event) => { event.preventDefault(); loadProducts(query) }}>
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search monitor, ultrasound..." />
              <button>Search</button>
            </form>
          </div>

          {error && <div className="alert error">{error}</div>}
          {notice && <div className="alert success">{notice}</div>}
          {loading ? (
            <div className="empty-state">Loading products from Django API...</div>
          ) : (
            <div className="product-grid">
              {products.map((product) => (
                <button
                  key={product.id}
                  className={`product-card ${selectedProduct?.id === product.id ? 'selected' : ''}`}
                  onClick={() => setSelectedProduct(product)}
                >
                  <div className="product-icon">⚕</div>
                  <div className="product-meta">
                    <span>{product.category_name}</span>
                    <strong>{product.name}</strong>
                    <p>{product.short_description}</p>
                    <div className="product-footer">
                      <b>{formatPrice(product.price)}</b>
                      <em>{product.stock_quantity ?? 0} in stock</em>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        <aside className="inquiry-panel">
          <p className="eyebrow">Request quote</p>
          <h2>{selectedProduct ? selectedProduct.name : 'Choose product'}</h2>
          {selectedProduct && (
            <div className="selected-summary">
              <span>{selectedProduct.vendor_name}</span>
              <strong>{formatPrice(selectedProduct.price)}</strong>
              <p>{selectedProduct.manufacturer} · {selectedProduct.model_number}</p>
            </div>
          )}

          <form onSubmit={submitInquiry} className="inquiry-form">
            <label>Buyer name<input required value={inquiry.buyer_name} onChange={(event) => setInquiry({ ...inquiry, buyer_name: event.target.value })} /></label>
            <label>Email<input required type="email" value={inquiry.buyer_email} onChange={(event) => setInquiry({ ...inquiry, buyer_email: event.target.value })} /></label>
            <label>Phone<input value={inquiry.buyer_phone} onChange={(event) => setInquiry({ ...inquiry, buyer_phone: event.target.value })} /></label>
            <label>Clinic / organization<input value={inquiry.organization} onChange={(event) => setInquiry({ ...inquiry, organization: event.target.value })} /></label>
            <label>Quantity<input required type="number" min="1" value={inquiry.quantity} onChange={(event) => setInquiry({ ...inquiry, quantity: Number(event.target.value) })} /></label>
            <label>Message<textarea value={inquiry.message} onChange={(event) => setInquiry({ ...inquiry, message: event.target.value })} placeholder="Delivery location, urgency, warranty question..." /></label>
            <button disabled={!selectedProduct || submitting} className="primary-button full-width">
              {submitting ? 'Sending...' : 'Send inquiry'}
            </button>
          </form>
        </aside>
      </section>
    </main>
  )
}
