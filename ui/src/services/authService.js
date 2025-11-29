import api from './api'

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
    throw error
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
    console.error('Logout error:', error)
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
    throw error
  }
}

export default {
  authenticateWithTelegram,
  logout,
  verifyToken,
}
