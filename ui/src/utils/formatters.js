import i18n from '../i18n'

/**
 * Get the current locale from i18n
 * Falls back to 'en-US' if i18n is not initialized
 */
const getCurrentLocale = () => {
  try {
    const language = i18n.language || 'en'
    // Convert language code to locale (e.g., 'en' -> 'en-US')
    return language.includes('-') ? language : `${language}-${language.toUpperCase()}`
  } catch (error) {
    console.warn('Failed to get i18n locale, falling back to en-US', error)
    return 'en-US'
  }
}

/**
 * Format date using the current locale
 * @param {Date|string|number} date - The date to format
 * @param {Object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date string
 */
export const formatDate = (date, options = {}) => {
  const locale = getCurrentLocale()
  const defaultOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }
  
  return new Date(date).toLocaleDateString(locale, {
    ...defaultOptions,
    ...options,
  })
}

/**
 * Format currency using the current locale
 * @param {number} amount - The amount to format
 * @param {string} currency - The currency code (default: 'USD')
 * @returns {string} Formatted currency string
 */
export const formatCurrency = (amount, currency = 'USD') => {
  const locale = getCurrentLocale()
  
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
  }).format(amount)
}

/**
 * Format number using the current locale
 * @param {number} number - The number to format
 * @param {number} decimals - Number of decimal places (default: 2)
 * @returns {string} Formatted number string
 */
export const formatNumber = (number, decimals = 2) => {
  const locale = getCurrentLocale()
  
  return new Intl.NumberFormat(locale, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(number)
}

// Truncate address
export const truncateAddress = (address, start = 6, end = 4) => {
  if (!address) return ''
  return `${address.slice(0, start)}...${address.slice(-end)}`
}

/**
 * Format percentage using the current locale
 * @param {number} value - The value to format (0-1 range)
 * @returns {string} Formatted percentage string
 */
export const formatPercentage = (value) => {
  const locale = getCurrentLocale()
  
  return new Intl.NumberFormat(locale, {
    style: 'percent',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}
