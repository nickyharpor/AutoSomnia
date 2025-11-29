import api from './api'

export const userService = {
  // Get all users
  getUsers: async (params = {}) => {
    const response = await api.get('/users/', { params })
    return response.data
  },

  // Get user by ID
  getUser: async (userId) => {
    const response = await api.get(`/users/${userId}`)
    return response.data
  },

  // Create user
  createUser: async (userData) => {
    const response = await api.post('/users/create', userData)
    return response.data
  },

  // Update user
  updateUser: async (userId, userData) => {
    const response = await api.put(`/users/${userId}`, userData)
    return response.data
  },

  // Delete user
  deleteUser: async (userId) => {
    const response = await api.delete(`/users/${userId}`)
    return response.data
  },

  // Enable auto-exchange
  enableAutoExchange: async (userId) => {
    const response = await api.post(`/users/${userId}/auto-exchange/enable`)
    return response.data
  },

  // Disable auto-exchange
  disableAutoExchange: async (userId) => {
    const response = await api.post(`/users/${userId}/auto-exchange/disable`)
    return response.data
  },
}

export default userService
