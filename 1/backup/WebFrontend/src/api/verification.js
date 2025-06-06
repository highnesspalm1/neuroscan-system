import api from './index'

export const verificationApi = {
  // Verify product by serial number
  async verifyProduct(serialNumber) {
    const response = await api.get(`/verify/${serialNumber}`)
    return response.data
  },

  // Get scan statistics (public endpoint)
  async getScanStats() {
    const response = await api.get('/verify/stats')
    return response.data
  },

  // Submit verification scan log
  async logScan(scanData) {
    const response = await api.post('/verify/log', scanData)
    return response.data
  }
}
