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
          Contact <span class="text-gradient">Us</span>
        </h1>
        <p class="text-xl text-gray-300">
          Get in touch with our team for support and inquiries
        </p>
      </div>

      <div class="grid md:grid-cols-2 gap-8">
        <!-- Contact Form -->
        <div class="glass-card">
          <h2 class="text-2xl font-bold text-white mb-6">Send us a Message</h2>
          
          <form @submit.prevent="submitForm" class="space-y-4">
            <div class="grid md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">
                  First Name *
                </label>
                <input
                  v-model="form.firstName"
                  type="text"
                  required
                  class="glass-input w-full"
                  placeholder="John"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-300 mb-2">
                  Last Name *
                </label>
                <input
                  v-model="form.lastName"
                  type="text"
                  required
                  class="glass-input w-full"
                  placeholder="Doe"
                />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">
                Email Address *
              </label>
              <input
                v-model="form.email"
                type="email"
                required
                class="glass-input w-full"
                placeholder="john@example.com"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">
                Company
              </label>
              <input
                v-model="form.company"
                type="text"
                class="glass-input w-full"
                placeholder="Company Name"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">
                Subject *
              </label>
              <select
                v-model="form.subject"
                required
                class="glass-input w-full"
              >
                <option value="">Select a subject</option>
                <option value="support">Technical Support</option>
                <option value="sales">Sales Inquiry</option>
                <option value="partnership">Partnership</option>
                <option value="bug">Bug Report</option>
                <option value="feature">Feature Request</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">
                Message *
              </label>
              <textarea
                v-model="form.message"
                rows="5"
                required
                class="glass-input w-full resize-none"
                placeholder="Tell us how we can help you..."
              ></textarea>
            </div>

            <button
              type="submit"
              class="w-full glass-button bg-gradient-primary hover:scale-105 transform transition-all duration-300 neon-glow py-3 font-semibold"
              :disabled="isSubmitting"
            >
              <div v-if="isSubmitting" class="flex items-center justify-center">
                <div class="loading-spinner mr-2"></div>
                Sending...
              </div>
              <div v-else>
                Send Message
              </div>
            </button>
          </form>
        </div>

        <!-- Contact Information -->
        <div class="space-y-6">
          <div class="glass-card">
            <h3 class="text-xl font-bold text-white mb-4">Get in Touch</h3>
            <div class="space-y-4">
              <div class="flex items-start space-x-3">
                <div class="w-10 h-10 bg-primary-500/20 rounded-lg flex items-center justify-center">
                  <svg class="w-5 h-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-white">Email</h4>
                  <p class="text-gray-300">support@neuroscan.com</p>
                  <p class="text-gray-300">sales@neuroscan.com</p>
                </div>
              </div>

              <div class="flex items-start space-x-3">
                <div class="w-10 h-10 bg-accent-500/20 rounded-lg flex items-center justify-center">
                  <svg class="w-5 h-5 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-white">Phone</h4>
                  <p class="text-gray-300">+1 (555) 123-4567</p>
                  <p class="text-gray-400 text-sm">Mon-Fri 9AM-5PM EST</p>
                </div>
              </div>

              <div class="flex items-start space-x-3">
                <div class="w-10 h-10 bg-primary-500/20 rounded-lg flex items-center justify-center">
                  <svg class="w-5 h-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <div>
                  <h4 class="font-semibold text-white">Office</h4>
                  <p class="text-gray-300">123 Innovation Drive</p>
                  <p class="text-gray-300">Tech Valley, CA 94041</p>
                </div>
              </div>
            </div>
          </div>

          <div class="glass-card">
            <h3 class="text-xl font-bold text-white mb-4">Technical Support</h3>
            <p class="text-gray-300 mb-4">
              Need help with NeuroScan? Our technical support team is here to assist you.
            </p>
            <div class="space-y-3">
              <a href="/docs" class="flex items-center text-primary-400 hover:text-primary-300 transition-colors">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                Documentation
              </a>
              <a href="https://github.com/neuroscan" class="flex items-center text-primary-400 hover:text-primary-300 transition-colors">
                <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                GitHub Issues
              </a>
            </div>
          </div>

          <div class="glass-card">
            <h3 class="text-xl font-bold text-white mb-4">Response Times</h3>
            <div class="space-y-2">
              <div class="flex justify-between">
                <span class="text-gray-400">Technical Support:</span>
                <span class="text-white">Within 24 hours</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">Sales Inquiries:</span>
                <span class="text-white">Within 4 hours</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">Bug Reports:</span>
                <span class="text-white">Within 48 hours</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">General Questions:</span>
                <span class="text-white">Within 72 hours</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useToast } from 'vue-toastification'

export default {
  name: 'Contact',
  setup() {
    const toast = useToast()
    const isSubmitting = ref(false)
    
    const form = ref({
      firstName: '',
      lastName: '',
      email: '',
      company: '',
      subject: '',
      message: ''
    })

    const submitForm = async () => {
      isSubmitting.value = true
      
      try {
        // Simulate form submission
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // In a real app, you would send this to your backend
        console.log('Form submitted:', form.value)
        
        toast.success('Message sent successfully! We\'ll get back to you soon.')
        
        // Reset form
        form.value = {
          firstName: '',
          lastName: '',
          email: '',
          company: '',
          subject: '',
          message: ''
        }
      } catch (error) {
        toast.error('Failed to send message. Please try again.')
      } finally {
        isSubmitting.value = false
      }
    }

    return {
      form,
      isSubmitting,
      submitForm
    }
  }
}
</script>
