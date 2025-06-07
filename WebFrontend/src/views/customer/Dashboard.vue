<template>
  <div class="min-h-screen bg-gradient-to-br from-dark via-gray-900 to-dark text-white">
    <!-- Header -->
    <header class="glass-nav border-b border-emerald-500/20">
      <div class="container mx-auto px-6 py-4 flex justify-between items-center">
        <div class="flex items-center space-x-4">
          <h1 class="text-2xl font-bold bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">
            NeuroScan Customer Portal
          </h1>
          <span class="text-sm text-gray-400">Dashboard</span>
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
    </header>

    <!-- Main Content -->
    <div class="container mx-auto px-6 py-8">
      <!-- Welcome Message -->
      <div class="mb-8">
        <h2 class="text-3xl font-bold text-white mb-2">
          Welcome back, {{ customerStore.customerName }}!
        </h2>
        <p class="text-gray-400">
          Track your products, certificates, and verification history
        </p>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="glass-card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">My Products</p>
              <p class="text-3xl font-bold text-emerald-400">{{ stats.totalProducts || 0 }}</p>
            </div>
            <div class="w-12 h-12 bg-emerald-500/20 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
          </div>
        </div>

        <div class="glass-card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">Active Certificates</p>
              <p class="text-3xl font-bold text-teal-400">{{ stats.activeCertificates || 0 }}</p>
            </div>
            <div class="w-12 h-12 bg-teal-500/20 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="glass-card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">Total Scans</p>
              <p class="text-3xl font-bold text-blue-400">{{ stats.totalScans || 0 }}</p>
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
              <p class="text-gray-400 text-sm">Recent Scans</p>
              <p class="text-3xl font-bold text-purple-400">{{ stats.recentScans || 0 }}</p>
            </div>
            <div class="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- Navigation Panel -->
        <div class="glass-card p-6">
          <h3 class="text-xl font-semibold mb-6 text-emerald-400">Quick Access</h3>
          <div class="space-y-4">
            <router-link
              to="/customer/products"
              class="flex items-center p-4 glass-button border-emerald-500/30 hover:border-emerald-400/50 transition-colors group"
            >
              <div class="w-10 h-10 bg-emerald-500/20 rounded-lg flex items-center justify-center mr-4">
                <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
              <div>
                <p class="font-medium text-white group-hover:text-emerald-400 transition-colors">My Products</p>
                <p class="text-sm text-gray-400">View all your registered products</p>
              </div>
            </router-link>

            <router-link
              to="/customer/certificates"
              class="flex items-center p-4 glass-button border-teal-500/30 hover:border-teal-400/50 transition-colors group"
            >
              <div class="w-10 h-10 bg-teal-500/20 rounded-lg flex items-center justify-center mr-4">
                <svg class="w-5 h-5 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <p class="font-medium text-white group-hover:text-teal-400 transition-colors">Certificates</p>
                <p class="text-sm text-gray-400">Manage authentication certificates</p>
              </div>
            </router-link>

            <router-link
              to="/customer/scan-logs"
              class="flex items-center p-4 glass-button border-blue-500/30 hover:border-blue-400/50 transition-colors group"
            >
              <div class="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center mr-4">
                <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div>
                <p class="font-medium text-white group-hover:text-blue-400 transition-colors">Scan History</p>
                <p class="text-sm text-gray-400">View verification history and analytics</p>
              </div>
            </router-link>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="glass-card p-6">
          <h3 class="text-xl font-semibold mb-6 text-emerald-400">Recent Activity</h3>
          <div class="space-y-4">
            <div
              v-for="activity in recentActivity"
              :key="activity.id"
              class="flex items-center justify-between p-3 bg-white/5 rounded-lg border border-white/10"
            >
              <div class="flex items-center space-x-3">
                <div class="w-8 h-8 bg-green-500/20 rounded-full flex items-center justify-center">
                  <svg class="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <p class="text-sm font-medium text-white">{{ activity.description }}</p>
                  <p class="text-xs text-gray-400">{{ activity.product_name }}</p>
                </div>
              </div>
              <span class="text-xs text-gray-400">{{ formatDate(activity.timestamp) }}</span>
            </div>
            
            <div v-if="!recentActivity.length" class="text-center py-8">
              <p class="text-gray-400">No recent activity</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Account Information -->
      <div class="glass-card p-6">
        <h3 class="text-xl font-semibold mb-6 text-emerald-400">Account Information</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-400 mb-1">Customer Name</label>
            <p class="text-white">{{ customerStore.customer?.name || 'N/A' }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-400 mb-1">Username</label>
            <p class="text-white">{{ customerStore.customer?.username || 'N/A' }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-400 mb-1">Email</label>
            <p class="text-white">{{ customerStore.customer?.email || 'N/A' }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-400 mb-1">Account Status</label>
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              Active
            </span>
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

const stats = computed(() => customerStore.dashboardStats || {})
const recentActivity = ref([])

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const logout = async () => {
  customerStore.logout()
  router.push('/customer/login')
}

onMounted(async () => {
  try {
    // Load dashboard data
    await customerStore.fetchDashboard()
    
    // Load recent scan logs for activity
    const scanLogs = await customerStore.fetchScanLogs(0, 5)
    recentActivity.value = scanLogs.map(log => ({
      id: log.id,
      description: 'Product verification',
      product_name: log.product_name || 'Unknown Product',
      timestamp: log.scanned_at
    }))
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  }
})
</script>
