<template>
  <div id="app" class="min-h-screen flex flex-col bg-gradient-to-br from-dark via-gray-900 to-dark">
    <!-- Navigation -->
    <AppNavbar />
    
    <!-- Main content -->
    <main class="flex-1">
      <router-view />
    </main>
    
    <!-- Footer -->
    <AppFooter />
    
    <!-- Global loading overlay -->
    <div v-if="isLoading" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
      <div class="glass-card p-8 text-center">
        <div class="loading-spinner mx-auto mb-4"></div>
        <p class="text-white font-medium">Loading...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AppNavbar from '@/components/AppNavbar.vue'
import AppFooter from '@/components/AppFooter.vue'

const isLoading = ref(false)
const authStore = useAuthStore()

onMounted(async () => {
  // Initialize app
  try {
    isLoading.value = true
    await authStore.initializeAuth()
  } catch (error) {
    console.error('App initialization error:', error)
  } finally {
    isLoading.value = false
  }
})
</script>

<style>
/* App-specific styles */
#app {
  font-family: 'Inter', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Smooth page transitions */
.router-view {
  transition: all 0.3s ease-in-out;
}

/* Custom selection color */
::selection {
  background-color: rgba(0, 229, 255, 0.3);
  color: white;
}

::-moz-selection {
  background-color: rgba(0, 229, 255, 0.3);
  color: white;
}
</style>
