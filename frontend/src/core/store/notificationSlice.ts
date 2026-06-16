import { create } from 'zustand'
import type { Notification } from '../../domain/entities/Notification'

export interface NotificationState {
  notifications: readonly Notification[]
  unreadCount: number
  loading: boolean
  error?: string
}

export interface NotificationActions {
  setNotifications: (notifications: readonly Notification[]) => void
  addNotification: (notification: Notification) => void
  markAsRead: (id: string) => void
  setLoading: (loading: boolean) => void
  setError: (error?: string) => void
}

export const useNotificationStore = create<NotificationState & NotificationActions>()((set) => ({
  notifications: [],
  unreadCount: 0,
  loading: false,
  error: undefined,
  setNotifications: (notifications) =>
    set({
      notifications,
      unreadCount: notifications.filter((notification) => !notification.read).length,
    }),
  addNotification: (notification) =>
    set((state) => ({
      notifications: [notification, ...state.notifications],
      unreadCount: state.unreadCount + (notification.read ? 0 : 1),
    })),
  markAsRead: (id) =>
    set((state) => {
      const notifications = state.notifications.map((notification) =>
        notification.id === id ? { ...notification, read: true } : notification
      )
      return {
        notifications,
        unreadCount: notifications.filter((notification) => !notification.read).length,
      }
    }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}))
