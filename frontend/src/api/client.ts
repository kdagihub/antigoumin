import axios, { type AxiosError, type AxiosRequestConfig } from 'axios'

const TOKEN_KEY = 'ag_token'

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function getBaseUrl(): string {
  return import.meta.env.VITE_API_BASE_URL.replace(/\/$/, '')
}

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setStoredToken(token: string | null): void {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token)
  } else {
    localStorage.removeItem(TOKEN_KEY)
  }
}

export const api = axios.create({
  baseURL: `${getBaseUrl()}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = getStoredToken()
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string; message?: string }>) => {
    if (error.response?.status === 401) {
      setStoredToken(null)
    }

    const status = error.response?.status ?? 500
    const data = error.response?.data
    const message = data?.detail ?? data?.message ?? `Erreur serveur (${status})`
    return Promise.reject(new ApiError(status, message))
  },
)

export async function apiRequest<T>(path: string, config?: AxiosRequestConfig): Promise<T> {
  const response = await api.request<T>({ url: path, ...config })
  return response.data
}
