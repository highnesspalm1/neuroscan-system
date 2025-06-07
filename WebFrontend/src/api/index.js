import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 120000, // Increased to 2 minutes for Render cold starts
  headers: {
    'Content-Type': 'application/json',
  }
})

console.log('API Configuration:')
console.log('- Base URL:', api.defaults.baseURL)
console.log('- Timeout:', api.defaults.timeout, 'ms')
console.log('- Environment VITE_API_URL:', import.meta.env.VITE_API_URL)
console.log('- Environment VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL)

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    
    // Check for admin token first
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    } else {
      // Check for customer token if no admin token
      const customerToken = localStorage.getItem('customer_token')
      if (customerToken) {
        config.headers.Authorization = `Bearer ${customerToken}`
      }
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const authStore = useAuthStore()
    
    if (error.response?.status === 401) {
      // Token expired or invalid
      if (authStore.token) {
        try {
          // Try to refresh token
          await authStore.refreshToken()
          // Retry the original request
          return api.request(error.config)
        } catch (refreshError) {
          // Refresh failed, logout user
          authStore.clearAuth()
          window.location.href = '/admin/login'
        }
      }
    }
    
    return Promise.reject(error)
  }
)

export default api
