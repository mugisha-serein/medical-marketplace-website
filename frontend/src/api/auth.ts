import { apiRequest } from './client'
import { API_V1_PATHS, apiPath } from './paths'
import { Role } from '../domain/enums/Role'
import type { User } from '../domain/entities/User'

interface BackendTokenResponse {
  readonly access: string
  readonly refresh: string
  readonly role: 'admin' | 'vendor' | 'customer'
  readonly email: string
  readonly full_name: string
}

interface BackendRefreshResponse {
  readonly access: string
}

interface BackendRegisterResponse {
  readonly message: string
  readonly user_id: string
}

export interface AuthResponse {
  readonly token: string
  readonly refreshToken?: string
  readonly user: User
}

function decodeJwtPayload(token: string): Record<string, unknown> {
  try {
    const payload = token.split('.')[1]
    const normalized = payload.replace(/-/g, '+').replace(/_/g, '/')
    return JSON.parse(window.atob(normalized)) as Record<string, unknown>
  } catch {
    return {}
  }
}

function mapRole(role: BackendTokenResponse['role'] | string | undefined): Role {
  if (role === 'admin') return Role.ADMIN
  if (role === 'vendor') return Role.VENDOR
  return Role.BUYER
}

function userFromToken(access: string, refresh?: string, fallback?: Partial<User>): AuthResponse {
  const payload = decodeJwtPayload(access)
  const email = String(fallback?.email ?? payload.email ?? '')
  return {
    token: access,
    refreshToken: refresh,
    user: {
      id: String(fallback?.id ?? payload.user_id ?? email),
      email,
      role: fallback?.role ?? mapRole(String(payload.role ?? 'customer')),
      name: String(fallback?.name ?? payload.full_name ?? email),
    },
  }
}

function splitName(name: string): { first_name: string; last_name: string } {
  const parts = name.trim().split(/\s+/).filter(Boolean)
  const first_name = parts.shift() ?? name.trim()
  return { first_name, last_name: parts.join(' ') || first_name }
}

/** POST /api/v1/auth/token/ — obtain access + refresh tokens */
export async function login(email: string, password: string): Promise<AuthResponse> {
  const result = await apiRequest<BackendTokenResponse>({
    method: 'POST',
    url: apiPath(API_V1_PATHS.auth.token),
    data: { email, password },
  })
  return userFromToken(result.data.access, result.data.refresh, {
    email: result.data.email,
    name: result.data.full_name,
    role: mapRole(result.data.role),
  })
}

/** POST /api/v1/auth/register/ then POST /api/v1/auth/token/ */
export async function register(email: string, password: string, name: string): Promise<AuthResponse> {
  const nameParts = splitName(name)
  await apiRequest<BackendRegisterResponse>({
    method: 'POST',
    url: apiPath(API_V1_PATHS.auth.register),
    data: {
      email,
      password,
      ...nameParts,
      role: 'customer',
    },
  })
  return login(email, password)
}

/** POST /api/v1/auth/token/refresh/ — refresh access token only */
export async function refreshSession(refresh: string, currentUser?: User): Promise<AuthResponse> {
  const result = await apiRequest<BackendRefreshResponse>({
    method: 'POST',
    url: apiPath(API_V1_PATHS.auth.tokenRefresh),
    data: { refresh },
  })
  return userFromToken(result.data.access, refresh, currentUser)
}

/** POST /api/v1/auth/logout/ */
export async function logout(refresh: string): Promise<void> {
  await apiRequest<{ message: string }>({
    method: 'POST',
    url: apiPath(API_V1_PATHS.auth.logout),
    data: { refresh },
  })
}
