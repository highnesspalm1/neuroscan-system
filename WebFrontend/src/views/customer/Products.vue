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
              My Products
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
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="glass-card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">Total Products</p>
              <p class="text-2xl font-bold text-emerald-400">{{ products.length }}</p>
            </div>
            <div class="w-10 h-10 bg-emerald-500/20 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
          </div>
        </div>

        <div class="glass-card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">Active Products</p>
              <p class="text-2xl font-bold text-green-400">{{ activeProducts }}</p>
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
              <p class="text-gray-400 text-sm">Verified Products</p>
              <p class="text-2xl font-bold text-blue-400">{{ verifiedProducts }}</p>
            </div>
            <div class="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
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
              placeholder="Search products by name or serial number..."
              class="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-emerald-400"
            >
          </div>
          <select
            v-model="statusFilter"
            class="px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white focus:outline-none focus:border-emerald-400"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </div>

      <!-- Products Grid -->
      <div v-if="isLoading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-400"></div>
      </div>

      <div v-else-if="filteredProducts.length === 0" class="text-center py-12">
        <div class="w-16 h-16 bg-gray-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
        </div>
        <h3 class="text-xl font-semibold text-gray-300 mb-2">No Products Found</h3>
        <p class="text-gray-400">No products match your current search criteria.</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="product in filteredProducts"
          :key="product.id"
          class="glass-card p-6 hover:border-emerald-400/50 transition-colors"
        >
          <!-- Product Header -->
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-white">{{ product.name }}</h3>
            <span
              :class="{
                'bg-green-100 text-green-800': product.is_active,
                'bg-red-100 text-red-800': !product.is_active
              }"
              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
            >
              {{ product.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>

          <!-- Product Info -->
          <div class="space-y-3 mb-4">
            <div>
              <label class="block text-xs font-medium text-gray-400 mb-1">Serial Number</label>
              <p class="text-sm text-white font-mono">{{ product.serial_number }}</p>
            </div>
            
            <div v-if="product.description">
              <label class="block text-xs font-medium text-gray-400 mb-1">Description</label>
              <p class="text-sm text-gray-300">{{ product.description }}</p>
            </div>

            <div>
              <label class="block text-xs font-medium text-gray-400 mb-1">Created</label>
              <p class="text-sm text-gray-300">{{ formatDate(product.created_at) }}</p>
            </div>

            <div v-if="product.manufacturer">
              <label class="block text-xs font-medium text-gray-400 mb-1">Manufacturer</label>
              <p class="text-sm text-gray-300">{{ product.manufacturer }}</p>
            </div>
          </div>

          <!-- QR Code Preview -->
          <div v-if="product.qr_code_url" class="mb-4 p-3 bg-white/5 rounded-lg">
            <img 
              :src="product.qr_code_url" 
              :alt="`QR Code for ${product.name}`"
              class="w-16 h-16 mx-auto"
            >
            <p class="text-xs text-gray-400 text-center mt-2">QR Code</p>
          </div>

          <!-- Actions -->
          <div class="flex gap-2">
            <button
              @click="viewProduct(product)"
              class="flex-1 px-3 py-2 glass-button border-emerald-500/30 hover:border-emerald-400/50 text-emerald-400 text-sm transition-colors"
            >
              View Details
            </button>
            <button
              v-if="product.qr_code_url"
              @click="downloadQR(product)"
              class="px-3 py-2 glass-button border-blue-500/30 hover:border-blue-400/50 text-blue-400 text-sm transition-colors"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Product Detail Modal -->
    <div v-if="selectedProduct" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="glass-card max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold text-white">{{ selectedProduct.name }}</h2>
            <button
              @click="selectedProduct = null"
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
                <label class="block text-sm font-medium text-gray-400 mb-1">Serial Number</label>
                <p class="text-white font-mono">{{ selectedProduct.serial_number }}</p>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-400 mb-1">Status</label>
                <span
                  :class="{
                    'bg-green-100 text-green-800': selectedProduct.is_active,
                    'bg-red-100 text-red-800': !selectedProduct.is_active
                  }"
                  class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                >
                  {{ selectedProduct.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>

              <div v-if="selectedProduct.description">
                <label class="block text-sm font-medium text-gray-400 mb-1">Description</label>
                <p class="text-gray-300">{{ selectedProduct.description }}</p>
              </div>

              <div v-if="selectedProduct.manufacturer">
                <label class="block text-sm font-medium text-gray-400 mb-1">Manufacturer</label>
                <p class="text-gray-300">{{ selectedProduct.manufacturer }}</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-400 mb-1">Created</label>
                <p class="text-gray-300">{{ formatDate(selectedProduct.created_at) }}</p>
              </div>
            </div>

            <div v-if="selectedProduct.qr_code_url" class="flex flex-col items-center">
              <img 
                :src="selectedProduct.qr_code_url" 
                :alt="`QR Code for ${selectedProduct.name}`"
                class="w-48 h-48 border border-white/20 rounded-lg"
              >
              <button
                @click="downloadQR(selectedProduct)"
                class="mt-4 px-4 py-2 glass-button border-blue-500/30 hover:border-blue-400/50 text-blue-400 transition-colors"
              >
                Download QR Code
              </button>
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
const selectedProduct = ref(null)
const isLoading = ref(false)

const products = computed(() => customerStore.products || [])

const filteredProducts = computed(() => {
  let filtered = products.value

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(product =>
      product.name.toLowerCase().includes(query) ||
      product.serial_number.toLowerCase().includes(query)
    )
  }

  // Status filter
  if (statusFilter.value) {
    if (statusFilter.value === 'active') {
      filtered = filtered.filter(product => product.is_active)
    } else if (statusFilter.value === 'inactive') {
      filtered = filtered.filter(product => !product.is_active)
    }
  }

  return filtered
})

const activeProducts = computed(() => 
  products.value.filter(product => product.is_active).length
)

const verifiedProducts = computed(() => 
  products.value.filter(product => product.is_verified).length
)

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const viewProduct = (product) => {
  selectedProduct.value = product
}

const downloadQR = (product) => {
  if (product.qr_code_url) {
    const link = document.createElement('a')
    link.href = product.qr_code_url
    link.download = `${product.name}-qr-code.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

const logout = () => {
  customerStore.logout()
  router.push('/customer/login')
}

onMounted(async () => {
  try {
    isLoading.value = true
    await customerStore.fetchProducts()
  } catch (error) {
    console.error('Failed to load products:', error)
  } finally {
    isLoading.value = false
  }
})
</script>
