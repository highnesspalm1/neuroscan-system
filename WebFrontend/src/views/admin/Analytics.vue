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
            Analytics & Reports
          </h1>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <div class="container mx-auto px-6 py-8">
      <!-- Time Range Selector -->
      <div class="glass-card p-6 mb-8">
        <div class="flex flex-col md:flex-row gap-4 items-center justify-between">
          <h3 class="text-lg font-semibold text-cyan-400">Analytics Dashboard</h3>
          <div class="flex gap-4">
            <select
              v-model="selectedRange"
              @change="loadAnalytics"
              class="px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-cyan-400 transition-colors"
            >
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
              <option value="1y">Last Year</option>
            </select>
            <button
              @click="exportReport"
              class="px-4 py-2 glass-button border-cyan-500/30 hover:border-cyan-400/50 text-cyan-400"
            >
              <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Export Report
            </button>
          </div>
        </div>
      </div>

      <!-- Key Metrics -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="glass-card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">Total Verifications</p>
              <p class="text-3xl font-bold text-cyan-400">{{ analytics.totalVerifications }}</p>
              <p class="text-sm" :class="getChangeClass(analytics.verificationChange)">
                {{ analytics.verificationChange > 0 ? '+' : '' }}{{ analytics.verificationChange }}% from last period
              </p>
            </div>
            <div class="w-12 h-12 bg-cyan-500/20 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="glass-card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">Unique Products</p>
              <p class="text-3xl font-bold text-green-400">{{ analytics.uniqueProducts }}</p>
              <p class="text-sm" :class="getChangeClass(analytics.productChange)">
                {{ analytics.productChange > 0 ? '+' : '' }}{{ analytics.productChange }}% from last period
              </p>
            </div>
            <div class="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
          </div>
        </div>

        <div class="glass-card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">Success Rate</p>
              <p class="text-3xl font-bold text-blue-400">{{ analytics.successRate }}%</p>
              <p class="text-sm" :class="getChangeClass(analytics.successRateChange)">
                {{ analytics.successRateChange > 0 ? '+' : '' }}{{ analytics.successRateChange }}% from last period
              </p>
            </div>
            <div class="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="glass-card p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">Avg. Daily Verifications</p>
              <p class="text-3xl font-bold text-yellow-400">{{ analytics.avgDaily }}</p>
              <p class="text-sm" :class="getChangeClass(analytics.avgDailyChange)">
                {{ analytics.avgDailyChange > 0 ? '+' : '' }}{{ analytics.avgDailyChange }}% from last period
              </p>
            </div>
            <div class="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <!-- Verification Trends -->
        <div class="glass-card p-6">
          <h3 class="text-xl font-semibold mb-6 text-cyan-400">Verification Trends</h3>
          <div class="h-64 flex items-center justify-center">
            <canvas ref="trendsChart" class="max-w-full max-h-full"></canvas>
          </div>
        </div>

        <!-- Category Distribution -->
        <div class="glass-card p-6">
          <h3 class="text-xl font-semibold mb-6 text-cyan-400">Category Distribution</h3>
          <div class="h-64 flex items-center justify-center">
            <canvas ref="categoryChart" class="max-w-full max-h-full"></canvas>
          </div>
        </div>
      </div>

      <!-- Geographic Distribution -->
      <div class="glass-card p-6 mb-8">
        <h3 class="text-xl font-semibold mb-6 text-cyan-400">Geographic Distribution</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="location in analytics.geoDistribution"
            :key="location.country"
            class="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10"
          >
            <div class="flex items-center space-x-3">
              <div class="w-8 h-8 bg-cyan-500/20 rounded-full flex items-center justify-center">
                <span class="text-cyan-400 text-sm font-semibold">{{ location.country.substring(0, 2).toUpperCase() }}</span>
              </div>
              <div>
                <p class="text-white font-medium">{{ location.country }}</p>
                <p class="text-gray-400 text-sm">{{ location.verifications }} verifications</p>
              </div>
            </div>
            <div class="text-right">
              <p class="text-cyan-400 font-semibold">{{ location.percentage }}%</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Top Products -->
      <div class="glass-card p-6 mb-8">
        <h3 class="text-xl font-semibold mb-6 text-cyan-400">Most Verified Products</h3>
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-white/5">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Rank</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Product</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Brand</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Category</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Verifications</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Success Rate</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-white/10">
              <tr
                v-for="(product, index) in analytics.topProducts"
                :key="product.id"
                class="hover:bg-white/5 transition-colors"
              >
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <span
                      :class="[
                        'w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold',
                        index === 0 ? 'bg-yellow-500/20 text-yellow-400' :
                        index === 1 ? 'bg-gray-400/20 text-gray-400' :
                        index === 2 ? 'bg-amber-600/20 text-amber-600' :
                        'bg-cyan-500/20 text-cyan-400'
                      ]"
                    >
                      {{ index + 1 }}
                    </span>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <p class="text-sm font-medium text-white">{{ product.name }}</p>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                  {{ product.brand }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 py-1 text-xs font-medium bg-blue-500/20 text-blue-400 rounded-full">
                    {{ product.category }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-cyan-400 font-semibold">
                  {{ product.verifications }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <span
                    :class="[
                      'font-semibold',
                      product.successRate >= 95 ? 'text-green-400' :
                      product.successRate >= 80 ? 'text-yellow-400' :
                      'text-red-400'
                    ]"
                  >
                    {{ product.successRate }}%
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="glass-card p-6">
        <h3 class="text-xl font-semibold mb-6 text-cyan-400">Recent Verification Activity</h3>
        <div class="space-y-4">
          <div
            v-for="activity in analytics.recentActivity"
            :key="activity.id"
            class="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/10"
          >
            <div class="flex items-center space-x-4">
              <div
                :class="[
                  'w-10 h-10 rounded-lg flex items-center justify-center',
                  activity.status === 'success' ? 'bg-green-500/20' : 'bg-red-500/20'
                ]"
              >
                <svg
                  :class="[
                    'w-5 h-5',
                    activity.status === 'success' ? 'text-green-400' : 'text-red-400'
                  ]"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    v-if="activity.status === 'success'"
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
              </div>
              <div>
                <p class="text-white font-medium">{{ activity.product_name }}</p>
                <p class="text-gray-400 text-sm">{{ activity.serial_number }} • {{ activity.location }}</p>
              </div>
            </div>
            <div class="text-right">
              <p class="text-sm text-gray-300">{{ formatDate(activity.timestamp) }}</p>
              <p
                :class="[
                  'text-xs font-medium',
                  activity.status === 'success' ? 'text-green-400' : 'text-red-400'
                ]"
              >
                {{ activity.status === 'success' ? 'Verified' : 'Failed' }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useAdminStore } from '@/stores/admin'

const adminStore = useAdminStore()

// Data
const selectedRange = ref('30d')
const analytics = ref({
  totalVerifications: 0,
  uniqueProducts: 0,
  successRate: 0,
  avgDaily: 0,
  verificationChange: 0,
  productChange: 0,
  successRateChange: 0,
  avgDailyChange: 0,
  geoDistribution: [],
  topProducts: [],
  recentActivity: [],
  trendsData: [],
  categoryData: []
})

// Chart refs
const trendsChart = ref(null)
const categoryChart = ref(null)

// Methods
const getChangeClass = (change) => {
  if (change > 0) return 'text-green-400'
  if (change < 0) return 'text-red-400'
  return 'text-gray-400'
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loadAnalytics = async () => {
  try {
    const data = await adminStore.getAnalytics(selectedRange.value)
    analytics.value = data
    
    await nextTick()
    renderCharts()
  } catch (error) {
    console.error('Failed to load analytics:', error)
  }
}

const renderCharts = () => {
  // Render trends chart (simplified version)
  if (trendsChart.value) {
    const ctx = trendsChart.value.getContext('2d')
    const gradient = ctx.createLinearGradient(0, 0, 0, 200)
    gradient.addColorStop(0, 'rgba(0, 229, 255, 0.3)')
    gradient.addColorStop(1, 'rgba(0, 229, 255, 0)')
    
    // Simple line chart rendering
    ctx.clearRect(0, 0, trendsChart.value.width, trendsChart.value.height)
    ctx.strokeStyle = '#00E5FF'
    ctx.lineWidth = 2
    ctx.beginPath()
    
    const data = analytics.value.trendsData || []
    if (data.length > 0) {
      const maxValue = Math.max(...data.map(d => d.value))
      const stepX = trendsChart.value.width / (data.length - 1)
      const stepY = trendsChart.value.height / maxValue
      
      data.forEach((point, index) => {
        const x = index * stepX
        const y = trendsChart.value.height - (point.value * stepY)
        
        if (index === 0) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
      })
      
      ctx.stroke()
    }
  }

  // Render category chart (simplified pie chart)
  if (categoryChart.value) {
    const ctx = categoryChart.value.getContext('2d')
    const centerX = categoryChart.value.width / 2
    const centerY = categoryChart.value.height / 2
    const radius = Math.min(centerX, centerY) - 20
    
    ctx.clearRect(0, 0, categoryChart.value.width, categoryChart.value.height)
    
    const data = analytics.value.categoryData || []
    const total = data.reduce((sum, item) => sum + item.value, 0)
    
    let currentAngle = -Math.PI / 2
    const colors = ['#00E5FF', '#39FF14', '#FF3366', '#FFB800', '#9B59B6']
    
    data.forEach((item, index) => {
      const sliceAngle = (item.value / total) * 2 * Math.PI
      
      ctx.beginPath()
      ctx.moveTo(centerX, centerY)
      ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle)
      ctx.closePath()
      
      ctx.fillStyle = colors[index % colors.length]
      ctx.fill()
      
      currentAngle += sliceAngle
    })
  }
}

const exportReport = async () => {
  try {
    await adminStore.exportAnalyticsReport(selectedRange.value)
  } catch (error) {
    console.error('Failed to export report:', error)
  }
}

onMounted(() => {
  loadAnalytics()
})
</script>
