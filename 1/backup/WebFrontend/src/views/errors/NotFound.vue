<template>
  <div class="min-h-screen bg-gradient-to-br from-dark via-gray-900 to-dark flex items-center justify-center">
    <div class="text-center px-6">
      <!-- 404 Animation -->
      <div class="relative mb-8">
        <div class="text-9xl font-bold text-cyan-400/20 select-none">404</div>
        <div class="absolute inset-0 flex items-center justify-center">
          <div class="w-32 h-32 border-4 border-cyan-500/30 rounded-full animate-pulse"></div>
          <div class="absolute w-24 h-24 border-4 border-cyan-400/50 rounded-full animate-spin"></div>
          <div class="absolute w-16 h-16 bg-cyan-500/20 rounded-full animate-bounce"></div>
        </div>
      </div>

      <!-- Error Message -->
      <div class="glass-card p-8 max-w-md mx-auto">
        <h1 class="text-3xl font-bold text-white mb-4">Page Not Found</h1>
        <p class="text-gray-400 mb-6">
          The page you're looking for doesn't exist or has been moved to a different location.
        </p>

        <!-- Navigation Options -->
        <div class="space-y-4">
          <router-link
            to="/"
            class="block w-full px-6 py-3 glass-button border-cyan-500/30 hover:border-cyan-400/50 text-cyan-400 transition-colors"
          >
            <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            Back to Home
          </router-link>

          <router-link
            to="/verify"
            class="block w-full px-6 py-3 glass-button border-green-500/30 hover:border-green-400/50 text-green-400 transition-colors"
          >
            <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Verify Product
          </router-link>

          <button
            @click="goBack"
            class="block w-full px-6 py-3 glass-button border-white/20 hover:border-white/30 text-gray-300 transition-colors"
          >
            <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
            Go Back
          </button>
        </div>

        <!-- Help Text -->
        <div class="mt-8 pt-6 border-t border-white/10">
          <p class="text-sm text-gray-500">
            If you believe this is an error, please 
            <router-link to="/contact" class="text-cyan-400 hover:text-cyan-300 transition-colors">
              contact our support team
            </router-link>
          </p>
        </div>
      </div>

      <!-- Floating Elements -->
      <div class="absolute top-20 left-10 w-4 h-4 bg-cyan-400/30 rounded-full animate-ping"></div>
      <div class="absolute top-40 right-20 w-6 h-6 bg-green-400/30 rounded-full animate-pulse"></div>
      <div class="absolute bottom-20 left-20 w-3 h-3 bg-blue-400/30 rounded-full animate-bounce"></div>
      <div class="absolute bottom-40 right-10 w-5 h-5 bg-yellow-400/30 rounded-full animate-ping"></div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/')
  }
}
</script>

<style scoped>
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

.animate-float {
  animation: float 3s ease-in-out infinite;
}
</style>
