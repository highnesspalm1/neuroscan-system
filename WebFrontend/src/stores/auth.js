import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('neuroscan_token') || null)
  const isLoading = ref(false)
  const error = ref(null)

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userRole = computed(() => user.value?.role || null)
  const isAdmin = computed(() => userRole.value === 'admin')

  // Actions
  const initializeAuth = async () => {
    if (token.value) {
      try {
        isLoading.value = true
        const userData = await authApi.getCurrentUser()
        user.value = userData
      } catch (err) {
        console.error('Auth initialization failed:', err)
        clearAuth()
      } finally {
        isLoading.value = false
      }
    }
  }
  const login = async (credentials) => {
    try {
      isLoading.value = true
      error.value = null
      
      console.log('Attempting login with credentials:', { username: credentials.username })
      
      const response = await authApi.login(credentials)
      
      console.log('Login response received:', response)
      
      if (!response.access_token) {
        throw new Error('No access token received')
      }
      
      token.value = response.access_token
      user.value = response.user
      
      localStorage.setItem('neuroscan_token', token.value)
      
      console.log('Login successful, token stored')
      
      return response
    } catch (err) {
      console.error('Login error:', err)
      error.value = err.response?.data?.detail || err.message || 'Login failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    try {
      if (token.value) {
        await authApi.logout()
      }
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      clearAuth()
    }
  }

  const clearAuth = () => {
    user.value = null
    token.value = null
    error.value = null
    localStorage.removeItem('neuroscan_token')
  }

  const refreshToken = async () => {
    try {
      const response = await authApi.refreshToken()
      token.value = response.access_token
      localStorage.setItem('neuroscan_token', token.value)
      return response
    } catch (err) {
      clearAuth()
      throw err
    }
  }

  return {
    // State
    user,
    token,
    isLoading,
    error,
    
    // Getters
    isAuthenticated,
    userRole,
    isAdmin,
    
    // Actions
    initializeAuth,
    login,
    logout,
    clearAuth,
    refreshToken
  }
})
