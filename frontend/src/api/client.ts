import type { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import type { ApiError, ApiResponse } from '../domain/contracts/api'
import { tokenService } from '../infrastructure/auth/tokenService'
import axios from 'axios'
import { z } from 'zod'

const DEFAULT_API_V1_BASE = 'http://localhost:8000/api/v1'

/** Normalize env base URL to exactly one /api/v1 suffix (no double slashes). */
export function normalizeApiBaseUrl(raw: string): string {
  let base = raw.trim().replace(/\/+$/, '')
  if (!base.endsWith('/api/v1')) {
    const suffix = base.endsWith('/api') ? '/v1' : '/api/v1'
    base = `${base}${suffix}`
  }
  // Ensure exactly one trailing slash to prevent URL joining errors
  return `${base.replace(/\/+$/, '')}/`
}

export const API_BASE_URL = normalizeApiBaseUrl(
  import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_V1_BASE
)

const TIMEOUT = Number(import.meta.env.VITE_API_TIMEOUT ?? 15000)

const createClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: API_BASE_URL,
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: Number.isFinite(TIMEOUT) ? TIMEOUT : 15000,
  })

  client.interceptors.request.use((config) => {
    const token = tokenService.getToken()
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    if (config.url) {
      // Fix malformed URL bug: strip redundant prefixes if they were passed manually
      let cleanUrl = config.url.replace(/^\/?(api\/v1\/|api\/)/, '')
      config.url = cleanUrl.replace(/^\/+/, '')
    }
    return config
  })

  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean }
      const data = error.response?.data as Record<string, unknown> | undefined

      // Global 401 Refresh Handler
      if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
        originalRequest._retry = true
        try {
          const refreshToken = tokenService.getRefreshToken?.() // Ensure tokenService provides this
          if (refreshToken) {
            // Use axios directly to avoid interceptor recursion
            const refreshRes = await axios.post(`${API_BASE_URL}auth/token/refresh/`, {
              refresh: refreshToken,
            })
            const { access } = refreshRes.data
            tokenService.saveToken?.(access)

            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${access}`
            }
            return client(originalRequest)
          }
        } catch (refreshError) {
          console.error('[Auth] Token refresh failed')
        }
        tokenService.clearToken()
        window.dispatchEvent(new CustomEvent('auth:unauthorized'))
      }

      const detail = data?.detail ?? data?.error ?? data?.message
      const normalized: ApiError = {
        code: String(data?.code ?? error.code ?? 'INTERNAL_SERVER_ERROR'),
        message: typeof detail === 'string' ? detail : error.message || 'An unexpected error occurred',
        details: data?.details as Record<string, unknown> | undefined,
      }
      return Promise.reject(normalized)
    }
  )

  return client
}

const apiClient = createClient()

export async function apiRequest<T>(config: AxiosRequestConfig): Promise<ApiResponse<T>> {
  const response: AxiosResponse<T> = await apiClient.request<T>(config)
  return { data: response.data }
}

export async function validatedRequest<T>(
  config: AxiosRequestConfig,
  schema?: z.ZodType<T>
): Promise<ApiResponse<T>> {
  const result = await apiRequest<T>(config)

  if (schema) {
    const validationResult = schema.safeParse(result.data)
    if (!validationResult.success) {
      console.error('[API Validation Error]:', validationResult.error)
      throw {
        code: 'VALIDATION_ERROR',
        message: 'The server returned an invalid data structure.',
        details: validationResult.error.format(),
      } as ApiError
    }
    return { data: validationResult.data }
  }

  return result
}

export default apiClient
