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

    <!-- Main Content -->
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="text-center mb-12">
        <h1 class="text-4xl md:text-5xl font-bold text-white mb-6">
          About <span class="text-gradient">NeuroScan</span>
        </h1>
        <p class="text-xl text-gray-300">
          Professional product authentication system built with modern technologies
        </p>
      </div>

      <!-- About Content -->
      <div class="space-y-8">
        <div class="glass-card">
          <h2 class="text-2xl font-bold text-white mb-4">Our Mission</h2>
          <p class="text-gray-300 leading-relaxed">
            NeuroScan is dedicated to providing premium product authentication solutions that help businesses 
            protect their brands and customers verify authentic products. Our advanced QR-code based system 
            combines security, usability, and comprehensive management tools to deliver a complete authentication ecosystem.
          </p>
        </div>

        <div class="glass-card">
          <h2 class="text-2xl font-bold text-white mb-6">Technology Stack</h2>
          <div class="grid md:grid-cols-2 gap-6">
            <div>
              <h3 class="text-lg font-semibold text-white mb-3">Backend Technologies</h3>
              <ul class="space-y-2 text-gray-300">
                <li class="flex items-center">
                  <span class="w-2 h-2 bg-primary-500 rounded-full mr-3"></span>
                  Python 3.11+ with FastAPI
                </li>
                <li class="flex items-center">
                  <span class="w-2 h-2 bg-primary-500 rounded-full mr-3"></span>
                  SQLAlchemy ORM with SQLite
                </li>
                <li class="flex items-center">
                  <span class="w-2 h-2 bg-primary-500 rounded-full mr-3"></span>
                  JWT Authentication & Security
                </li>
                <li class="flex items-center">
                  <span class="w-2 h-2 bg-primary-500 rounded-full mr-3"></span>
                  ReportLab for PDF Generation
                </li>
              </ul>
            </div>
            
            <div>
              <h3 class="text-lg font-semibold text-white mb-3">Frontend Technologies</h3>
              <ul class="space-y-2 text-gray-300">
                <li class="flex items-center">
                  <span class="w-2 h-2 bg-accent-500 rounded-full mr-3"></span>
                  Vue.js 3 with Composition API
                </li>
                <li class="flex items-center">
                  <span class="w-2 h-2 bg-accent-500 rounded-full mr-3"></span>
                  TailwindCSS for Styling
                </li>
                <li class="flex items-center">
                  <span class="w-2 h-2 bg-accent-500 rounded-full mr-3"></span>
                  PySide6 Desktop Application
                </li>
                <li class="flex items-center">
                  <span class="w-2 h-2 bg-accent-500 rounded-full mr-3"></span>
                  HTML5 QR Code Scanner
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div class="glass-card">
          <h2 class="text-2xl font-bold text-white mb-4">Key Features</h2>
          <div class="grid md:grid-cols-2 gap-6">
            <div class="space-y-4">
              <div class="flex items-start space-x-3">
                <div class="w-8 h-8 bg-primary-500/20 rounded-lg flex items-center justify-center mt-1">
                  <svg class="w-4 h-4 text-primary-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-white">QR Code Verification</h4>
                  <p class="text-gray-400 text-sm">Advanced scanning with real-time verification</p>
                </div>
              </div>
              
              <div class="flex items-start space-x-3">
                <div class="w-8 h-8 bg-primary-500/20 rounded-lg flex items-center justify-center mt-1">
                  <svg class="w-4 h-4 text-primary-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-white">Certificate Management</h4>
                  <p class="text-gray-400 text-sm">Complete lifecycle management system</p>
                </div>
              </div>
              
              <div class="flex items-start space-x-3">
                <div class="w-8 h-8 bg-primary-500/20 rounded-lg flex items-center justify-center mt-1">
                  <svg class="w-4 h-4 text-primary-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-white">PDF Label Generation</h4>
                  <p class="text-gray-400 text-sm">Professional labels with embedded QR codes</p>
                </div>
              </div>
            </div>
            
            <div class="space-y-4">
              <div class="flex items-start space-x-3">
                <div class="w-8 h-8 bg-accent-500/20 rounded-lg flex items-center justify-center mt-1">
                  <svg class="w-4 h-4 text-accent-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-white">Analytics Dashboard</h4>
                  <p class="text-gray-400 text-sm">Comprehensive reporting and insights</p>
                </div>
              </div>
              
              <div class="flex items-start space-x-3">
                <div class="w-8 h-8 bg-accent-500/20 rounded-lg flex items-center justify-center mt-1">
                  <svg class="w-4 h-4 text-accent-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-white">RESTful API</h4>
                  <p class="text-gray-400 text-sm">Secure API for third-party integrations</p>
                </div>
              </div>
              
              <div class="flex items-start space-x-3">
                <div class="w-8 h-8 bg-accent-500/20 rounded-lg flex items-center justify-center mt-1">
                  <svg class="w-4 h-4 text-accent-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-white">Open Source</h4>
                  <p class="text-gray-400 text-sm">100% open source with MIT license</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="glass-card">
          <h2 class="text-2xl font-bold text-white mb-4">Open Source Commitment</h2>
          <p class="text-gray-300 leading-relaxed mb-4">
            NeuroScan is completely open source and available under the MIT license. We believe in transparency, 
            security through peer review, and community-driven development. The entire codebase is available 
            on GitHub for inspection, contribution, and customization.
          </p>
          <div class="flex flex-wrap gap-4">
            <a href="https://github.com/neuroscan" class="glass-button hover:scale-105 transform transition-all duration-300">
              <svg class="w-5 h-5 inline mr-2" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
              View on GitHub
            </a>
            <a href="/docs" class="glass-button hover:scale-105 transform transition-all duration-300">
              Documentation
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'About'
}
</script>
