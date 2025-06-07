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
              Scan History
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
              <p class="text-gray-400 text-sm">Total Scans</p>
              <p class="text-2xl font-bold text-emerald-400">{{ scanLogs.length }}</p>
            </div>
            <div class="w-10 h-10 bg-emerald-500/20 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="glass-card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">This Month</p>
              <p class="text-2xl font-bold text-blue-400">{{ thisMonthScans }}</p>
            </div>
            <div class="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="glass-card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">Successful</p>
              <p class="text-2xl font-bold text-green-400">{{ successfulScans }}</p>
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
              <p class="text-gray-400 text-sm">Failed</p>
              <p class="text-2xl font-bold text-red-400">{{ failedScans }}</p>
            </div>
            <div class="w-10 h-10 bg-red-500/20 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters and Search -->
      <div class="glass-card p-6 mb-8">
        <div class="flex flex-col lg:flex-row gap-4">
          <div class="flex-1">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search by product name or scan result..."
              class="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-emerald-400"
            >
          </div>
          
          <select
            v-model="statusFilter"
            class="px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white focus:outline-none focus:border-emerald-400"
          >
            <option value="">All Results</option>
            <option value="success">Successful</option>
            <option value="failed">Failed</option>
          </select>

          <select
            v-model="timeFilter"
            class="px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white focus:outline-none focus:border-emerald-400"
          >
            <option value="">All Time</option>
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="year">This Year</option>
          </select>
        </div>
      </div>

      <!-- Scan Logs Table -->
      <div v-if="isLoading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-400"></div>
      </div>

      <div v-else-if="filteredScanLogs.length === 0" class="text-center py-12">
        <div class="w-16 h-16 bg-gray-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <h3 class="text-xl font-semibold text-gray-300 mb-2">No Scan Logs Found</h3>
        <p class="text-gray-400">No scan logs match your current filters.</p>
      </div>

      <div v-else class="glass-card overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-white/5 border-b border-white/10">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Product
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Result
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Scan Time
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Location
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Device
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/10">
              <tr
                v-for="log in paginatedScanLogs"
                :key="log.id"
                class="hover:bg-white/5 transition-colors"
              >
                <td class="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div class="text-sm font-medium text-white">
                      {{ log.product_name || 'Unknown Product' }}
                    </div>
                    <div class="text-sm text-gray-400 font-mono">
                      {{ log.serial_number || 'N/A' }}
                    </div>
                  </div>
                </td>
                
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="{
                      'bg-green-100 text-green-800': log.is_valid,
                      'bg-red-100 text-red-800': !log.is_valid
                    }"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                  >
                    <svg
                      :class="{
                        'text-green-400': log.is_valid,
                        'text-red-400': !log.is_valid
                      }"
                      class="w-3 h-3 mr-1"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        v-if="log.is_valid"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M5 13l4 4L19 7"
                      />
                      <path
                        v-else
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                    {{ log.is_valid ? 'Valid' : 'Invalid' }}
                  </span>
                </td>

                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-white">{{ formatDateTime(log.scanned_at) }}</div>
                  <div class="text-sm text-gray-400">{{ getTimeAgo(log.scanned_at) }}</div>
                </td>

                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-white">
                    {{ log.location || 'Unknown' }}
                  </div>
                  <div class="text-sm text-gray-400">
                    {{ log.ip_address || 'N/A' }}
                  </div>
                </td>

                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-white">
                    {{ log.user_agent ? getDeviceType(log.user_agent) : 'Unknown' }}
                  </div>
                  <div class="text-sm text-gray-400">
                    {{ log.browser_info || 'N/A' }}
                  </div>
                </td>

                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    @click="viewScanDetails(log)"
                    class="text-emerald-400 hover:text-emerald-300 transition-colors mr-3"
                  >
                    View Details
                  </button>
                  <button
                    v-if="log.product_id"
                    @click="viewProduct(log.product_id)"
                    class="text-blue-400 hover:text-blue-300 transition-colors"
                  >
                    View Product
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="px-6 py-4 border-t border-white/10">
          <div class="flex items-center justify-between">
            <div class="text-sm text-gray-400">
              Showing {{ ((currentPage - 1) * pageSize) + 1 }} to {{ Math.min(currentPage * pageSize, filteredScanLogs.length) }} of {{ filteredScanLogs.length }} results
            </div>
            <div class="flex space-x-2">
              <button
                @click="currentPage = Math.max(1, currentPage - 1)"
                :disabled="currentPage === 1"
                :class="{ 'opacity-50 cursor-not-allowed': currentPage === 1 }"
                class="px-3 py-1 glass-button border-emerald-500/30 hover:border-emerald-400/50 text-emerald-400 transition-colors"
              >
                Previous
              </button>
              <span class="px-3 py-1 text-gray-400">
                Page {{ currentPage }} of {{ totalPages }}
              </span>
              <button
                @click="currentPage = Math.min(totalPages, currentPage + 1)"
                :disabled="currentPage === totalPages"
                :class="{ 'opacity-50 cursor-not-allowed': currentPage === totalPages }"
                class="px-3 py-1 glass-button border-emerald-500/30 hover:border-emerald-400/50 text-emerald-400 transition-colors"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Scan Details Modal -->
    <div v-if="selectedScan" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="glass-card max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold text-white">Scan Details</h2>
            <button
              @click="selectedScan = null"
              class="text-gray-400 hover:text-white transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-400 mb-1">Product Name</label>
                <p class="text-white">{{ selectedScan.product_name || 'Unknown Product' }}</p>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-400 mb-1">Serial Number</label>
                <p class="text-white font-mono">{{ selectedScan.serial_number || 'N/A' }}</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-400 mb-1">Scan Result</label>
                <span
                  :class="{
                    'bg-green-100 text-green-800': selectedScan.is_valid,
                    'bg-red-100 text-red-800': !selectedScan.is_valid
                  }"
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                >
                  {{ selectedScan.is_valid ? 'Valid' : 'Invalid' }}
                </span>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-400 mb-1">Scan Time</label>
                <p class="text-gray-300">{{ formatDateTime(selectedScan.scanned_at) }}</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-400 mb-1">IP Address</label>
                <p class="text-gray-300">{{ selectedScan.ip_address || 'N/A' }}</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-400 mb-1">Location</label>
                <p class="text-gray-300">{{ selectedScan.location || 'Unknown' }}</p>
              </div>

              <div class="md:col-span-2">
                <label class="block text-sm font-medium text-gray-400 mb-1">User Agent</label>
                <p class="text-gray-300 text-sm break-all">{{ selectedScan.user_agent || 'N/A' }}</p>
              </div>

              <div v-if="selectedScan.notes" class="md:col-span-2">
                <label class="block text-sm font-medium text-gray-400 mb-1">Notes</label>
                <p class="text-gray-300">{{ selectedScan.notes }}</p>
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
const timeFilter = ref('')
const selectedScan = ref(null)
const isLoading = ref(false)
const currentPage = ref(1)
const pageSize = 10

const scanLogs = computed(() => customerStore.scanLogs || [])

const filteredScanLogs = computed(() => {
  let filtered = scanLogs.value

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(log =>
      (log.product_name && log.product_name.toLowerCase().includes(query)) ||
      (log.serial_number && log.serial_number.toLowerCase().includes(query))
    )
  }

  // Status filter
  if (statusFilter.value) {
    if (statusFilter.value === 'success') {
      filtered = filtered.filter(log => log.is_valid)
    } else if (statusFilter.value === 'failed') {
      filtered = filtered.filter(log => !log.is_valid)
    }
  }

  // Time filter
  if (timeFilter.value) {
    const now = new Date()
    filtered = filtered.filter(log => {
      const scanDate = new Date(log.scanned_at)
      
      switch (timeFilter.value) {
        case 'today':
          return scanDate.toDateString() === now.toDateString()
        case 'week':
          const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
          return scanDate >= weekAgo
        case 'month':
          const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
          return scanDate >= monthAgo
        case 'year':
          const yearAgo = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000)
          return scanDate >= yearAgo
        default:
          return true
      }
    })
  }

  return filtered
})

const paginatedScanLogs = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return filteredScanLogs.value.slice(start, end)
})

const totalPages = computed(() => Math.ceil(filteredScanLogs.value.length / pageSize))

const thisMonthScans = computed(() => {
  const now = new Date()
  const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
  return scanLogs.value.filter(log => new Date(log.scanned_at) >= monthAgo).length
})

const successfulScans = computed(() => 
  scanLogs.value.filter(log => log.is_valid).length
)

const failedScans = computed(() => 
  scanLogs.value.filter(log => !log.is_valid).length
)

const formatDateTime = (dateString) => {
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getTimeAgo = (dateString) => {
  const now = new Date()
  const scanDate = new Date(dateString)
  const diffMs = now - scanDate
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffHours / 24)

  if (diffDays > 0) {
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
  } else if (diffHours > 0) {
    return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
  } else {
    const diffMinutes = Math.floor(diffMs / (1000 * 60))
    return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`
  }
}

const getDeviceType = (userAgent) => {
  if (!userAgent) return 'Unknown'
  
  if (userAgent.includes('Mobile')) return 'Mobile'
  if (userAgent.includes('Tablet')) return 'Tablet'
  if (userAgent.includes('Windows')) return 'Windows PC'
  if (userAgent.includes('Mac')) return 'Mac'
  if (userAgent.includes('Linux')) return 'Linux'
  
  return 'Desktop'
}

const viewScanDetails = (scan) => {
  selectedScan.value = scan
}

const viewProduct = (productId) => {
  router.push(`/customer/products?highlight=${productId}`)
}

const logout = () => {
  customerStore.logout()
  router.push('/customer/login')
}

onMounted(async () => {
  try {
    isLoading.value = true
    await customerStore.fetchScanLogs()
  } catch (error) {
    console.error('Failed to load scan logs:', error)
  } finally {
    isLoading.value = false
  }
})
</script>
