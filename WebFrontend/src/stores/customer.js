import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import customerApi from '@/api/customer'
import api from '@/api/index'

export const useCustomerStore = defineStore('customer', () => {
  // State
  const customer = ref(null)
  const token = ref(localStorage.getItem('customer_token'))
  const isLoading = ref(false)
  const error = ref(null)
  const dashboardStats = ref(null)
  const products = ref([])
  const certificates = ref([])
  const scanLogs = ref([])

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!customer.value)
  const customerName = computed(() => customer.value?.name || '')

  // Actions
  const login = async (credentials) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await customerApi.login(credentials)
        token.value = response.access_token
      customer.value = response.customer
      
      // Store token in localStorage
      localStorage.setItem('customer_token', response.access_token)
      
      return response
    } catch (err) {
      // Better error handling for common issues
      if (err.code === 'ECONNABORTED' || err.message.includes('timeout')) {
        error.value = 'Connection timeout - the service might be starting up. Please try again in a moment.'
      } else if (err.code === 'ERR_NETWORK' || err.message.includes('Network Error')) {
        error.value = 'Network error - please check your connection and try again.'
      } else {
        error.value = err.response?.data?.detail || err.message || 'Login failed'
      }
      throw err    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    customer.value = null
    token.value = null
    dashboardStats.value = null
    products.value = []
    certificates.value = []
    scanLogs.value = []
    
    localStorage.removeItem('customer_token')
  }

  const fetchMe = async () => {
    try {
      isLoading.value = true
      const customerData = await customerApi.getMe()
      customer.value = customerData
      return customerData
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch customer info'
      // If unauthorized, logout
      if (err.response?.status === 401) {
        logout()
      }
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const fetchDashboard = async () => {
    try {
      isLoading.value = true
      const stats = await customerApi.getDashboard()
      dashboardStats.value = stats
      return stats
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch dashboard'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const fetchProducts = async (skip = 0, limit = 100) => {
    try {
      isLoading.value = true
      const productData = await customerApi.getProducts(skip, limit)
      if (skip === 0) {
        products.value = productData
      } else {
        products.value.push(...productData)
      }
      return productData
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch products'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const fetchCertificates = async (skip = 0, limit = 100) => {
    try {
      isLoading.value = true
      const certData = await customerApi.getCertificates(skip, limit)
      if (skip === 0) {
        certificates.value = certData
      } else {
        certificates.value.push(...certData)
      }
      return certData
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch certificates'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const fetchScanLogs = async (skip = 0, limit = 100) => {
    try {
      isLoading.value = true
      const scanData = await customerApi.getScanLogs(skip, limit)
      if (skip === 0) {
        scanLogs.value = scanData
      } else {
        scanLogs.value.push(...scanData)
      }
      return scanData
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch scan logs'
      throw err
    } finally {
      isLoading.value = false
    }
  }  // Initialize store if token exists
  const initializeAuth = async () => {
    if (token.value) {
      try {
        await fetchMe()
      } catch (err) {
        logout()
      }
    }
  }

  return {
    // State
    customer,
    token,
    isLoading,
    error,
    dashboardStats,
    products,
    certificates,
    scanLogs,
    
    // Getters
    isAuthenticated,
    customerName,
    
    // Actions
    login,
    logout,
    fetchMe,
    fetchDashboard,
    fetchProducts,
    fetchCertificates,
    fetchScanLogs,
    initializeAuth
  }
})
