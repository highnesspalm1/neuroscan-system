import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Public pages
import Home from '@/views/Home.vue'
import Verify from '@/views/Verify.vue'
import About from '@/views/About.vue'
import Contact from '@/views/Contact.vue'

// Admin pages
import AdminLogin from '@/views/admin/Login.vue'
import AdminDashboard from '@/views/admin/Dashboard.vue'
import AdminProducts from '@/views/admin/Products.vue'
import AdminCertificates from '@/views/admin/Certificates.vue'
import AdminAnalytics from '@/views/admin/Analytics.vue'

// Error pages
import NotFound from '@/views/errors/NotFound.vue'

const routes = [
  // Public Routes
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { 
      title: 'NeuroScan - Premium Product Authentication',
      description: 'Professional QR-code based product verification system'
    }
  },
  {
    path: '/verify',
    name: 'Verify',
    component: Verify,
    meta: { 
      title: 'Verify Product - NeuroScan',
      description: 'Verify product authenticity using QR code or serial number'
    }
  },
  {
    path: '/verify/:serialNumber',
    name: 'VerifyDirect',
    component: Verify,
    props: true,
    meta: { 
      title: 'Product Verification - NeuroScan',
      description: 'Product authenticity verification results'
    }
  },
  {
    path: '/about',
    name: 'About',
    component: About,
    meta: { 
      title: 'About NeuroScan',
      description: 'Learn about our premium product authentication system'
    }
  },
  {
    path: '/contact',
    name: 'Contact',
    component: Contact,
    meta: { 
      title: 'Contact Us - NeuroScan',
      description: 'Get in touch with our team for support and inquiries'
    }
  },

  // Admin Routes
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: AdminLogin,
    meta: { 
      title: 'Admin Login - NeuroScan',
      description: 'Administrator access to NeuroScan management system',
      guest: true
    }
  },
  {
    path: '/admin',
    redirect: '/admin/dashboard'
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { 
      title: 'Admin Dashboard - NeuroScan',
      description: 'NeuroScan administration dashboard',
      requiresAuth: true
    }
  },  {
    path: '/admin/products',
    name: 'AdminProducts',
    component: AdminProducts,
    meta: { 
      title: 'Product Management - NeuroScan',
      description: 'Manage products and inventory',
      requiresAuth: true
    }
  },
  {
    path: '/admin/certificates',
    name: 'AdminCertificates',
    component: AdminCertificates,
    meta: { 
      title: 'Certificate Management - NeuroScan',
      description: 'Manage product certificates and authentications',
      requiresAuth: true
    }
  },
  {
    path: '/admin/analytics',
    name: 'AdminAnalytics',
    component: AdminAnalytics,
    meta: { 
      title: 'Analytics & Reports - NeuroScan',
      description: 'View verification analytics and generate reports',
      requiresAuth: true
    }
  },

  // Error Routes
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: { 
      title: 'Page Not Found - NeuroScan',
      description: 'The requested page could not be found'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Set page title and meta
  if (to.meta.title) {
    document.title = to.meta.title
  }
  
  if (to.meta.description) {
    const metaDescription = document.querySelector('meta[name="description"]')
    if (metaDescription) {
      metaDescription.setAttribute('content', to.meta.description)
    }
  }

  // Check authentication requirements
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      next({ name: 'AdminLogin', query: { redirect: to.fullPath } })
      return
    }
  }

  // Redirect authenticated users away from login
  if (to.meta.guest && authStore.isAuthenticated) {
    next({ name: 'AdminDashboard' })
    return
  }

  next()
})

router.afterEach((to, from) => {
  // Analytics tracking would go here
  console.log(`Navigation: ${from.path} -> ${to.path}`)
})

export default router
