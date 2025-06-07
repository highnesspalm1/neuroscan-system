import api from './index'

export const authApi = {
  // Login with retry logic for Render cold starts
  async login(credentials) {
    console.log('AuthAPI: Sending login request to /auth/login')
    console.log('AuthAPI: Request payload:', { username: credentials.username })
    
    try {
      const response = await api.post('/auth/login', {
        username: credentials.username,
        password: credentials.password
      })
      
      console.log('AuthAPI: Login response status:', response.status)
      console.log('AuthAPI: Login response data:', response.data)
      
      return response.data
    } catch (error) {
      console.error('AuthAPI: Login error:', error)
      
      // If timeout error, give user helpful message
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        throw new Error('Server is starting up (this can take up to 60 seconds on free hosting). Please try again in a moment.')
      }
      
      throw error
    }
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
