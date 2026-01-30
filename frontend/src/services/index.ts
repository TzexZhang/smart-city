import api from './api'

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  full_name?: string
}

export const authApi = {
  login: (data: LoginRequest) => api.post('/auth/login', data),
  register: (data: RegisterRequest) => api.post('/auth/register', data),
  logout: () => api.post('/auth/logout'),
  getCurrentUser: () => api.get('/auth/me'),
}

export const userApi = {
  getConfig: () => api.get('/users/me/config'),
  updateConfig: (data: any) => api.put('/users/me/config', data),
}

export const aiApi = {
  getProviders: () => api.get('/ai/providers'),
  addProvider: (data: any) => api.post('/ai/providers', data),
  deleteProvider: (id: string) => api.delete(`/ai/providers/${id}`),
  setDefaultProvider: (id: string) => api.put(`/ai/providers/${id}/default`),
  getModels: (providerCode?: string) => api.get('/ai/models', {
    params: { provider_code: providerCode },
  }),
  getUsageStats: () => api.get('/ai/usage/stats'),
}

export const chatApi = {
  sendMessage: (data: { session_id?: string; message: string }) =>
    api.post('/chat/completions', data),
  getHistory: (sessionId: string) => api.get(`/chat/history/${sessionId}`),
  clearHistory: (sessionId: string) => api.delete(`/chat/history/${sessionId}`),
}
