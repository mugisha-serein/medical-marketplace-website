export const Role = {
  ADMIN: 'ADMIN',
  VENDOR: 'VENDOR',
  BUYER: 'BUYER',
} as const

export type Role = (typeof Role)[keyof typeof Role]
