import { useCallback } from 'react'
import { useAuthStore } from '../../../core/store/authSlice'

export function useLogin() {
  const login = useAuthStore((state) => state.login)

  return useCallback(
    async (email: string, password: string) => {
      await login(email, password)
    },
    [login]
  )
}
