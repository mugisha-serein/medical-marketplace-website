export const NotificationType = {
  ORDER_UPDATE: 'ORDER_UPDATE',
  SYSTEM_ALERT: 'SYSTEM_ALERT',
  PROMOTION: 'PROMOTION',
} as const

export type NotificationType = (typeof NotificationType)[keyof typeof NotificationType]
