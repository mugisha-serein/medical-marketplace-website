import { useMemo } from 'react'
import { useAuthStore } from '../../../core/store/authSlice'
import { Role } from '../../../domain/enums/Role'

export function useAuth() {
  const user = useAuthStore((state) => state.user)
  const token = useAuthStore((state) => state.token)
  const loading = useAuthStore((state) => state.loading)
  const error = useAuthStore((state) => state.error)

  const isAuthenticated = useMemo(() => Boolean(user && token), [user, token])
  const role = user?.role ?? Role.BUYER

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    role,
  }
}
