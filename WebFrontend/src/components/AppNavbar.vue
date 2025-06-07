<template>
  <nav class="glass-nav border-b border-cyan-500/20 sticky top-0 z-50">
    <div class="container mx-auto px-6">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <router-link 
          to="/" 
          class="flex items-center space-x-3 hover:opacity-80 transition-opacity"
        >
          <div class="w-8 h-8 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <span class="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
            NeuroScan
          </span>
        </router-link>

        <!-- Desktop Navigation -->
        <div class="hidden md:flex items-center space-x-8">
          <router-link
            to="/"
            class="nav-link"
            :class="{ 'text-cyan-400': $route.name === 'Home' }"
          >
            Home
          </router-link>
          <router-link
            to="/verify"
            class="nav-link"
            :class="{ 'text-cyan-400': $route.name === 'Verify' || $route.name === 'VerifyDirect' }"
          >
            Verify
          </router-link>
          <router-link
            to="/about"
            class="nav-link"
            :class="{ 'text-cyan-400': $route.name === 'About' }"
          >
            About
          </router-link>
          <router-link
            to="/contact"
            class="nav-link"
            :class="{ 'text-cyan-400': $route.name === 'Contact' }"
          >
            Contact
          </router-link>
            <!-- Admin Link -->
          <router-link
            v-if="!authStore.isAuthenticated"
            to="/admin/login"
            class="px-4 py-2 glass-button border-cyan-500/30 hover:border-cyan-400/50 text-cyan-400 transition-colors"
          >
            Admin
          </router-link>
          <router-link
            v-else
            to="/admin/dashboard"
            class="px-4 py-2 glass-button border-cyan-500/30 hover:border-cyan-400/50 text-cyan-400 transition-colors"
          >
            Dashboard
          </router-link>
          
          <!-- Customer Link -->
          <router-link
            v-if="!customerStore.isAuthenticated"
            to="/customer/login"
            class="px-4 py-2 glass-button border-emerald-500/30 hover:border-emerald-400/50 text-emerald-400 transition-colors"
          >
            Customer Portal
          </router-link>
          <router-link
            v-else
            to="/customer/dashboard"
            class="px-4 py-2 glass-button border-emerald-500/30 hover:border-emerald-400/50 text-emerald-400 transition-colors"
          >
            My Portal
          </router-link>
        </div>

        <!-- Mobile Menu Button -->
        <button
          @click="mobileMenuOpen = !mobileMenuOpen"
          class="md:hidden p-2 text-gray-400 hover:text-white transition-colors"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path 
              v-if="!mobileMenuOpen"
              stroke-linecap="round" 
              stroke-linejoin="round" 
              stroke-width="2" 
              d="M4 6h16M4 12h16M4 18h16" 
            />
            <path 
              v-else
              stroke-linecap="round" 
              stroke-linejoin="round" 
              stroke-width="2" 
              d="M6 18L18 6M6 6l12 12" 
            />
          </svg>
        </button>
      </div>

      <!-- Mobile Menu -->
      <div 
        v-if="mobileMenuOpen"
        class="md:hidden py-4 border-t border-white/10"
      >
        <div class="flex flex-col space-y-2">
          <router-link
            to="/"
            @click="mobileMenuOpen = false"
            class="px-4 py-2 nav-link"
            :class="{ 'text-cyan-400': $route.name === 'Home' }"
          >
            Home
          </router-link>
          <router-link
            to="/verify"
            @click="mobileMenuOpen = false"
            class="px-4 py-2 nav-link"
            :class="{ 'text-cyan-400': $route.name === 'Verify' || $route.name === 'VerifyDirect' }"
          >
            Verify
          </router-link>
          <router-link
            to="/about"
            @click="mobileMenuOpen = false"
            class="px-4 py-2 nav-link"
            :class="{ 'text-cyan-400': $route.name === 'About' }"
          >
            About
          </router-link>
          <router-link
            to="/contact"
            @click="mobileMenuOpen = false"
            class="px-4 py-2 nav-link"
            :class="{ 'text-cyan-400': $route.name === 'Contact' }"
          >
            Contact
          </router-link>          <router-link
            v-if="!authStore.isAuthenticated"
            to="/admin/login"
            @click="mobileMenuOpen = false"
            class="mx-4 mt-2 px-4 py-2 glass-button border-cyan-500/30 hover:border-cyan-400/50 text-cyan-400 transition-colors text-center"
          >
            Admin
          </router-link>
          <router-link
            v-else
            to="/admin/dashboard"
            @click="mobileMenuOpen = false"
            class="mx-4 mt-2 px-4 py-2 glass-button border-cyan-500/30 hover:border-cyan-400/50 text-cyan-400 transition-colors text-center"
          >
            Dashboard
          </router-link>
          <router-link
            v-if="!customerStore.isAuthenticated"
            to="/customer/login"
            @click="mobileMenuOpen = false"
            class="mx-4 mt-2 px-4 py-2 glass-button border-emerald-500/30 hover:border-emerald-400/50 text-emerald-400 transition-colors text-center"
          >
            Customer Portal
          </router-link>
          <router-link
            v-else
            to="/customer/dashboard"
            @click="mobileMenuOpen = false"
            class="mx-4 mt-2 px-4 py-2 glass-button border-emerald-500/30 hover:border-emerald-400/50 text-emerald-400 transition-colors text-center"
          >
            My Portal
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCustomerStore } from '@/stores/customer'

const authStore = useAuthStore()
const customerStore = useCustomerStore()
const mobileMenuOpen = ref(false)
</script>

<style scoped>
.nav-link {
  @apply text-gray-300 hover:text-white transition-colors relative;
}

.nav-link.router-link-active {
  @apply text-cyan-400;
}

.nav-link::after {
  content: '';
  position: absolute;
  width: 0;
  height: 2px;
  bottom: -4px;
  left: 50%;
  background: linear-gradient(90deg, #00E5FF, #2196F3);
  transition: all 0.3s ease;
  transform: translateX(-50%);
}

.nav-link:hover::after,
.nav-link.router-link-active::after {
  width: 100%;
}
</style>
