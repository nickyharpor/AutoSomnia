import api from './api'
import i18n from '../i18n'

export const userService = {
  // Get all users
  getUsers: async (params = {}) => {
    try {
      const response = await api.get('/users/', { params })
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || i18n.t('errors:user.loadFailed')
      throw new Error(message)
    }
  },

  // Get user by ID
  getUser: async (userId) => {
    try {
      const response = await api.get(`/users/${userId}`)
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || i18n.t('errors:user.loadFailed')
      throw new Error(message)
    }
  },

  // Create user
  createUser: async (userData) => {
    try {
      const response = await api.post('/users/create', userData)
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || i18n.t('errors:user.createFailed')
      throw new Error(message)
    }
  },

  // Update user
  updateUser: async (userId, userData) => {
    try {
      const response = await api.put(`/users/${userId}`, userData)
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || i18n.t('errors:user.updateFailed')
      throw new Error(message)
    }
  },

  // Delete user
  deleteUser: async (userId) => {
    try {
      const response = await api.delete(`/users/${userId}`)
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || i18n.t('errors:user.deleteFailed')
      throw new Error(message)
    }
  },

  // Enable auto-exchange
  enableAutoExchange: async (userId) => {
    try {
      const response = await api.post(`/users/${userId}/auto-exchange/enable`)
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || i18n.t('errors:user.autoExchangeFailed')
      throw new Error(message)
    }
  },

  // Disable auto-exchange
  disableAutoExchange: async (userId) => {
    try {
      const response = await api.post(`/users/${userId}/auto-exchange/disable`)
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || i18n.t('errors:user.autoExchangeFailed')
      throw new Error(message)
    }
  },
}

export default userService
