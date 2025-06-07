<template>
  <div class="min-h-screen bg-gradient-to-br from-dark via-gray-900 to-dark text-white">
    <!-- Header -->
    <header class="glass-nav border-b border-emerald-500/20">
      <div class="container mx-auto px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <router-link
              to="/customer/dashboard"
              class="text-gray-400 hover:text-emerald-400 transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </router-link>
            <h1 class="text-2xl font-bold bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">
              My Certificates
            </h1>
          </div>
          
          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-300">{{ customerStore.customerName }}</span>
            <button
              @click="logout"
              class="px-4 py-2 glass-button text-red-400 border-red-500/30 hover:border-red-400/50"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <div class="container mx-auto px-6 py-8">
      <!-- Summary Stats -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="glass-card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">Total Certificates</p>
              <p class="text-2xl font-bold text-emerald-400">{{ certificates.length }}</p>
            </div>
            <div class="w-10 h-10 bg-emerald-500/20 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="glass-card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">Active</p>
              <p class="text-2xl font-bold text-green-400">{{ activeCertificates }}</p>
            </div>
            <div class="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="glass-card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">Expiring Soon</p>
              <p class="text-2xl font-bold text-yellow-400">{{ expiringSoon }}</p>
            </div>
            <div class="w-10 h-10 bg-yellow-500/20 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="glass-card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">Expired</p>
              <p class="text-2xl font-bold text-red-400">{{ expiredCertificates }}</p>
            </div>
            <div class="w-10 h-10 bg-red-500/20 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Search and Filter -->
      <div class="glass-card p-6 mb-8">
        <div class="flex flex-col md:flex-row gap-4">
          <div class="flex-1">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search certificates by product name or certificate ID..."
              class="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-emerald-400"
            >
          </div>
          <select
            v-model="statusFilter"
            class="px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white focus:outline-none focus:border-emerald-400"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="expired">Expired</option>
            <option value="expiring">Expiring Soon</option>
          </select>
        </div>
      </div>

      <!-- Certificates List -->
      <div v-if="isLoading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-400"></div>
      </div>

      <div v-else-if="filteredCertificates.length === 0" class="text-center py-12">
        <div class="w-16 h-16 bg-gray-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 class="text-xl font-semibold text-gray-300 mb-2">No Certificates Found</h3>
        <p class="text-gray-400">No certificates match your current search criteria.</p>
      </div>

      <div v-else class="space-y-6">
        <div
          v-for="certificate in filteredCertificates"
          :key="certificate.id"
          class="glass-card p-6 hover:border-emerald-400/50 transition-colors"
        >
          <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            <!-- Certificate Info -->
            <div class="flex-1">
              <div class="flex items-center gap-4 mb-4">
                <h3 class="text-lg font-semibold text-white">{{ certificate.product_name }}</h3>
                <span
                  :class="getCertificateStatusClass(certificate)"
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                >
                  {{ getCertificateStatus(certificate) }}
                </span>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <label class="block text-xs font-medium text-gray-400 mb-1">Certificate ID</label>
                  <p class="text-sm text-white font-mono">{{ certificate.certificate_id }}</p>
                </div>
                
                <div>
                  <label class="block text-xs font-medium text-gray-400 mb-1">Issue Date</label>
                  <p class="text-sm text-gray-300">{{ formatDate(certificate.issue_date) }}</p>
                </div>

                <div>
                  <label class="block text-xs font-medium text-gray-400 mb-1">Expiry Date</label>
                  <p class="text-sm text-gray-300">{{ formatDate(certificate.expiry_date) }}</p>
                </div>

                <div v-if="certificate.issuer">
                  <label class="block text-xs font-medium text-gray-400 mb-1">Issuer</label>
                  <p class="text-sm text-gray-300">{{ certificate.issuer }}</p>
                </div>

                <div>
                  <label class="block text-xs font-medium text-gray-400 mb-1">Verification Count</label>
                  <p class="text-sm text-gray-300">{{ certificate.verification_count || 0 }}</p>
                </div>

                <div>
                  <label class="block text-xs font-medium text-gray-400 mb-1">Last Verified</label>
                  <p class="text-sm text-gray-300">
                    {{ certificate.last_verified ? formatDate(certificate.last_verified) : 'Never' }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex flex-col gap-2 lg:w-48">
              <button
                @click="viewCertificate(certificate)"
                class="px-4 py-2 glass-button border-emerald-500/30 hover:border-emerald-400/50 text-emerald-400 transition-colors"
              >
                View Details
              </button>
              
              <button
                v-if="certificate.pdf_url"
                @click="downloadCertificate(certificate)"
                class="px-4 py-2 glass-button border-blue-500/30 hover:border-blue-400/50 text-blue-400 transition-colors"
              >
                Download PDF
              </button>

              <button
                @click="verifyCertificate(certificate)"
                class="px-4 py-2 glass-button border-green-500/30 hover:border-green-400/50 text-green-400 transition-colors"
              >
                Verify Now
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Certificate Detail Modal -->
    <div v-if="selectedCertificate" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="glass-card max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold text-white">Certificate Details</h2>
            <button
              @click="selectedCertificate = null"
              class="text-gray-400 hover:text-white transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-400 mb-1">Product Name</label>
                <p class="text-white">{{ selectedCertificate.product_name }}</p>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-400 mb-1">Certificate ID</label>
                <p class="text-white font-mono">{{ selectedCertificate.certificate_id }}</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-400 mb-1">Status</label>
                <span
                  :class="getCertificateStatusClass(selectedCertificate)"
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                >
                  {{ getCertificateStatus(selectedCertificate) }}
                </span>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-400 mb-1">Issue Date</label>
                <p class="text-gray-300">{{ formatDate(selectedCertificate.issue_date) }}</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-400 mb-1">Expiry Date</label>
                <p class="text-gray-300">{{ formatDate(selectedCertificate.expiry_date) }}</p>
              </div>

              <div v-if="selectedCertificate.issuer">
                <label class="block text-sm font-medium text-gray-400 mb-1">Issuer</label>
                <p class="text-gray-300">{{ selectedCertificate.issuer }}</p>
              </div>
            </div>

            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-400 mb-1">Verification Count</label>
                <p class="text-gray-300">{{ selectedCertificate.verification_count || 0 }}</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-400 mb-1">Last Verified</label>
                <p class="text-gray-300">
                  {{ selectedCertificate.last_verified ? formatDate(selectedCertificate.last_verified) : 'Never' }}
                </p>
              </div>

              <div v-if="selectedCertificate.description">
                <label class="block text-sm font-medium text-gray-400 mb-1">Description</label>
                <p class="text-gray-300">{{ selectedCertificate.description }}</p>
              </div>

              <div class="flex flex-col gap-3 pt-4">
                <button
                  v-if="selectedCertificate.pdf_url"
                  @click="downloadCertificate(selectedCertificate)"
                  class="px-4 py-2 glass-button border-blue-500/30 hover:border-blue-400/50 text-blue-400 transition-colors"
                >
                  Download Certificate PDF
                </button>

                <button
                  @click="verifyCertificate(selectedCertificate)"
                  class="px-4 py-2 glass-button border-green-500/30 hover:border-green-400/50 text-green-400 transition-colors"
                >
                  Verify Certificate
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCustomerStore } from '@/stores/customer'

const router = useRouter()
const customerStore = useCustomerStore()

const searchQuery = ref('')
const statusFilter = ref('')
const selectedCertificate = ref(null)
const isLoading = ref(false)

const certificates = computed(() => customerStore.certificates || [])

const filteredCertificates = computed(() => {
  let filtered = certificates.value

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(cert =>
      cert.product_name.toLowerCase().includes(query) ||
      cert.certificate_id.toLowerCase().includes(query)
    )
  }

  // Status filter
  if (statusFilter.value) {
    filtered = filtered.filter(cert => {
      const status = getCertificateStatus(cert).toLowerCase()
      return status.includes(statusFilter.value)
    })
  }

  return filtered
})

const activeCertificates = computed(() => 
  certificates.value.filter(cert => !isExpired(cert)).length
)

const expiredCertificates = computed(() => 
  certificates.value.filter(cert => isExpired(cert)).length
)

const expiringSoon = computed(() => 
  certificates.value.filter(cert => isExpiringSoon(cert) && !isExpired(cert)).length
)

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const isExpired = (certificate) => {
  return new Date(certificate.expiry_date) < new Date()
}

const isExpiringSoon = (certificate) => {
  const expiryDate = new Date(certificate.expiry_date)
  const today = new Date()
  const thirtyDaysFromNow = new Date(today.getTime() + (30 * 24 * 60 * 60 * 1000))
  return expiryDate <= thirtyDaysFromNow && expiryDate > today
}

const getCertificateStatus = (certificate) => {
  if (isExpired(certificate)) {
    return 'Expired'
  } else if (isExpiringSoon(certificate)) {
    return 'Expiring Soon'
  } else {
    return 'Active'
  }
}

const getCertificateStatusClass = (certificate) => {
  if (isExpired(certificate)) {
    return 'bg-red-100 text-red-800'
  } else if (isExpiringSoon(certificate)) {
    return 'bg-yellow-100 text-yellow-800'
  } else {
    return 'bg-green-100 text-green-800'
  }
}

const viewCertificate = (certificate) => {
  selectedCertificate.value = certificate
}

const downloadCertificate = (certificate) => {
  if (certificate.pdf_url) {
    const link = document.createElement('a')
    link.href = certificate.pdf_url
    link.download = `${certificate.product_name}-certificate.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

const verifyCertificate = (certificate) => {
  // Navigate to verification page with certificate ID
  window.open(`/verify/${certificate.certificate_id}`, '_blank')
}

const logout = () => {
  customerStore.logout()
  router.push('/customer/login')
}

onMounted(async () => {
  try {
    isLoading.value = true
    await customerStore.fetchCertificates()
  } catch (error) {
    console.error('Failed to load certificates:', error)
  } finally {
    isLoading.value = false
  }
})
</script>
