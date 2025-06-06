<template>
  <div class="min-h-screen bg-gradient-to-br from-dark via-gray-900 to-dark text-white">
    <!-- Header -->
    <header class="glass-nav border-b border-cyan-500/20">
      <div class="container mx-auto px-6 py-4 flex justify-between items-center">
        <div class="flex items-center space-x-4">
          <h1 class="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
            NeuroScan Admin
          </h1>
          <span class="text-sm text-gray-400">Dashboard</span>
        </div>
        <div class="flex items-center space-x-4">
          <span class="text-sm text-gray-300">{{ authStore.user?.username }}</span>
          <button
            @click="logout"
            class="px-4 py-2 glass-button text-red-400 border-red-500/30 hover:border-red-400/50"
          >
            Logout
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <div class="container mx-auto px-6 py-8">
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="glass-card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">Total Products</p>
              <p class="text-3xl font-bold text-cyan-400">{{ stats.totalProducts }}</p>
            </div>
            <div class="w-12 h-12 bg-cyan-500/20 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
          </div>
        </div>

        <div class="glass-card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">Verified Today</p>
              <p class="text-3xl font-bold text-green-400">{{ stats.verifiedToday }}</p>
            </div>
            <div class="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="glass-card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">Total Verifications</p>
              <p class="text-3xl font-bold text-blue-400">{{ stats.totalVerifications }}</p>
            </div>
            <div class="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="glass-card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">Active Certificates</p>
              <p class="text-3xl font-bold text-yellow-400">{{ stats.activeCertificates }}</p>
            </div>
            <div class="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- Quick Actions Panel -->
        <div class="glass-card p-6">
          <h3 class="text-xl font-semibold mb-6 text-cyan-400">Quick Actions</h3>
          <div class="space-y-4">
            <router-link
              to="/admin/products/add"
              class="flex items-center p-4 glass-button border-cyan-500/30 hover:border-cyan-400/50 transition-colors group"
            >
              <div class="w-10 h-10 bg-cyan-500/20 rounded-lg flex items-center justify-center mr-4">
                <svg class="w-5 h-5 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </div>
              <div>
                <p class="font-medium text-white group-hover:text-cyan-400 transition-colors">Add New Product</p>
                <p class="text-sm text-gray-400">Register a new product for authentication</p>
              </div>
            </router-link>

            <router-link
              to="/admin/certificates"
              class="flex items-center p-4 glass-button border-green-500/30 hover:border-green-400/50 transition-colors group"
            >
              <div class="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center mr-4">
                <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <p class="font-medium text-white group-hover:text-green-400 transition-colors">Manage Certificates</p>
                <p class="text-sm text-gray-400">View and manage authentication certificates</p>
              </div>
            </router-link>

            <router-link
              to="/admin/analytics"
              class="flex items-center p-4 glass-button border-blue-500/30 hover:border-blue-400/50 transition-colors group"
            >
              <div class="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center mr-4">
                <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div>
                <p class="font-medium text-white group-hover:text-blue-400 transition-colors">View Analytics</p>
                <p class="text-sm text-gray-400">Check verification statistics and trends</p>
              </div>
            </router-link>
          </div>
        </div>

        <!-- Recent Verifications -->
        <div class="glass-card p-6">
          <h3 class="text-xl font-semibold mb-6 text-cyan-400">Recent Verifications</h3>
          <div class="space-y-4">
            <div
              v-for="verification in recentVerifications"
              :key="verification.id"
              class="flex items-center justify-between p-3 bg-white/5 rounded-lg border border-white/10"
            >
              <div class="flex items-center space-x-3">
                <div class="w-8 h-8 bg-green-500/20 rounded-full flex items-center justify-center">
                  <svg class="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <p class="text-sm font-medium text-white">{{ verification.product_name }}</p>
                  <p class="text-xs text-gray-400">{{ verification.serial_number }}</p>
                </div>
              </div>
              <span class="text-xs text-gray-400">{{ formatDate(verification.verified_at) }}</span>
            </div>
          </div>
          <router-link
            to="/admin/verifications"
            class="block mt-4 text-center text-cyan-400 hover:text-cyan-300 text-sm transition-colors"
          >
            View All Verifications →
          </router-link>
        </div>
      </div>

      <!-- System Status -->
      <div class="glass-card p-6">
        <h3 class="text-xl font-semibold mb-6 text-cyan-400">System Status</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="flex items-center space-x-3">
            <div class="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            <span class="text-gray-300">API Server: Online</span>
          </div>
          <div class="flex items-center space-x-3">
            <div class="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            <span class="text-gray-300">Database: Connected</span>
          </div>
          <div class="flex items-center space-x-3">
            <div class="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            <span class="text-gray-300">Certificate Service: Active</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAdminStore } from '@/stores/admin'

const router = useRouter()
const authStore = useAuthStore()
const adminStore = useAdminStore()

const stats = ref({
  totalProducts: 0,
  verifiedToday: 0,
  totalVerifications: 0,
  activeCertificates: 0
})

const recentVerifications = ref([])

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const logout = async () => {
  await authStore.logout()
  router.push('/admin/login')
}

onMounted(async () => {
  try {
    // Load dashboard data
    const [statsData, verificationsData] = await Promise.all([
      adminStore.getDashboardStats(),
      adminStore.getRecentVerifications()
    ])
    
    stats.value = statsData
    recentVerifications.value = verificationsData.slice(0, 5) // Show last 5
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  }
})
</script>
