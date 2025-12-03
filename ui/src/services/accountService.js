import api from './api'
import i18n from '../i18n'

export const accountService = {
  // Get user accounts
  getUserAccounts: async (userId) => {
    try {
      const response = await api.get(`/account/list_user_accounts/${userId}`)
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || i18n.t('errors:account.loadFailed')
      throw new Error(message)
    }
  },

  // Get account balance
  getBalance: async (address) => {
    try {
      const response = await api.get(`/account/balance/${address}`)
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || i18n.t('errors:account.loadFailed')
      throw new Error(message)
    }
  },

  // Create new account
  createAccount: async (accountData) => {
    try {
      const response = await api.post('/account/create', accountData)
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || i18n.t('errors:account.createFailed')
      throw new Error(message)
    }
  },
}

export default accountService
