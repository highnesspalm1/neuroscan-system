<template>
  <div class="min-h-screen bg-gradient-to-br from-dark via-gray-900 to-dark text-white">
    <!-- Header -->
    <header class="glass-nav border-b border-cyan-500/20">
      <div class="container mx-auto px-6 py-4">
        <div class="flex items-center space-x-4">
          <router-link
            to="/admin/dashboard"
            class="text-gray-400 hover:text-cyan-400 transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </router-link>
          <h1 class="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
            Certificate Management
          </h1>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <div class="container mx-auto px-6 py-8">
      <!-- Filters -->
      <div class="glass-card p-6 mb-8">
        <div class="flex flex-col md:flex-row gap-4">
          <div class="flex-1">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search certificates..."
              class="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-cyan-400 transition-colors"
            >
          </div>
          <select
            v-model="statusFilter"
            class="px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-cyan-400 transition-colors"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="expired">Expired</option>
            <option value="revoked">Revoked</option>
          </select>
          <button
            @click="loadCertificates"
            class="px-4 py-2 glass-button border-cyan-500/30 hover:border-cyan-400/50 text-cyan-400"
          >
            <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>
      </div>

      <!-- Certificates Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        <div
          v-for="certificate in filteredCertificates"
          :key="certificate.id"
          class="glass-card p-6 hover:border-cyan-500/30 transition-colors"
        >
          <!-- Certificate Header -->
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-3">
              <div class="w-12 h-12 bg-cyan-500/20 rounded-lg flex items-center justify-center">
                <svg class="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <h3 class="font-semibold text-white">{{ certificate.product_name }}</h3>
                <p class="text-sm text-gray-400">{{ certificate.product_brand }}</p>
              </div>
            </div>
            <span
              :class="[
                'px-2 py-1 text-xs font-medium rounded-full',
                getStatusClass(certificate.status)
              ]"
            >
              {{ certificate.status }}
            </span>
          </div>

          <!-- Certificate Details -->
          <div class="space-y-3 mb-6">
            <div class="flex justify-between">
              <span class="text-gray-400">Serial Number:</span>
              <span class="text-white font-mono text-sm">{{ certificate.serial_number }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-400">Certificate ID:</span>
              <span class="text-white font-mono text-sm">{{ certificate.certificate_id.substring(0, 8) }}...</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-400">Issue Date:</span>
              <span class="text-white">{{ formatDate(certificate.issue_date) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-400">Expiry Date:</span>
              <span
                :class="[
                  isExpiringSoon(certificate.expiry_date) ? 'text-yellow-400' : 'text-white'
                ]"
              >
                {{ formatDate(certificate.expiry_date) }}
              </span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-400">Verifications:</span>
              <span class="text-cyan-400">{{ certificate.verification_count || 0 }}</span>
            </div>
          </div>

          <!-- Certificate Actions -->
          <div class="flex space-x-2">
            <button
              @click="viewCertificate(certificate)"
              class="flex-1 px-3 py-2 glass-button border-cyan-500/30 hover:border-cyan-400/50 text-cyan-400 text-sm"
            >
              View
            </button>
            <button
              @click="downloadCertificate(certificate)"
              class="flex-1 px-3 py-2 glass-button border-green-500/30 hover:border-green-400/50 text-green-400 text-sm"
            >
              Download
            </button>
            <button
              v-if="certificate.status === 'active'"
              @click="revokeCertificate(certificate)"
              class="flex-1 px-3 py-2 glass-button border-red-500/30 hover:border-red-400/50 text-red-400 text-sm"
            >
              Revoke
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredCertificates.length === 0" class="text-center py-12">
        <div class="w-24 h-24 bg-gray-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 class="text-xl font-semibold text-gray-400 mb-2">No certificates found</h3>
        <p class="text-gray-500">There are no certificates matching your search criteria.</p>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="flex justify-center mt-8">
        <div class="flex space-x-2">
          <button
            @click="currentPage--"
            :disabled="currentPage === 1"
            class="px-3 py-2 glass-button border-white/20 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <span class="px-4 py-2 text-gray-300">
            Page {{ currentPage }} of {{ totalPages }}
          </span>
          <button
            @click="currentPage++"
            :disabled="currentPage === totalPages"
            class="px-3 py-2 glass-button border-white/20 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- Certificate Details Modal -->
    <div
      v-if="showDetailsModal"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
      @click.self="showDetailsModal = false"
    >
      <div class="glass-card p-6 w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-xl font-semibold text-cyan-400">Certificate Details</h3>
          <button
            @click="showDetailsModal = false"
            class="text-gray-400 hover:text-white transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div v-if="selectedCertificate" class="space-y-6">
          <!-- Basic Information -->
          <div class="glass-card p-4">
            <h4 class="text-lg font-semibold text-white mb-4">Basic Information</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm text-gray-400 mb-1">Product Name</label>
                <p class="text-white">{{ selectedCertificate.product_name }}</p>
              </div>
              <div>
                <label class="block text-sm text-gray-400 mb-1">Brand</label>
                <p class="text-white">{{ selectedCertificate.product_brand }}</p>
              </div>
              <div>
                <label class="block text-sm text-gray-400 mb-1">Serial Number</label>
                <p class="text-white font-mono">{{ selectedCertificate.serial_number }}</p>
              </div>
              <div>
                <label class="block text-sm text-gray-400 mb-1">Certificate ID</label>
                <p class="text-white font-mono text-sm">{{ selectedCertificate.certificate_id }}</p>
              </div>
            </div>
          </div>

          <!-- Certificate Status -->
          <div class="glass-card p-4">
            <h4 class="text-lg font-semibold text-white mb-4">Certificate Status</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm text-gray-400 mb-1">Status</label>
                <span
                  :class="[
                    'px-3 py-1 text-sm font-medium rounded-full',
                    getStatusClass(selectedCertificate.status)
                  ]"
                >
                  {{ selectedCertificate.status }}
                </span>
              </div>
              <div>
                <label class="block text-sm text-gray-400 mb-1">Verification Count</label>
                <p class="text-cyan-400 text-lg font-semibold">{{ selectedCertificate.verification_count || 0 }}</p>
              </div>
              <div>
                <label class="block text-sm text-gray-400 mb-1">Issue Date</label>
                <p class="text-white">{{ formatDate(selectedCertificate.issue_date) }}</p>
              </div>
              <div>
                <label class="block text-sm text-gray-400 mb-1">Expiry Date</label>
                <p
                  :class="[
                    isExpiringSoon(selectedCertificate.expiry_date) ? 'text-yellow-400' : 'text-white'
                  ]"
                >
                  {{ formatDate(selectedCertificate.expiry_date) }}
                </p>
              </div>
            </div>
          </div>

          <!-- Digital Signature -->
          <div class="glass-card p-4">
            <h4 class="text-lg font-semibold text-white mb-4">Digital Signature</h4>
            <div class="bg-gray-800/50 p-4 rounded-lg">
              <p class="text-xs font-mono text-gray-300 break-all">
                {{ selectedCertificate.digital_signature || 'No signature available' }}
              </p>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex justify-end space-x-3">
            <button
              @click="downloadCertificate(selectedCertificate)"
              class="px-4 py-2 glass-button border-green-500/30 hover:border-green-400/50 text-green-400"
            >
              Download PDF
            </button>
            <button
              v-if="selectedCertificate.status === 'active'"
              @click="revokeCertificate(selectedCertificate)"
              class="px-4 py-2 glass-button border-red-500/30 hover:border-red-400/50 text-red-400"
            >
              Revoke Certificate
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAdminStore } from '@/stores/admin'

const adminStore = useAdminStore()

// Data
const certificates = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const itemsPerPage = 9

// Modals
const showDetailsModal = ref(false)
const selectedCertificate = ref(null)

// Computed
const filteredCertificates = computed(() => {
  let filtered = certificates.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(cert =>
      cert.product_name.toLowerCase().includes(query) ||
      cert.product_brand.toLowerCase().includes(query) ||
      cert.serial_number.toLowerCase().includes(query) ||
      cert.certificate_id.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(cert => cert.status === statusFilter.value)
  }

  const start = (currentPage.value - 1) * itemsPerPage
  return filtered.slice(start, start + itemsPerPage)
})

const totalPages = computed(() => {
  let filtered = certificates.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(cert =>
      cert.product_name.toLowerCase().includes(query) ||
      cert.product_brand.toLowerCase().includes(query) ||
      cert.serial_number.toLowerCase().includes(query) ||
      cert.certificate_id.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(cert => cert.status === statusFilter.value)
  }

  return Math.ceil(filtered.length / itemsPerPage)
})

// Methods
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const getStatusClass = (status) => {
  switch (status) {
    case 'active':
      return 'bg-green-500/20 text-green-400'
    case 'expired':
      return 'bg-yellow-500/20 text-yellow-400'
    case 'revoked':
      return 'bg-red-500/20 text-red-400'
    default:
      return 'bg-gray-500/20 text-gray-400'
  }
}

const isExpiringSoon = (expiryDate) => {
  const expiry = new Date(expiryDate)
  const now = new Date()
  const daysUntilExpiry = Math.ceil((expiry - now) / (1000 * 60 * 60 * 24))
  return daysUntilExpiry <= 30 && daysUntilExpiry > 0
}

const loadCertificates = async () => {
  try {
    certificates.value = await adminStore.getCertificates()
  } catch (error) {
    console.error('Failed to load certificates:', error)
  }
}

const viewCertificate = (certificate) => {
  selectedCertificate.value = certificate
  showDetailsModal.value = true
}

const downloadCertificate = async (certificate) => {
  try {
    await adminStore.downloadCertificate(certificate.id)
  } catch (error) {
    console.error('Failed to download certificate:', error)
  }
}

const revokeCertificate = async (certificate) => {
  if (confirm(`Are you sure you want to revoke the certificate for ${certificate.product_name}?`)) {
    try {
      await adminStore.revokeCertificate(certificate.id)
      await loadCertificates()
      if (showDetailsModal.value) {
        showDetailsModal.value = false
      }
    } catch (error) {
      console.error('Failed to revoke certificate:', error)
    }
  }
}

onMounted(() => {
  loadCertificates()
})
</script>
