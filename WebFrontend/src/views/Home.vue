<template>
  <div class="min-h-screen">
    <!-- Navigation -->
    <nav class="navbar-glass fixed w-full top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo -->
          <div class="flex items-center">
            <router-link to="/" class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-gradient-primary rounded-xl flex items-center justify-center neon-glow">
                <span class="text-white font-bold text-xl">N</span>
              </div>
              <span class="text-xl font-bold text-gradient">NeuroScan</span>
            </router-link>
          </div>

          <!-- Navigation Links -->
          <div class="hidden md:flex items-center space-x-8">
            <router-link to="/" class="text-gray-300 hover:text-primary-400 transition-colors duration-200">
              Home
            </router-link>
            <router-link to="/verify" class="text-gray-300 hover:text-primary-400 transition-colors duration-200">
              Verify Product
            </router-link>
            <router-link to="/about" class="text-gray-300 hover:text-primary-400 transition-colors duration-200">
              About
            </router-link>
            <router-link to="/contact" class="text-gray-300 hover:text-primary-400 transition-colors duration-200">
              Contact
            </router-link>
            <router-link 
              to="/admin/login" 
              class="glass-button bg-gradient-primary hover:bg-primary-600 text-white px-4 py-2 rounded-lg font-medium"
            >
              Admin Login
            </router-link>
          </div>

          <!-- Mobile menu button -->
          <div class="md:hidden">
            <button @click="mobileMenuOpen = !mobileMenuOpen" class="text-gray-300 hover:text-white">
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Mobile menu -->
      <div v-if="mobileMenuOpen" class="md:hidden glass-effect border-t border-white/10">
        <div class="px-2 pt-2 pb-3 space-y-1">
          <router-link to="/" class="block px-3 py-2 text-gray-300 hover:text-primary-400">Home</router-link>
          <router-link to="/verify" class="block px-3 py-2 text-gray-300 hover:text-primary-400">Verify Product</router-link>
          <router-link to="/about" class="block px-3 py-2 text-gray-300 hover:text-primary-400">About</router-link>
          <router-link to="/contact" class="block px-3 py-2 text-gray-300 hover:text-primary-400">Contact</router-link>
          <router-link to="/admin/login" class="block px-3 py-2 text-primary-400 font-medium">Admin Login</router-link>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="relative pt-20 pb-32 hero-gradient">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <h1 class="text-5xl md:text-7xl font-bold text-white mb-6 animate-fade-in">
            Premium Product
            <span class="text-gradient block">Authentication</span>
          </h1>
          <p class="text-xl md:text-2xl text-gray-300 mb-12 max-w-3xl mx-auto animate-fade-in">
            Professional QR-code based product verification system with certificate management and PDF label generation.
          </p>
          
          <!-- CTA Buttons -->
          <div class="flex flex-col sm:flex-row gap-4 justify-center items-center animate-slide-up">
            <router-link 
              to="/verify" 
              class="glass-button bg-gradient-primary hover:scale-105 transform transition-all duration-300 neon-glow px-8 py-4 text-lg font-semibold"
            >
              Verify Product Now
            </router-link>
            <button 
              @click="scrollToFeatures" 
              class="glass-button hover:scale-105 transform transition-all duration-300 px-8 py-4 text-lg font-semibold"
            >
              Learn More
            </button>
          </div>
        </div>

        <!-- Hero Visual -->
        <div class="mt-20 relative">
          <div class="glass-card max-w-4xl mx-auto p-8 float-animation">
            <div class="grid md:grid-cols-2 gap-8 items-center">
              <div>
                <h3 class="text-2xl font-bold text-white mb-4">Instant Verification</h3>
                <p class="text-gray-300 mb-6">
                  Scan QR codes or enter serial numbers to instantly verify product authenticity with our advanced certificate system.
                </p>
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 bg-accent-500/20 rounded-lg flex items-center justify-center">
                    <svg class="w-6 h-6 text-accent-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                    </svg>
                  </div>
                  <span class="text-gray-300">Real-time verification</span>
                </div>
              </div>
              <div class="flex justify-center">
                <div class="w-48 h-48 bg-gradient-to-br from-primary-500/20 to-accent-500/20 rounded-2xl flex items-center justify-center neon-border glow-pulse">
                  <svg class="w-24 h-24 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V6a1 1 0 00-1-1H5a1 1 0 00-1 1v1a1 1 0 001 1zm12 0h2a1 1 0 001-1V6a1 1 0 00-1-1h-2a1 1 0 00-1 1v1a1 1 0 001 1zM5 20h2a1 1 0 001-1v-1a1 1 0 00-1-1H5a1 1 0 00-1 1v1a1 1 0 001 1z" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="py-20 bg-dark-800/50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-4xl md:text-5xl font-bold text-white mb-6">
            Powerful <span class="text-gradient">Features</span>
          </h2>
          <p class="text-xl text-gray-300 max-w-2xl mx-auto">
            Everything you need for professional product authentication and certificate management.
          </p>
        </div>

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          <!-- Feature 1 -->
          <div class="glass-card card-hover">
            <div class="w-16 h-16 bg-primary-500/20 rounded-2xl flex items-center justify-center mb-6 neon-border">
              <svg class="w-8 h-8 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold text-white mb-4">QR Code Verification</h3>
            <p class="text-gray-300">
              Advanced QR code scanning technology with instant verification results and detailed product information.
            </p>
          </div>

          <!-- Feature 2 -->
          <div class="glass-card card-hover">
            <div class="w-16 h-16 bg-accent-500/20 rounded-2xl flex items-center justify-center mb-6 neon-border">
              <svg class="w-8 h-8 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold text-white mb-4">Certificate Management</h3>
            <p class="text-gray-300">
              Complete certificate lifecycle management with automated generation and secure storage systems.
            </p>
          </div>

          <!-- Feature 3 -->
          <div class="glass-card card-hover">
            <div class="w-16 h-16 bg-primary-500/20 rounded-2xl flex items-center justify-center mb-6 neon-border">
              <svg class="w-8 h-8 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold text-white mb-4">PDF Label Generation</h3>
            <p class="text-gray-300">
              Professional PDF label generation with custom branding and high-quality QR codes for printing.
            </p>
          </div>

          <!-- Feature 4 -->
          <div class="glass-card card-hover">
            <div class="w-16 h-16 bg-accent-500/20 rounded-2xl flex items-center justify-center mb-6 neon-border">
              <svg class="w-8 h-8 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold text-white mb-4">Analytics Dashboard</h3>
            <p class="text-gray-300">
              Comprehensive analytics and reporting with real-time insights into verification patterns and usage.
            </p>
          </div>

          <!-- Feature 5 -->
          <div class="glass-card card-hover">
            <div class="w-16 h-16 bg-primary-500/20 rounded-2xl flex items-center justify-center mb-6 neon-border">
              <svg class="w-8 h-8 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold text-white mb-4">Secure API</h3>
            <p class="text-gray-300">
              RESTful API with JWT authentication and rate limiting for secure third-party integrations.
            </p>
          </div>

          <!-- Feature 6 -->
          <div class="glass-card card-hover">
            <div class="w-16 h-16 bg-accent-500/20 rounded-2xl flex items-center justify-center mb-6 neon-border">
              <svg class="w-8 h-8 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <h3 class="text-xl font-bold text-white mb-4">Open Source</h3>
            <p class="text-gray-300">
              100% open source with modern technologies including Python, FastAPI, Vue.js, and SQLite.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-20 bg-gradient-to-r from-primary-900/20 to-accent-900/20">
      <div class="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
        <h2 class="text-4xl md:text-5xl font-bold text-white mb-6">
          Ready to Get Started?
        </h2>
        <p class="text-xl text-gray-300 mb-8">
          Start verifying your products today with our powerful authentication system.
        </p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <router-link 
            to="/verify" 
            class="glass-button bg-gradient-primary hover:scale-105 transform transition-all duration-300 neon-glow px-8 py-4 text-lg font-semibold"
          >
            Verify a Product
          </router-link>
          <router-link 
            to="/admin/login" 
            class="glass-button hover:scale-105 transform transition-all duration-300 px-8 py-4 text-lg font-semibold"
          >
            Access Admin Panel
          </router-link>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-dark-900 border-t border-white/10 py-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid md:grid-cols-4 gap-8">
          <div class="col-span-2">
            <div class="flex items-center space-x-3 mb-4">
              <div class="w-10 h-10 bg-gradient-primary rounded-xl flex items-center justify-center neon-glow">
                <span class="text-white font-bold text-xl">N</span>
              </div>
              <span class="text-xl font-bold text-gradient">NeuroScan</span>
            </div>
            <p class="text-gray-400 mb-4">
              Professional product authentication system with advanced QR code verification and certificate management.
            </p>
            <p class="text-sm text-gray-500">
              © 2025 NeuroScan. Open Source Software.
            </p>
          </div>
          
          <div>
            <h3 class="text-white font-semibold mb-4">Product</h3>
            <ul class="space-y-2">
              <li><router-link to="/verify" class="text-gray-400 hover:text-primary-400 transition-colors">Verify Product</router-link></li>
              <li><router-link to="/about" class="text-gray-400 hover:text-primary-400 transition-colors">About</router-link></li>
              <li><a href="https://github.com/neuroscan" class="text-gray-400 hover:text-primary-400 transition-colors">GitHub</a></li>
            </ul>
          </div>
          
          <div>
            <h3 class="text-white font-semibold mb-4">Support</h3>
            <ul class="space-y-2">
              <li><router-link to="/contact" class="text-gray-400 hover:text-primary-400 transition-colors">Contact</router-link></li>
              <li><a href="/docs" class="text-gray-400 hover:text-primary-400 transition-colors">Documentation</a></li>
              <li><router-link to="/admin/login" class="text-gray-400 hover:text-primary-400 transition-colors">Admin Access</router-link></li>
            </ul>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'Home',
  setup() {
    const mobileMenuOpen = ref(false)

    const scrollToFeatures = () => {
      document.getElementById('features').scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
      })
    }

    return {
      mobileMenuOpen,
      scrollToFeatures
    }
  }
}
</script>
