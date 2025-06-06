<template>
  <div class="min-h-screen bg-gradient-to-br from-dark via-gray-900 to-dark text-white">
    <!-- Header -->
    <header class="glass-nav border-b border-cyan-500/20">
      <div class="container mx-auto px-6 py-4">
        <div class="flex items-center justify-between">
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
              Product Management
            </h1>
          </div>          <div class="flex items-center space-x-3">
            <button
              @click="generateBatchLabels"
              class="px-4 py-2 glass-button border-purple-500/30 hover:border-purple-400/50 text-purple-400"
              title="Generate Batch Labels"
            >
              <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Batch Labels
            </button>
            <button
              @click="showAddModal = true"
              class="px-4 py-2 glass-button border-cyan-500/30 hover:border-cyan-400/50 text-cyan-400"
            >
              <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              Add Product
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <div class="container mx-auto px-6 py-8">
      <!-- Filters and Search -->
      <div class="glass-card p-6 mb-8">
        <div class="flex flex-col md:flex-row gap-4">
          <div class="flex-1">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search products..."
              class="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-cyan-400 transition-colors"
            >
          </div>
          <select
            v-model="statusFilter"
            class="px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-cyan-400 transition-colors"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
          <select
            v-model="categoryFilter"
            class="px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-cyan-400 transition-colors"
          >
            <option value="">All Categories</option>
            <option value="electronics">Electronics</option>
            <option value="pharmaceutical">Pharmaceutical</option>
            <option value="luxury">Luxury Goods</option>
            <option value="automotive">Automotive</option>
          </select>
        </div>
      </div>

      <!-- Products Table -->
      <div class="glass-card overflow-hidden">
        <div class="p-6 border-b border-white/10">
          <h3 class="text-xl font-semibold text-cyan-400">Products</h3>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full">            <thead class="bg-white/5">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  <input
                    type="checkbox"
                    @change="toggleAllProducts"
                    :checked="selectedProducts.length === filteredProducts.length && filteredProducts.length > 0"
                    class="rounded bg-white/10 border-white/20 text-cyan-400 focus:ring-cyan-400 focus:ring-offset-0"
                  >
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Product</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Serial Number</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Category</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Created</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/10">              <tr
                v-for="product in filteredProducts"
                :key="product.id"
                class="hover:bg-white/5 transition-colors"
              >
                <td class="px-6 py-4 whitespace-nowrap">
                  <input
                    type="checkbox"
                    :value="product"
                    v-model="selectedProducts"
                    class="rounded bg-white/10 border-white/20 text-cyan-400 focus:ring-cyan-400 focus:ring-offset-0"
                  >
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="w-10 h-10 bg-cyan-500/20 rounded-lg flex items-center justify-center mr-3">
                      <svg class="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                      </svg>
                    </div>
                    <div>
                      <p class="text-sm font-medium text-white">{{ product.name }}</p>
                      <p class="text-sm text-gray-400">{{ product.brand }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="text-sm font-mono text-gray-300">{{ product.serial_number }}</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 py-1 text-xs font-medium bg-blue-500/20 text-blue-400 rounded-full">
                    {{ product.category }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="[
                      'px-2 py-1 text-xs font-medium rounded-full',
                      product.status === 'active'
                        ? 'bg-green-500/20 text-green-400'
                        : 'bg-red-500/20 text-red-400'
                    ]"
                  >
                    {{ product.status }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                  {{ formatDate(product.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <div class="flex space-x-2">                    <button
                      @click="editProduct(product)"
                      class="text-cyan-400 hover:text-cyan-300 transition-colors"
                      title="Edit Product"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button
                      @click="viewQRCode(product)"
                      class="text-green-400 hover:text-green-300 transition-colors"
                      title="View QR Code"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
                      </svg>
                    </button>
                    <button
                      @click="generateProductLabel(product)"
                      class="text-purple-400 hover:text-purple-300 transition-colors"
                      title="Generate PDF Label"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </button>
                    <button
                      @click="deleteProduct(product)"
                      class="text-red-400 hover:text-red-300 transition-colors"
                      title="Delete Product"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div class="px-6 py-3 border-t border-white/10 flex items-center justify-between">
          <div class="text-sm text-gray-400">
            Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to {{ Math.min(currentPage * itemsPerPage, totalItems) }} of {{ totalItems }} results
          </div>
          <div class="flex space-x-2">
            <button
              @click="currentPage--"
              :disabled="currentPage === 1"
              class="px-3 py-1 text-sm glass-button border-white/20 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <button
              @click="currentPage++"
              :disabled="currentPage * itemsPerPage >= totalItems"
              class="px-3 py-1 text-sm glass-button border-white/20 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Product Modal -->
    <div
      v-if="showAddModal || showEditModal"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
      @click.self="closeModals"
    >
      <div class="glass-card p-6 w-full max-w-md mx-4">
        <h3 class="text-xl font-semibold mb-6 text-cyan-400">
          {{ showAddModal ? 'Add New Product' : 'Edit Product' }}
        </h3>
        <form @submit.prevent="showAddModal ? addProduct() : updateProduct()">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">Product Name</label>
              <input
                v-model="productForm.name"
                type="text"
                required
                class="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-cyan-400 transition-colors"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">Brand</label>
              <input
                v-model="productForm.brand"
                type="text"
                required
                class="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-cyan-400 transition-colors"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">Serial Number</label>
              <input
                v-model="productForm.serial_number"
                type="text"
                required
                class="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-cyan-400 transition-colors"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">Category</label>
              <select
                v-model="productForm.category"
                required
                class="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-cyan-400 transition-colors"
              >
                <option value="">Select Category</option>
                <option value="electronics">Electronics</option>
                <option value="pharmaceutical">Pharmaceutical</option>
                <option value="luxury">Luxury Goods</option>
                <option value="automotive">Automotive</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">Description</label>
              <textarea
                v-model="productForm.description"
                rows="3"
                class="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-cyan-400 transition-colors"
              ></textarea>
            </div>
          </div>
          <div class="flex justify-end space-x-3 mt-6">
            <button
              type="button"
              @click="closeModals"
              class="px-4 py-2 glass-button border-white/20"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-4 py-2 glass-button border-cyan-500/30 hover:border-cyan-400/50 text-cyan-400"
            >
              {{ showAddModal ? 'Add Product' : 'Update Product' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- QR Code Modal -->
    <div
      v-if="showQRModal"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
      @click.self="showQRModal = false"
    >
      <div class="glass-card p-6 w-full max-w-sm mx-4 text-center">
        <h3 class="text-xl font-semibold mb-6 text-cyan-400">QR Code</h3>
        <div class="bg-white p-4 rounded-lg mb-4">
          <canvas ref="qrCanvas" class="mx-auto"></canvas>
        </div>
        <p class="text-sm text-gray-300 mb-4">{{ selectedProduct?.name }}</p>
        <p class="text-xs text-gray-400 mb-6 font-mono">{{ selectedProduct?.serial_number }}</p>
        <button
          @click="downloadQR"
          class="w-full px-4 py-2 glass-button border-cyan-500/30 hover:border-cyan-400/50 text-cyan-400 mb-3"
        >
          Download QR Code
        </button>
        <button
          @click="showQRModal = false"
          class="w-full px-4 py-2 glass-button border-white/20"
        >
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useAdminStore } from '@/stores/admin'
import QRCode from 'qrcode'

const adminStore = useAdminStore()

// Data
const products = ref([])
const selectedProducts = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const categoryFilter = ref('')
const currentPage = ref(1)
const itemsPerPage = 10

// Modals
const showAddModal = ref(false)
const showEditModal = ref(false)
const showQRModal = ref(false)
const selectedProduct = ref(null)

// Form
const productForm = ref({
  name: '',
  brand: '',
  serial_number: '',
  category: '',
  description: ''
})

// QR Code
const qrCanvas = ref(null)

// Computed
const filteredProducts = computed(() => {
  let filtered = products.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(product =>
      product.name.toLowerCase().includes(query) ||
      product.brand.toLowerCase().includes(query) ||
      product.serial_number.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(product => product.status === statusFilter.value)
  }

  if (categoryFilter.value) {
    filtered = filtered.filter(product => product.category === categoryFilter.value)
  }

  const start = (currentPage.value - 1) * itemsPerPage
  return filtered.slice(start, start + itemsPerPage)
})

const totalItems = computed(() => {
  let filtered = products.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(product =>
      product.name.toLowerCase().includes(query) ||
      product.brand.toLowerCase().includes(query) ||
      product.serial_number.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(product => product.status === statusFilter.value)
  }

  if (categoryFilter.value) {
    filtered = filtered.filter(product => product.category === categoryFilter.value)
  }

  return filtered.length
})

// Methods
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const loadProducts = async () => {
  try {
    products.value = await adminStore.getProducts()
  } catch (error) {
    console.error('Failed to load products:', error)
  }
}

const addProduct = async () => {
  try {
    await adminStore.createProduct(productForm.value)
    await loadProducts()
    closeModals()
    resetForm()
  } catch (error) {
    console.error('Failed to add product:', error)
  }
}

const editProduct = (product) => {
  selectedProduct.value = product
  productForm.value = { ...product }
  showEditModal.value = true
}

const updateProduct = async () => {
  try {
    await adminStore.updateProduct(selectedProduct.value.id, productForm.value)
    await loadProducts()
    closeModals()
    resetForm()
  } catch (error) {
    console.error('Failed to update product:', error)
  }
}

const deleteProduct = async (product) => {
  if (confirm(`Are you sure you want to delete ${product.name}?`)) {
    try {
      await adminStore.deleteProduct(product.id)
      await loadProducts()
    } catch (error) {
      console.error('Failed to delete product:', error)
    }
  }
}

const viewQRCode = async (product) => {
  selectedProduct.value = product
  showQRModal.value = true
  
  await nextTick()
  
  try {
    const verificationUrl = `${window.location.origin}/verify?serial=${product.serial_number}`
    await QRCode.toCanvas(qrCanvas.value, verificationUrl, {
      width: 200,
      margin: 2,
      color: {
        dark: '#000000',
        light: '#FFFFFF'
      }
    })
  } catch (error) {
    console.error('Failed to generate QR code:', error)
  }
}

const downloadQR = () => {
  const link = document.createElement('a')
  link.download = `qr-${selectedProduct.value.serial_number}.png`
  link.href = qrCanvas.value.toDataURL()
  link.click()
}

const generateProductLabel = async (product) => {
  try {
    const blob = await adminStore.generateProductLabel(product.id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `product_label_${product.serial_number}.pdf`
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Failed to generate product label:', error)
    alert('Failed to generate PDF label. Please try again.')
  }
}

const generateBatchLabels = async () => {
  if (selectedProducts.value.length === 0) {
    alert('Please select products to generate batch labels')
    return
  }
  
  try {
    const productIds = selectedProducts.value.map(p => p.id)
    const blob = await adminStore.generateBatchLabels(productIds)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `batch_labels_${new Date().getTime()}.pdf`
    link.click()
    window.URL.revokeObjectURL(url)
    selectedProducts.value = [] // Clear selection after generating
  } catch (error) {
    console.error('Failed to generate batch labels:', error)
    alert('Failed to generate batch labels. Please try again.')
  }
}

const toggleAllProducts = (event) => {
  if (event.target.checked) {
    selectedProducts.value = [...filteredProducts.value]
  } else {
    selectedProducts.value = []
  }
}

const closeModals = () => {
  showAddModal.value = false
  showEditModal.value = false
  showQRModal.value = false
  selectedProduct.value = null
}

const resetForm = () => {
  productForm.value = {
    name: '',
    brand: '',
    serial_number: '',
    category: '',
    description: ''
  }
}

onMounted(() => {
  loadProducts()
})
</script>
