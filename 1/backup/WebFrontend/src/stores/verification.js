import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { verificationApi } from '@/api/verification'

export const useVerificationStore = defineStore('verification', () => {
  // State
  const currentVerification = ref(null)
  const verificationHistory = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  const scanStats = ref({
    totalScans: 0,
    verifiedScans: 0,
    invalidScans: 0,
    todayScans: 0
  })

  // Getters
  const verificationStatus = computed(() => {
    if (!currentVerification.value) return null
    return currentVerification.value.is_valid ? 'verified' : 'invalid'
  })

  const verificationRate = computed(() => {
    if (scanStats.value.totalScans === 0) return 0
    return Math.round((scanStats.value.verifiedScans / scanStats.value.totalScans) * 100)
  })

  // Actions
  const verifyProduct = async (serialNumber) => {
    try {
      isLoading.value = true
      error.value = null
      
      const result = await verificationApi.verifyProduct(serialNumber)
      currentVerification.value = result
      
      // Add to history
      verificationHistory.value.unshift({
        ...result,
        scanned_at: new Date().toISOString()
      })
      
      // Keep only last 50 scans in memory
      if (verificationHistory.value.length > 50) {
        verificationHistory.value = verificationHistory.value.slice(0, 50)
      }
      
      return result
    } catch (err) {
      error.value = err.response?.data?.detail || 'Verification failed'
      currentVerification.value = {
        is_valid: false,
        error: error.value,
        serial_number: serialNumber
      }
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const getScanStats = async () => {
    try {
      const stats = await verificationApi.getScanStats()
      scanStats.value = stats
      return stats
    } catch (err) {
      console.error('Failed to fetch scan stats:', err)
    }
  }

  const clearVerification = () => {
    currentVerification.value = null
    error.value = null
  }

  const clearHistory = () => {
    verificationHistory.value = []
  }

  return {
    // State
    currentVerification,
    verificationHistory,
    isLoading,
    error,
    scanStats,
    
    // Getters
    verificationStatus,
    verificationRate,
    
    // Actions
    verifyProduct,
    getScanStats,
    clearVerification,
    clearHistory
  }
})
