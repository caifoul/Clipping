import { api } from './client'
import type { User } from './types'

export const authApi = {
  signup: (email: string, password: string) =>
    api.post<User>('/api/auth/signup', { email, password }),
  login: (email: string, password: string) =>
    api.post<User>('/api/auth/login', { email, password }),
  logout: () => api.post<void>('/api/auth/logout'),
  me: () => api.get<User>('/api/auth/me'),
}
