import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { login as loginApi, register as registerApi } from '../../api/auth'
import type { ApiError } from '../../domain/contracts/api'
import { tokenService } from '../../infrastructure/auth/tokenService'
import type { User } from '../../domain/entities/User'

export interface AuthState {
  user: User | null
  token: string | null
  loading: boolean
  error?: string
}

export interface AuthActions {
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name: string) => Promise<void>
  logout: () => void
  setUser: (user: User | null) => void
  setToken: (token: string | null) => void
  setLoading: (loading: boolean) => void
  setError: (error?: string) => void
}

export const useAuthStore = create<AuthState & AuthActions>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      loading: false,
      error: undefined,
      login: async (email, password) => {
        set({ loading: true, error: undefined })
        try {
          const response = await loginApi(email, password)
          tokenService.setToken(response.token)
          set({ token: response.token, user: response.user, loading: false })
        } catch (err: unknown) {
          const message = (err as ApiError)?.message ?? 'Login failed'
          set({ error: message, loading: false })
        }
      },
      register: async (email, password, name) => {
        set({ loading: true, error: undefined })
        try {
          const response = await registerApi(email, password, name)
          tokenService.setToken(response.token)
          set({ token: response.token, user: response.user, loading: false })
        } catch (err: unknown) {
          const message = (err as ApiError)?.message ?? 'Registration failed'
          set({ error: message, loading: false })
        }
      },
      logout: () => {
        tokenService.clearToken()
        set({ user: null, token: null })
      },
      setUser: (user) => set({ user }),
      setToken: (token) => set({ token }),
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error }),
    }),
    { 
      name: 'auth-store', 
      storage: createJSONStorage(() => localStorage) 
    }
  )
)
