<template>
  <div class="min-h-screen pt-20">
    <!-- Navigation (simplified) -->
    <nav class="navbar-glass fixed w-full top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <router-link to="/" class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-gradient-primary rounded-xl flex items-center justify-center neon-glow">
              <span class="text-white font-bold text-xl">N</span>
            </div>
            <span class="text-xl font-bold text-gradient">NeuroScan</span>
          </router-link>
          
          <router-link to="/" class="text-gray-300 hover:text-primary-400 transition-colors">
            ← Back to Home
          </router-link>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-4xl md:text-5xl font-bold text-white mb-6">
          Product <span class="text-gradient">Verification</span>
        </h1>
        <p class="text-xl text-gray-300">
          Verify product authenticity using QR code scanning or serial number entry
        </p>
      </div>

      <!-- Verification Methods -->
      <div class="grid md:grid-cols-2 gap-8 mb-12">
        <!-- QR Code Scanner -->
        <div class="glass-card">
          <div class="text-center mb-6">
            <div class="w-16 h-16 bg-primary-500/20 rounded-2xl flex items-center justify-center mb-4 mx-auto neon-border">
              <svg class="w-8 h-8 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V6a1 1 0 00-1-1H5a1 1 0 00-1 1v1a1 1 0 001 1zm12 0h2a1 1 0 001-1V6a1 1 0 00-1-1h-2a1 1 0 00-1 1v1a1 1 0 001 1zM5 20h2a1 1 0 001-1v-1a1 1 0 00-1-1H5a1 1 0 00-1 1v1a1 1 0 001 1z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold text-white mb-2">Scan QR Code</h3>
            <p class="text-gray-400 mb-6">Use your camera to scan the product QR code</p>
          </div>

          <!-- QR Scanner Component -->
          <div v-if="!isScanning" class="text-center">
            <button 
              @click="startScanning" 
              class="glass-button bg-gradient-primary hover:scale-105 transform transition-all duration-300 neon-glow px-6 py-3 font-semibold"
              :disabled="verificationStore.isLoading"
            >
              <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Start Camera
            </button>
          </div>

          <div v-else class="space-y-4">
            <div id="qr-reader" class="w-full rounded-lg overflow-hidden bg-black"></div>
            <button 
              @click="stopScanning" 
              class="w-full glass-button hover:bg-red-500/20 text-red-400 border-red-500/30"
            >
              Stop Scanner
            </button>
          </div>
        </div>

        <!-- Manual Entry -->
        <div class="glass-card">
          <div class="text-center mb-6">
            <div class="w-16 h-16 bg-accent-500/20 rounded-2xl flex items-center justify-center mb-4 mx-auto neon-border">
              <svg class="w-8 h-8 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold text-white mb-2">Enter Serial Number</h3>
            <p class="text-gray-400 mb-6">Manually enter the product serial number</p>
          </div>

          <form @submit.prevent="verifySerial" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">
                Serial Number
              </label>
              <input
                v-model="serialNumber"
                type="text"
                placeholder="NS-20250531120000-1234-ABCD-12345678"
                class="glass-input w-full"
                :disabled="verificationStore.isLoading"
              />
              <p class="text-xs text-gray-500 mt-1">
                Format: NS-YYYYMMDDHHMMSS-PPPP-CCCC-XXXXXXXX
              </p>
            </div>
            
            <button 
              type="submit" 
              class="w-full glass-button bg-gradient-accent hover:scale-105 transform transition-all duration-300 neon-glow py-3 font-semibold"
              :disabled="!serialNumber.trim() || verificationStore.isLoading"
            >
              <div v-if="verificationStore.isLoading" class="flex items-center justify-center">
                <div class="loading-spinner mr-2"></div>
                Verifying...
              </div>
              <div v-else class="flex items-center justify-center">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Verify Product
              </div>
            </button>
          </form>
        </div>
      </div>

      <!-- Verification Result -->
      <div v-if="verificationStore.currentVerification" class="glass-card mb-8 animate-slide-up">
        <div class="text-center mb-6">
          <h3 class="text-2xl font-bold text-white mb-4">Verification Result</h3>
          
          <!-- Status Badge -->
          <div class="inline-flex items-center px-6 py-3 rounded-full text-lg font-semibold mb-6"
               :class="getStatusClass(verificationStore.verificationStatus)">
            <svg class="w-6 h-6 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path v-if="verificationStore.verificationStatus === 'verified'" 
                    fill-rule="evenodd" 
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" 
                    clip-rule="evenodd" />
              <path v-else 
                    fill-rule="evenodd" 
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" 
                    clip-rule="evenodd" />
            </svg>
            {{ getStatusText(verificationStore.verificationStatus) }}
          </div>
        </div>

        <!-- Product Details -->
        <div v-if="verificationStore.currentVerification.is_valid && verificationStore.currentVerification.certificate" 
             class="grid md:grid-cols-2 gap-6">
          <div>
            <h4 class="text-lg font-semibold text-white mb-3">Product Information</h4>
            <div class="space-y-2">
              <div class="flex justify-between">
                <span class="text-gray-400">Product Name:</span>
                <span class="text-white">{{ verificationStore.currentVerification.certificate.product?.name || 'N/A' }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">Model:</span>
                <span class="text-white">{{ verificationStore.currentVerification.certificate.product?.model || 'N/A' }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">Serial Number:</span>
                <span class="text-white font-mono text-sm">{{ verificationStore.currentVerification.serial_number }}</span>
              </div>
            </div>
          </div>
          
          <div>
            <h4 class="text-lg font-semibold text-white mb-3">Certificate Details</h4>
            <div class="space-y-2">
              <div class="flex justify-between">
                <span class="text-gray-400">Issue Date:</span>
                <span class="text-white">{{ formatDate(verificationStore.currentVerification.certificate.issue_date) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">Valid Until:</span>
                <span class="text-white">{{ formatDate(verificationStore.currentVerification.certificate.expiry_date) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">Customer:</span>
                <span class="text-white">{{ verificationStore.currentVerification.certificate.customer?.name || 'N/A' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-else-if="!verificationStore.currentVerification.is_valid" class="text-center">
          <p class="text-red-400 mb-4">
            {{ verificationStore.currentVerification.error || 'Product verification failed. This product may be counterfeit or the serial number is invalid.' }}
          </p>
          <div class="glass-effect p-4 rounded-lg border border-red-500/30 bg-red-500/10">
            <h4 class="text-red-400 font-semibold mb-2">⚠️ Security Warning</h4>
            <p class="text-gray-300 text-sm">
              This product could not be verified through our authentication system. Please contact the manufacturer or authorized dealer to confirm authenticity.
            </p>
          </div>
        </div>
      </div>

      <!-- Help Section -->
      <div class="glass-card">
        <h3 class="text-xl font-bold text-white mb-4">Need Help?</h3>
        <div class="grid md:grid-cols-2 gap-6">
          <div>
            <h4 class="text-lg font-semibold text-white mb-2">QR Code Scanning</h4>
            <ul class="text-gray-300 space-y-1 text-sm">
              <li>• Ensure good lighting conditions</li>
              <li>• Hold camera steady and close to QR code</li>
              <li>• Allow camera permissions when prompted</li>
              <li>• QR code should be clearly visible and undamaged</li>
            </ul>
          </div>
          
          <div>
            <h4 class="text-lg font-semibold text-white mb-2">Serial Number Format</h4>
            <ul class="text-gray-300 space-y-1 text-sm">
              <li>• Format: NS-YYYYMMDDHHMMSS-PPPP-CCCC-XXXXXXXX</li>
              <li>• NS = NeuroScan prefix</li>
              <li>• YYYY = Year, MM = Month, DD = Day</li>
              <li>• Check product label or documentation</li>
            </ul>
          </div>
        </div>
        
        <div class="mt-6 text-center">
          <router-link 
            to="/contact" 
            class="glass-button hover:scale-105 transform transition-all duration-300 px-6 py-2"
          >
            Contact Support
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useVerificationStore } from '@/stores/verification'
import { useToast } from 'vue-toastification'
import { Html5QrcodeScanner } from 'html5-qrcode'
import moment from 'moment'

export default {
  name: 'Verify',
  props: {
    serialNumber: String
  },
  setup(props) {
    const route = useRoute()
    const verificationStore = useVerificationStore()
    const toast = useToast()
    
    const serialNumber = ref(props.serialNumber || route.params.serialNumber || '')
    const isScanning = ref(false)
    let qrScanner = null

    const startScanning = () => {
      isScanning.value = true
      
      // Initialize QR scanner
      qrScanner = new Html5QrcodeScanner(
        "qr-reader",
        { 
          fps: 10, 
          qrbox: { width: 250, height: 250 },
          aspectRatio: 1.0
        },
        false
      )
      
      qrScanner.render(
        (decodedText) => {
          // QR code successfully scanned
          console.log('QR code scanned:', decodedText)
          
          // Extract serial number from QR code
          let extractedSerial = decodedText
          if (decodedText.includes('serial=')) {
            extractedSerial = decodedText.split('serial=')[1].split('&')[0]
          } else if (decodedText.startsWith('NS-')) {
            extractedSerial = decodedText
          }
          
          serialNumber.value = extractedSerial
          stopScanning()
          verifySerial()
        },
        (error) => {
          // QR code scanning error (not critical)
          console.log('QR scan error:', error)
        }
      )
    }

    const stopScanning = () => {
      if (qrScanner) {
        qrScanner.clear()
        qrScanner = null
      }
      isScanning.value = false
    }

    const verifySerial = async () => {
      if (!serialNumber.value.trim()) {
        toast.error('Please enter a serial number')
        return
      }

      try {
        await verificationStore.verifyProduct(serialNumber.value.trim())
        
        if (verificationStore.verificationStatus === 'verified') {
          toast.success('Product verified successfully!')
        } else {
          toast.error('Product verification failed')
        }
      } catch (error) {
        console.error('Verification error:', error)
        toast.error('Verification failed. Please try again.')
      }
    }

    const getStatusClass = (status) => {
      switch (status) {
        case 'verified':
          return 'status-verified'
        case 'invalid':
          return 'status-invalid'
        default:
          return 'status-pending'
      }
    }

    const getStatusText = (status) => {
      switch (status) {
        case 'verified':
          return 'Verified Authentic'
        case 'invalid':
          return 'Invalid Product'
        default:
          return 'Unknown Status'
      }
    }

    const formatDate = (dateString) => {
      return moment(dateString).format('MMM DD, YYYY')
    }

    // Auto-verify if serial number is provided in route
    onMounted(() => {
      if (serialNumber.value) {
        verifySerial()
      }
    })

    // Cleanup scanner on unmount
    onUnmounted(() => {
      stopScanning()
    })

    return {
      verificationStore,
      serialNumber,
      isScanning,
      startScanning,
      stopScanning,
      verifySerial,
      getStatusClass,
      getStatusText,
      formatDate
    }
  }
}
</script>
