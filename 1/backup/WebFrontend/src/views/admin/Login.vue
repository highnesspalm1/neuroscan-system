<template>
  <div class="min-h-screen pt-20">
    <!-- Navigation -->
    <nav class="navbar-glass fixed w-full top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <router-link to="/" class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-gradient-primary rounded-xl flex items-center justify-center neon-glow">
              <span class="text-white font-bold text-xl">N</span>
            </div>
            <span class="text-xl font-bold text-gradient">NeuroScan</span>
          </router-link>
          
          <router-link to="/" class="text-gray-300 hover:text-primary-400 transition-colors">
            ← Back to Home
          </router-link>
        </div>
      </div>
    </nav>

    <!-- Login Form -->
    <div class="flex items-center justify-center min-h-screen px-4 sm:px-6 lg:px-8">
      <div class="glass-card max-w-md w-full">
        <div class="text-center mb-8">
          <div class="w-20 h-20 bg-gradient-primary rounded-2xl flex items-center justify-center mb-6 mx-auto neon-glow">
            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h2 class="text-3xl font-bold text-white mb-2">Admin Login</h2>
          <p class="text-gray-400">Sign in to access the NeuroScan admin panel</p>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              Username
            </label>
            <input
              v-model="credentials.username"
              type="text"
              required
              class="glass-input w-full focus-primary"
              placeholder="Enter your username"
              :disabled="authStore.isLoading"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">
              Password
            </label>
            <div class="relative">
              <input
                v-model="credentials.password"
                :type="showPassword ? 'text' : 'password'"
                required
                class="glass-input w-full pr-12 focus-primary"
                placeholder="Enter your password"
                :disabled="authStore.isLoading"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-white"
                :disabled="authStore.isLoading"
              >
                <svg v-if="showPassword" class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <svg v-else class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                </svg>
              </button>
            </div>
          </div>

          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <input
                id="remember-me"
                v-model="rememberMe"
                type="checkbox"
                class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-600 bg-gray-700 rounded"
              />
              <label for="remember-me" class="ml-2 block text-sm text-gray-300">
                Remember me
              </label>
            </div>

            <div class="text-sm">
              <a href="#" class="text-primary-400 hover:text-primary-300 transition-colors">
                Forgot password?
              </a>
            </div>
          </div>

          <div v-if="authStore.error" class="glass-effect p-4 rounded-lg border border-red-500/30 bg-red-500/10">
            <div class="flex">
              <svg class="h-5 w-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
              <p class="text-red-400 text-sm">{{ authStore.error }}</p>
            </div>
          </div>

          <button
            type="submit"
            class="w-full glass-button bg-gradient-primary hover:scale-105 transform transition-all duration-300 neon-glow py-3 font-semibold focus-primary"
            :disabled="authStore.isLoading"
          >
            <div v-if="authStore.isLoading" class="flex items-center justify-center">
              <div class="loading-spinner mr-2"></div>
              Signing in...
            </div>
            <div v-else class="flex items-center justify-center">
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
              </svg>
              Sign In
            </div>
          </button>
        </form>

        <!-- Demo Credentials Info -->
        <div class="mt-8 glass-effect p-4 rounded-lg border border-primary-500/30 bg-primary-500/10">
          <h4 class="text-primary-400 font-semibold mb-2">Demo Credentials</h4>
          <div class="text-sm text-gray-300 space-y-1">
            <p><strong>Username:</strong> admin</p>
            <p><strong>Password:</strong> admin123</p>
          </div>
        </div>

        <div class="mt-6 text-center">
          <p class="text-sm text-gray-400">
            Need help? 
            <router-link to="/contact" class="text-primary-400 hover:text-primary-300 transition-colors">
              Contact support
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

export default {
  name: 'AdminLogin',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const authStore = useAuthStore()
    const toast = useToast()

    const credentials = ref({
      username: '',
      password: ''
    })
    const showPassword = ref(false)
    const rememberMe = ref(false)

    const handleLogin = async () => {
      try {
        await authStore.login(credentials.value)
        
        toast.success('Login successful!')
        
        // Redirect to intended page or dashboard
        const redirectTo = route.query.redirect || '/admin/dashboard'
        router.push(redirectTo)
      } catch (error) {
        console.error('Login error:', error)
        // Error is already handled by the store
      }
    }

    return {
      authStore,
      credentials,
      showPassword,
      rememberMe,
      handleLogin
    }
  }
}
</script>
