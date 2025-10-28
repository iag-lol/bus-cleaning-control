import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User, LoginCredentials, TokenResponse } from '../types'
import api from '../services/api'

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => void
  setUser: (user: User) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      login: async (credentials: LoginCredentials) => {
        const response = await api.post<TokenResponse>('/auth/login', credentials)
        const { access_token, refresh_token } = response.data

        // Set tokens in API client
        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

        // Get user info (you would typically have a /me endpoint)
        // For now, we'll decode the token or fetch user info
        // This is a simplified version
        const user: User = {
          id: 1,
          nombre: 'Admin',
          email: credentials.email,
          rol: 'ADMIN' as any,
          activo: true,
          created_at: new Date().toISOString(),
        }

        set({
          user,
          accessToken: access_token,
          refreshToken: refresh_token,
          isAuthenticated: true,
        })
      },

      logout: () => {
        delete api.defaults.headers.common['Authorization']
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        })
      },

      setUser: (user: User) => {
        set({ user })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
