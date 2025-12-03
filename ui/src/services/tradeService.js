import api from './api'
import i18n from '../i18n'

export const tradeService = {
  // Get all trade events
  getTrades: async (params = {}) => {
    try {
      const response = await api.get('/trades/', { params })
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || i18n.t('errors:trade.loadFailed')
      throw new Error(message)
    }
  },

  // Get trade by ID
  getTrade: async (tradeId) => {
    try {
      const response = await api.get(`/trades/${tradeId}`)
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || i18n.t('errors:trade.loadFailed')
      throw new Error(message)
    }
  },

  // Get trades by user
  getUserTrades: async (userId) => {
    try {
      const response = await api.get(`/trades/user/${userId}`)
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || i18n.t('errors:trade.loadFailed')
      throw new Error(message)
    }
  },

  // Get trade statistics
  getTradeStats: async () => {
    try {
      const response = await api.get('/trades/stats')
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || i18n.t('errors:trade.loadFailed')
      throw new Error(message)
    }
  },
}

export default tradeService
