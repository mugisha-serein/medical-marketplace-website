import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Suspense, lazy } from 'react'
import MainLayout from '../../presentation/layout/MainLayout'
import { LoadingSpinner } from '../../presentation/components/atoms/LoadingSpinner'

const HomePage = lazy(() => import('../../presentation/pages/home/HomePage'))
const AuthPage = lazy(() => import('../../presentation/pages/auth/AuthPage'))
const CatalogPage = lazy(() => import('../../presentation/pages/catalog/CatalogPage'))
const ProductDetailPage = lazy(() => import('../../presentation/pages/catalog/ProductDetailPage'))
const CartPage = lazy(() => import('../../presentation/pages/cart/CartPage'))
const OrderHistoryPage = lazy(() => import('../../presentation/pages/orders/OrderHistoryPage'))

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          {/* Public Authentication Routes */}
          <Route path="/login" element={<AuthPage />} />
          <Route path="/register" element={<AuthPage />} />

          {/* Main Marketplace Routes wrapped in Global Layout */}
          <Route element={<MainLayout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/catalog" element={<CatalogPage />} />
            <Route path="/catalog/:slug" element={<ProductDetailPage />} />
            <Route path="/cart" element={<CartPage />} />
            <Route path="/orders" element={<OrderHistoryPage />} />
          </Route>

          {/* Fallback Redirects */}
          <Route path="*" element={<Navigate replace to="/" />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  )
}
