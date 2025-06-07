import api from './index'

export const authApi = {
  // Login
  async login(credentials) {
    const response = await api.post('/auth/login', {
      username: credentials.username,
      password: credentials.password
    })
    return response.data
  },

  // Get current user
  async getCurrentUser() {
    const response = await api.get('/auth/me')
    return response.data
  },

  // Refresh token (using token endpoint for now)
  async refreshToken() {
    const formData = new FormData()
    formData.append('username', 'admin')
    formData.append('password', 'admin123')
    
    const response = await api.post('/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      }
    })
    return response.data
  },

  // Logout (placeholder - no backend endpoint yet)
  async logout() {
    return { message: 'Logged out successfully' }
  }
}
