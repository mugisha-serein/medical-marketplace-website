const TOKEN_KEY = 'medical_marketplace_token'

export const tokenService = {
  getToken(): string | null {
    return window.localStorage.getItem(TOKEN_KEY)
  },
  setToken(token: string): void {
    window.localStorage.setItem(TOKEN_KEY, token)
  },
  clearToken(): void {
    window.localStorage.removeItem(TOKEN_KEY)
  },
}
