import api from './api'

export const accountService = {
  // Get user accounts
  getUserAccounts: async (userId) => {
    const response = await api.get(`/account/list_user_accounts/${userId}`)
    return response.data
  },

  // Get account balance
  getBalance: async (address) => {
    const response = await api.get(`/account/balance/${address}`)
    return response.data
  },

  // Create new account
  createAccount: async (accountData) => {
    const response = await api.post('/account/create', accountData)
    return response.data
  },
}

export default accountService
