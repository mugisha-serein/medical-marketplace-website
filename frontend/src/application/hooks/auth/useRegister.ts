import { useCallback } from 'react'
import { useAuthStore } from '../../../core/store/authSlice'

export function useRegister() {
  const register = useAuthStore((state) => state.register)

  return useCallback(
    async (email: string, password: string, name: string) => {
      await register(email, password, name)
    },
    [register]
  )
}
