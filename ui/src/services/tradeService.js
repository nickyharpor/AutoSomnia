import api from './api'

export const tradeService = {
  // Get all trade events
  getTrades: async (params = {}) => {
    const response = await api.get('/trades/', { params })
    return response.data
  },

  // Get trade by ID
  getTrade: async (tradeId) => {
    const response = await api.get(`/trades/${tradeId}`)
    return response.data
  },

  // Get trades by user
  getUserTrades: async (userId) => {
    const response = await api.get(`/trades/user/${userId}`)
    return response.data
  },

  // Get trade statistics
  getTradeStats: async () => {
    const response = await api.get('/trades/stats')
    return response.data
  },
}

export default tradeService
