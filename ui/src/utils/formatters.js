// Format date
export const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Format currency
export const formatCurrency = (amount, currency = 'USD') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount)
}

// Format number
export const formatNumber = (number, decimals = 2) => {
  return Number(number).toFixed(decimals)
}

// Truncate address
export const truncateAddress = (address, start = 6, end = 4) => {
  if (!address) return ''
  return `${address.slice(0, start)}...${address.slice(-end)}`
}

// Format percentage
export const formatPercentage = (value) => {
  return `${(value * 100).toFixed(2)}%`
}
