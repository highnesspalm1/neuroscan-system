import { defineStore } from 'pinia'
import { ref } from 'vue'
import { adminApi } from '@/api/admin'

export const useAdminStore = defineStore('admin', () => {
  // State
  const customers = ref([])
  const products = ref([])
  const certificates = ref([])
  const scanLogs = ref([])
  const analytics = ref({
    totalCustomers: 0,
    totalProducts: 0,
    totalCertificates: 0,
    totalScans: 0,
    recentActivity: []
  })
  const isLoading = ref(false)
  const error = ref(null)

  // Customer Actions
  const fetchCustomers = async () => {
    try {
      isLoading.value = true
      const data = await adminApi.getCustomers()
      customers.value = data
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch customers'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const createCustomer = async (customerData) => {
    try {
      isLoading.value = true
      const newCustomer = await adminApi.createCustomer(customerData)
      customers.value.unshift(newCustomer)
      return newCustomer
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create customer'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updateCustomer = async (customerId, customerData) => {
    try {
      isLoading.value = true
      const updatedCustomer = await adminApi.updateCustomer(customerId, customerData)
      const index = customers.value.findIndex(c => c.id === customerId)
      if (index !== -1) {
        customers.value[index] = updatedCustomer
      }
      return updatedCustomer
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update customer'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const deleteCustomer = async (customerId) => {
    try {
      isLoading.value = true
      await adminApi.deleteCustomer(customerId)
      customers.value = customers.value.filter(c => c.id !== customerId)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete customer'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Product Actions
  const fetchProducts = async () => {
    try {
      isLoading.value = true
      const data = await adminApi.getProducts()
      products.value = data
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch products'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const createProduct = async (productData) => {
    try {
      isLoading.value = true
      const newProduct = await adminApi.createProduct(productData)
      products.value.unshift(newProduct)
      return newProduct
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create product'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updateProduct = async (productId, productData) => {
    try {
      isLoading.value = true
      const updatedProduct = await adminApi.updateProduct(productId, productData)
      const index = products.value.findIndex(p => p.id === productId)
      if (index !== -1) {
        products.value[index] = updatedProduct
      }
      return updatedProduct
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update product'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const deleteProduct = async (productId) => {
    try {
      isLoading.value = true
      await adminApi.deleteProduct(productId)
      products.value = products.value.filter(p => p.id !== productId)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete product'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Certificate Actions
  const fetchCertificates = async () => {
    try {
      isLoading.value = true
      const data = await adminApi.getCertificates()
      certificates.value = data
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch certificates'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const createCertificate = async (certificateData) => {
    try {
      isLoading.value = true
      const newCertificate = await adminApi.createCertificate(certificateData)
      certificates.value.unshift(newCertificate)
      return newCertificate
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to create certificate'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updateCertificate = async (certificateId, certificateData) => {
    try {
      isLoading.value = true
      const updatedCertificate = await adminApi.updateCertificate(certificateId, certificateData)
      const index = certificates.value.findIndex(c => c.id === certificateId)
      if (index !== -1) {
        certificates.value[index] = updatedCertificate
      }
      return updatedCertificate
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to update certificate'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const deleteCertificate = async (certificateId) => {
    try {
      isLoading.value = true
      await adminApi.deleteCertificate(certificateId)
      certificates.value = certificates.value.filter(c => c.id !== certificateId)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete certificate'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Dashboard Actions
  const getDashboardStats = async () => {
    try {
      isLoading.value = true
      const data = await adminApi.getDashboardStats()
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch dashboard stats'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const getRecentVerifications = async () => {
    try {
      const data = await adminApi.getRecentVerifications()
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch recent verifications'
      throw err
    }
  }

  // Analytics Actions
  const getAnalytics = async (timeRange = '30d') => {
    try {
      isLoading.value = true
      const data = await adminApi.getAnalytics(timeRange)
      analytics.value = data
      return data
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to fetch analytics'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const exportAnalyticsReport = async (timeRange = '30d') => {
    try {
      const blob = await adminApi.exportAnalyticsReport(timeRange)
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `neuroscan-analytics-${timeRange}-${new Date().toISOString().split('T')[0]}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to export analytics report'
      throw err
    }
  }

  // Certificate Actions
  const downloadCertificate = async (certificateId) => {
    try {
      const blob = await adminApi.downloadCertificate(certificateId)
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `certificate-${certificateId}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to download certificate'
      throw err
    }
  }

  const revokeCertificate = async (certificateId) => {
    try {
      isLoading.value = true
      await adminApi.revokeCertificate(certificateId)
      
      // Update local state
      const index = certificates.value.findIndex(cert => cert.id === certificateId)
      if (index !== -1) {
        certificates.value[index].status = 'revoked'
      }
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to revoke certificate'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    // State
    customers,
    products,
    certificates,
    scanLogs,
    analytics,
    isLoading,
    error,
    
    // Customer Actions
    fetchCustomers,
    createCustomer,
    updateCustomer,
    deleteCustomer,
    
    // Product Actions
    fetchProducts,
    createProduct,
    updateProduct,
    deleteProduct,
    
    // Certificate Actions
    fetchCertificates,
    createCertificate,
    updateCertificate,
    deleteCertificate,
    
    // Dashboard Actions
    getDashboardStats,
    getRecentVerifications,
      // Dashboard Actions
    getDashboardStats,
    getRecentVerifications,
      // Analytics Actions
    getAnalytics,
    exportAnalyticsReport,
    
    // Certificate Actions
    downloadCertificate,
    revokeCertificate,
    
    // PDF Label Generation
    generateProductLabel: async (productId, options = {}) => {
      try {
        return await adminApi.generateProductLabel(productId, options)
      } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to generate product label'
        throw err
      }
    },
    
    generateCertificateLabel: async (certificateId) => {
      try {
        return await adminApi.generateCertificateLabel(certificateId)
      } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to generate certificate label'
        throw err
      }
    },
    
    generateBatchLabels: async (productIds, options = {}) => {
      try {
        return await adminApi.generateBatchLabels(productIds, options)
      } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to generate batch labels'
        throw err
      }
    },
    
    generateAllProductsLabels: async (options = {}) => {
      try {
        return await adminApi.generateAllProductsLabels(options)
      } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to generate all products labels'
        throw err
      }
    },
    
    generateTemplatePreview: async (labelType = 'product') => {
      try {
        return await adminApi.generateTemplatePreview(labelType)
      } catch (err) {
        error.value = err.response?.data?.detail || 'Failed to generate template preview'
        throw err
      }
    }
  }
})
