import api from './index'

const customerApi = {
  // Authentication
  async login(credentials) {
    const response = await api.post('/customer/login', credentials)
    return response.data
  },

  async getMe() {
    const response = await api.get('/customer/me')
    return response.data
  },

  // Dashboard
  async getDashboard() {
    const response = await api.get('/customer/dashboard')
    return response.data
  },

  // Customer data
  async getProducts(skip = 0, limit = 100) {
    const response = await api.get('/customer/products', {
      params: { skip, limit }
    })
    return response.data
  },

  async getCertificates(skip = 0, limit = 100) {
    const response = await api.get('/customer/certificates', {
      params: { skip, limit }
    })
    return response.data
  },

  async getScanLogs(skip = 0, limit = 100) {
    const response = await api.get('/customer/scan-logs', {
      params: { skip, limit }
    })
    return response.data
  }
}

export default customerApi
