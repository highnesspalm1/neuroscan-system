<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- Header -->
      <div class="text-center">
        <div class="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-indigo-100">
          <svg class="h-6 w-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
        <h2 class="mt-6 text-3xl font-extrabold text-gray-900">
          Customer Portal
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          Sign in to access your product analytics and statistics
        </p>
      </div>

      <!-- Login Form -->
      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="username" class="sr-only">Username</label>
            <input
              id="username"
              v-model="form.username"
              name="username"
              type="text"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="Username"
            />
          </div>
          <div>
            <label for="password" class="sr-only">Password</label>
            <input
              id="password"
              v-model="form.password"
              name="password"
              type="password"
              required              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="Password"
            />
          </div>
        </div>
        
        <!-- Error Message -->
        <div v-if="error" class="rounded-md bg-red-50 p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">
                Login Failed
              </h3>
              <div class="mt-2 text-sm text-red-700">
                <p>{{ error }}</p>
                <p v-if="isTimeoutError" class="mt-2 text-xs">
                  💡 <strong>Tip:</strong> The service might be starting up. 
                  <button @click="wakeUpAPI" class="underline hover:no-underline">
                    Click here to wake up the API
                  </button> and try again.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- API Status -->
        <div v-if="isWakingUp" class="rounded-md bg-blue-50 p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="animate-spin h-5 w-5 text-blue-400" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-blue-800">
                Waking up API service...
              </h3>
              <p class="mt-1 text-sm text-blue-700">
                Please wait while the backend service starts up. This may take 30-60 seconds.
              </p>
            </div>
          </div>        </div>

        <!-- Submit Button -->
        <div>
          <button
            type="submit"
            :disabled="isLoading"
            class="w-full glass-button bg-gradient-primary hover:scale-105 transform transition-all duration-300 neon-glow py-3 font-semibold focus-primary disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:scale-100"
          >
            <span v-if="isLoading" class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>              Signing in...
            </span>
            <span v-else>Sign in</span>
          </button>
        </div>
        
        <!-- Back to Admin -->
        <div class="text-center">
          <router-link
            to="/admin/login"
            class="text-sm text-emerald-400 hover:text-emerald-300 transition-colors duration-200"
          >
            Admin? Sign in here
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCustomerStore } from '@/stores/customer'
import api from '@/api/index'

const router = useRouter()
const customerStore = useCustomerStore()

// Form state
const form = ref({
  username: '',
  password: ''
})

// Wake-up state
const isWakingUp = ref(false)

// Computed properties
const isLoading = computed(() => customerStore.isLoading)
const error = computed(() => customerStore.error)
const isTimeoutError = computed(() => {
  return error.value && (
    error.value.includes('timeout') || 
    error.value.includes('Network Error') ||
    error.value.includes('ERR_NETWORK') ||
    error.value.includes('Failed to fetch')
  )
})

// Methods
const wakeUpAPI = async () => {
  try {
    isWakingUp.value = true
    await api.get('/health')
    // Wait a moment for the service to fully wake up
    await new Promise(resolve => setTimeout(resolve, 2000))
    isWakingUp.value = false
    // Clear any previous error
    customerStore.error = null
  } catch (err) {
    console.log('Wake up request sent, service should be starting...')
    isWakingUp.value = false
  }
}

const handleLogin = async () => {
  try {
    await customerStore.login(form.value)
    router.push('/customer/dashboard')
  } catch (err) {
    // Error is handled by the store
    console.error('Login failed:', err)
  }
}
</script>
