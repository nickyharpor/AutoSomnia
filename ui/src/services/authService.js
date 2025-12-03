import api from './api'
import i18n from '../i18n'

/**
 * Verify and authenticate Telegram user data
 * @param {Object} telegramData - Data received from Telegram widget
 * @returns {Promise<Object>} Authentication response with token and user data
 */
export const authenticateWithTelegram = async (telegramData) => {
  try {
    const response = await api.post('/auth/telegram', telegramData)
    return response.data
  } catch (error) {
    const message = error.response?.data?.message || i18n.t('errors:auth.loginFailed')
    throw new Error(message)
  }
}

/**
 * Logout user
 * @returns {Promise<void>}
 */
export const logout = async () => {
  try {
    await api.post('/auth/logout')
  } catch (error) {
    const message = error.response?.data?.message || i18n.t('errors:auth.logoutFailed')
    console.error('Logout error:', message)
    throw new Error(message)
  }
}

/**
 * Verify current token
 * @returns {Promise<Object>} User data if token is valid
 */
export const verifyToken = async () => {
  try {
    const response = await api.get('/auth/verify')
    return response.data
  } catch (error) {
    const message = error.response?.data?.message || i18n.t('errors:auth.verifyFailed')
    throw new Error(message)
  }
}

export default {
  authenticateWithTelegram,
  logout,
  verifyToken,
}
