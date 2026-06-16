// src/core/store/index.ts
import { useAuthStore } from './authSlice';
import { useProductStore } from './productSlice';
import { useCartStore } from './cartSlice';
import { useOrderStore } from './orderSlice';
import { useNotificationStore } from './notificationSlice';

export const store = {
  auth: useAuthStore,
  product: useProductStore,
  cart: useCartStore,
  order: useOrderStore,
  notification: useNotificationStore,
};

// Export selectors for convenience (optional)
export * from './authSlice';
export * from './productSlice';
export * from './cartSlice';
export * from './orderSlice';
export * from './notificationSlice';
