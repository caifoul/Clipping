import { createContext, useContext, type ReactNode } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { authApi } from '../api/auth'
import { ApiError } from '../api/client'
import type { User } from '../api/types'

type AuthContextValue = {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()

  const meQuery = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: async () => {
      try {
        return await authApi.me()
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) return null
        throw err
      }
    },
  })

  const loginMutation = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      authApi.login(email, password),
    onSuccess: (user) => queryClient.setQueryData(['auth', 'me'], user),
  })

  const signupMutation = useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      authApi.signup(email, password),
    onSuccess: (user) => queryClient.setQueryData(['auth', 'me'], user),
  })

  const logoutMutation = useMutation({
    mutationFn: () => authApi.logout(),
    onSuccess: () => queryClient.setQueryData(['auth', 'me'], null),
  })

  const value: AuthContextValue = {
    user: meQuery.data ?? null,
    isLoading: meQuery.isLoading,
    login: async (email, password) => {
      await loginMutation.mutateAsync({ email, password })
    },
    signup: async (email, password) => {
      await signupMutation.mutateAsync({ email, password })
    },
    logout: async () => {
      await logoutMutation.mutateAsync()
    },
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
