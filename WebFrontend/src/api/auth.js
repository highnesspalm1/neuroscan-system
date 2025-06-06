import api from './index'

export const authApi = {
  // Login
  async login(credentials) {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)
    
    const response = await api.post('/admin/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      }
    })
    return response.data
  },

  // Get current user
  async getCurrentUser() {
    const response = await api.get('/admin/me')
    return response.data
  },

  // Refresh token
  async refreshToken() {
    const response = await api.post('/admin/refresh')
    return response.data
  },

  // Logout
  async logout() {
    const response = await api.post('/admin/logout')
    return response.data
  }
}
