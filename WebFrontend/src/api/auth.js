import api from './index'

export const authApi = {
  // Login
  async login(credentials) {
    console.log('AuthAPI: Sending login request to /auth/login')
    console.log('AuthAPI: Request payload:', { username: credentials.username })
    
    const response = await api.post('/auth/login', {
      username: credentials.username,
      password: credentials.password
    })
    
    console.log('AuthAPI: Login response status:', response.status)
    console.log('AuthAPI: Login response data:', response.data)
    
    return response.data
  },

  // Get current user
  async getCurrentUser() {
    console.log('AuthAPI: Getting current user from /auth/me')
    const response = await api.get('/auth/me')
    console.log('AuthAPI: Current user response:', response.data)
    return response.data
  },

  // Refresh token (using token endpoint for now)
  async refreshToken() {
    console.log('AuthAPI: Refreshing token')
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
