import api from './index'

export const adminApi = {
  // Customers
  async getCustomers() {
    const response = await api.get('/admin/customers/')
    return response.data
  },

  async getCustomer(id) {
    const response = await api.get(`/admin/customers/${id}`)
    return response.data
  },

  async createCustomer(customerData) {
    const response = await api.post('/admin/customers/', customerData)
    return response.data
  },

  async updateCustomer(id, customerData) {
    const response = await api.put(`/admin/customers/${id}`, customerData)
    return response.data
  },

  async deleteCustomer(id) {
    const response = await api.delete(`/admin/customers/${id}`)
    return response.data
  },

  // Products
  async getProducts() {
    const response = await api.get('/admin/products/')
    return response.data
  },

  async getProduct(id) {
    const response = await api.get(`/admin/products/${id}`)
    return response.data
  },

  async createProduct(productData) {
    const response = await api.post('/admin/products/', productData)
    return response.data
  },

  async updateProduct(id, productData) {
    const response = await api.put(`/admin/products/${id}`, productData)
    return response.data
  },

  async deleteProduct(id) {
    const response = await api.delete(`/admin/products/${id}`)
    return response.data
  },

  // Certificates
  async getCertificates() {
    const response = await api.get('/admin/certificates/')
    return response.data
  },

  async getCertificate(id) {
    const response = await api.get(`/admin/certificates/${id}`)
    return response.data
  },

  async createCertificate(certificateData) {
    const response = await api.post('/admin/certificates/', certificateData)
    return response.data
  },

  async updateCertificate(id, certificateData) {
    const response = await api.put(`/admin/certificates/${id}`, certificateData)
    return response.data
  },

  async deleteCertificate(id) {
    const response = await api.delete(`/admin/certificates/${id}`)
    return response.data
  },

  // Scan Logs
  async getScanLogs(params = {}) {
    const response = await api.get('/admin/scan-logs/', { params })
    return response.data
  },

  async getScanLog(id) {
    const response = await api.get(`/admin/scan-logs/${id}`)
    return response.data
  },

  // Dashboard
  async getDashboardStats() {
    const response = await api.get('/admin/dashboard/stats')
    return response.data
  },

  async getRecentVerifications() {
    const response = await api.get('/admin/dashboard/recent-verifications')
    return response.data
  },

  // Analytics
  async getAnalytics(timeRange = '30d') {
    const response = await api.get(`/admin/analytics?range=${timeRange}`)
    return response.data
  },

  async exportAnalyticsReport(timeRange = '30d') {
    const response = await api.get(`/admin/analytics/export?range=${timeRange}`, {
      responseType: 'blob'
    })
    return response.data
  },

  // Settings
  async getSettings() {
    const response = await api.get('/admin/settings/')
    return response.data
  },

  async updateSettings(settings) {
    const response = await api.put('/admin/settings/', settings)
    return response.data
  },
  // PDF Generation
  async generateCertificatePDF(certificateId) {
    const response = await api.get(`/admin/certificates/${certificateId}/pdf`, {
      responseType: 'blob'
    })
    return response.data
  },

  async generateProductLabel(productId, options = {}) {
    const response = await api.get(`/labels/product/${productId}`, {
      params: options,
      responseType: 'blob'
    })
    return response.data
  },

  async generateCertificateLabel(certificateId) {
    const response = await api.get(`/labels/certificate/${certificateId}`, {
      responseType: 'blob'
    })
    return response.data
  },

  async generateBatchLabels(productIds, options = {}) {
    const response = await api.post('/labels/batch', productIds, {
      params: options,
      responseType: 'blob'
    })
    return response.data
  },

  async generateAllProductsLabels(options = {}) {
    const response = await api.get('/labels/all-products', {
      params: options,
      responseType: 'blob'
    })
    return response.data
  },

  async generateTemplatePreview(labelType = 'product') {
    const response = await api.get('/labels/template-preview', {
      params: { label_type: labelType },
      responseType: 'blob'
    })
    return response.data
  },

  async getPdfStats() {
    const response = await api.get('/labels/stats')
    return response.data
  },

  // Certificate Management
  async downloadCertificate(certificateId) {
    const response = await api.get(`/admin/certificates/${certificateId}/download`, {
      responseType: 'blob'
    })
    return response.data
  },

  async revokeCertificate(certificateId) {
    const response = await api.post(`/admin/certificates/${certificateId}/revoke`)
    return response.data
  }
}
