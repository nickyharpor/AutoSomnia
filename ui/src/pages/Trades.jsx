import { useState, useMemo } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { X, ChevronLeft, ChevronRight, ArrowUpDown } from 'lucide-react'
import Card from '../components/common/Card'
import Button from '../components/common/Button'
import './Trades.css'

const Trades = () => {
  const [timeframe, setTimeframe] = useState('week')
  const [selectedTrade, setSelectedTrade] = useState(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [sortConfig, setSortConfig] = useState({ key: 'date', direction: 'desc' })
  const [filters, setFilters] = useState({
    tradeId: '',
    fromCurrency: '',
    toCurrency: ''
  })
  
  const itemsPerPage = 10

  // Sample data for the chart
  // TODO: Replace with API call in the future
  const generateSampleData = (timeframe) => {
    const now = new Date()
    const data = []

    switch (timeframe) {
      case 'week':
        // Last 7 days
        for (let i = 6; i >= 0; i--) {
          const date = new Date(now)
          date.setDate(date.getDate() - i)
          data.push({
            date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
            amount: Math.floor(Math.random() * 5000) + 1000
          })
        }
        break
      case 'month':
        // Last 30 days (show every 3 days)
        for (let i = 30; i >= 0; i -= 3) {
          const date = new Date(now)
          date.setDate(date.getDate() - i)
          data.push({
            date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
            amount: Math.floor(Math.random() * 8000) + 2000
          })
        }
        break
      case '3months':
        // Last 90 days (show every 9 days)
        for (let i = 90; i >= 0; i -= 9) {
          const date = new Date(now)
          date.setDate(date.getDate() - i)
          data.push({
            date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
            amount: Math.floor(Math.random() * 12000) + 3000
          })
        }
        break
      case 'year':
        // Last 12 months
        for (let i = 11; i >= 0; i--) {
          const date = new Date(now)
          date.setMonth(date.getMonth() - i)
          data.push({
            date: date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' }),
            amount: Math.floor(Math.random() * 20000) + 5000
          })
        }
        break
      default:
        break
    }

    return data
  }

  const chartData = useMemo(() => generateSampleData(timeframe), [timeframe])

  const timeframeOptions = [
    { value: 'week', label: 'Last Week' },
    { value: 'month', label: 'Last Month' },
    { value: '3months', label: 'Last 3 Months' },
    { value: 'year', label: 'Last Year' }
  ]

  // Sample trades data
  // TODO: Replace with API call in the future
  const sampleTrades = useMemo(() => {
    const trades = []
    const currencies = ['USDT', 'SOMI', 'ETH', 'PEPE', 'WBTC']
    const now = new Date()
    
    for (let i = 0; i < 50; i++) {
      const fromCurrency = currencies[Math.floor(Math.random() * currencies.length)]
      let toCurrency = currencies[Math.floor(Math.random() * currencies.length)]
      while (toCurrency === fromCurrency) {
        toCurrency = currencies[Math.floor(Math.random() * currencies.length)]
      }
      
      const fromAmount = (Math.random() * 1000 + 100).toFixed(2)
      const toAmount = (Math.random() * 1000 + 100).toFixed(2)
      const usdValue = (Math.random() * 5000 + 500).toFixed(2)
      
      const date = new Date(now)
      date.setHours(date.getHours() - i * 2)
      
      trades.push({
        id: `TXN${String(i + 1).padStart(6, '0')}`,
        fromCurrency,
        fromAmount,
        toCurrency,
        toAmount,
        usdValue,
        date: date.toISOString(),
        status: Math.random() > 0.1 ? 'success' : 'failed',
        txHash: `0x${Math.random().toString(16).substr(2, 64)}`,
        gasUsed: (Math.random() * 100000 + 21000).toFixed(0),
        gasFee: (Math.random() * 10 + 1).toFixed(4)
      })
    }
    
    return trades
  }, [])

  // Filter trades
  const filteredTrades = useMemo(() => {
    return sampleTrades.filter(trade => {
      const matchesId = trade.id.toLowerCase().includes(filters.tradeId.toLowerCase())
      const matchesFrom = trade.fromCurrency.toLowerCase().includes(filters.fromCurrency.toLowerCase())
      const matchesTo = trade.toCurrency.toLowerCase().includes(filters.toCurrency.toLowerCase())
      return matchesId && matchesFrom && matchesTo
    })
  }, [sampleTrades, filters])

  // Sort trades
  const sortedTrades = useMemo(() => {
    const sorted = [...filteredTrades]
    sorted.sort((a, b) => {
      let aValue = a[sortConfig.key]
      let bValue = b[sortConfig.key]
      
      if (sortConfig.key === 'date') {
        aValue = new Date(aValue).getTime()
        bValue = new Date(bValue).getTime()
      } else if (sortConfig.key === 'usdValue') {
        aValue = parseFloat(aValue)
        bValue = parseFloat(bValue)
      }
      
      if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1
      if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1
      return 0
    })
    return sorted
  }, [filteredTrades, sortConfig])

  // Paginate trades
  const paginatedTrades = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage
    return sortedTrades.slice(startIndex, startIndex + itemsPerPage)
  }, [sortedTrades, currentPage])

  const totalPages = Math.ceil(sortedTrades.length / itemsPerPage)

  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }))
  }

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
    setCurrentPage(1)
  }

  const handleViewTrade = (trade) => {
    setSelectedTrade(trade)
  }

  const closeModal = () => {
    setSelectedTrade(null)
  }

  return (
    <div className="trades-page">
      <div className="page-header">
        <h1>Trade History</h1>
      </div>

      {/* Trade Volume Chart */}
      <Card title="Trade Volume">
        <div className="chart-controls">
          <div className="timeframe-selector">
            {timeframeOptions.map((option) => (
              <button
                key={option.value}
                className={`timeframe-button ${timeframe === option.value ? 'active' : ''}`}
                onClick={() => setTimeframe(option.value)}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        <div className="chart-container">
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
              <XAxis 
                dataKey="date" 
                stroke="var(--text-secondary)"
                style={{ fontSize: '0.875rem' }}
              />
              <YAxis 
                stroke="var(--text-secondary)"
                style={{ fontSize: '0.875rem' }}
                tickFormatter={(value) => `$${value.toLocaleString()}`}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'rgba(0, 0, 0, 0.85)',
                  border: '1px solid rgba(102, 126, 234, 0.5)',
                  borderRadius: '8px',
                  color: '#ffffff',
                  padding: '12px',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)'
                }}
                labelStyle={{
                  color: '#ffffff',
                  fontWeight: '600',
                  marginBottom: '4px'
                }}
                itemStyle={{
                  color: '#ffffff'
                }}
                formatter={(value) => [`$${value.toLocaleString()}`, 'Trade Volume']}
                cursor={{ fill: 'rgba(102, 126, 234, 0.1)' }}
              />
              <Legend 
                wrapperStyle={{ color: 'var(--text-primary)' }}
              />
              <Bar 
                dataKey="amount" 
                fill="#667eea" 
                name="Trade Volume (USD)"
                radius={[8, 8, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Trade History Table */}
      <Card title="Recent Trades">
        <div className="trades-table-container">
          {/* Filters */}
          <div className="table-filters">
            <input
              type="text"
              placeholder="Filter by Trade ID..."
              value={filters.tradeId}
              onChange={(e) => handleFilterChange('tradeId', e.target.value)}
              className="filter-input"
            />
            <input
              type="text"
              placeholder="Filter by From Currency..."
              value={filters.fromCurrency}
              onChange={(e) => handleFilterChange('fromCurrency', e.target.value)}
              className="filter-input"
            />
            <input
              type="text"
              placeholder="Filter by To Currency..."
              value={filters.toCurrency}
              onChange={(e) => handleFilterChange('toCurrency', e.target.value)}
              className="filter-input"
            />
          </div>

          {/* Table */}
          <div className="table-wrapper">
            <table className="trades-table">
              <thead>
                <tr>
                  <th onClick={() => handleSort('id')} className="sortable">
                    <div className="th-content">
                      Trade ID
                      <ArrowUpDown size={14} />
                    </div>
                  </th>
                  <th onClick={() => handleSort('fromCurrency')} className="sortable">
                    <div className="th-content">
                      From
                      <ArrowUpDown size={14} />
                    </div>
                  </th>
                  <th onClick={() => handleSort('toCurrency')} className="sortable">
                    <div className="th-content">
                      To
                      <ArrowUpDown size={14} />
                    </div>
                  </th>
                  <th onClick={() => handleSort('usdValue')} className="sortable">
                    <div className="th-content">
                      USD Value
                      <ArrowUpDown size={14} />
                    </div>
                  </th>
                  <th onClick={() => handleSort('date')} className="sortable">
                    <div className="th-content">
                      Date & Time
                      <ArrowUpDown size={14} />
                    </div>
                  </th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {paginatedTrades.length > 0 ? (
                  paginatedTrades.map((trade) => (
                    <tr key={trade.id}>
                      <td className="trade-id">{trade.id}</td>
                      <td>
                        <div className="currency-cell">
                          <span className="currency">{trade.fromCurrency}</span>
                          <span className="amount">{trade.fromAmount}</span>
                        </div>
                      </td>
                      <td>
                        <div className="currency-cell">
                          <span className="currency">{trade.toCurrency}</span>
                          <span className="amount">{trade.toAmount}</span>
                        </div>
                      </td>
                      <td className="usd-value">${parseFloat(trade.usdValue).toLocaleString()}</td>
                      <td className="date-cell">
                        {new Date(trade.date).toLocaleString()}
                      </td>
                      <td>
                        <Button size="small" onClick={() => handleViewTrade(trade)}>
                          View Trade
                        </Button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="6" className="empty-state">
                      No trades found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="pagination">
              <button
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
                className="pagination-button"
              >
                <ChevronLeft size={18} />
                Previous
              </button>
              
              <div className="pagination-info">
                Page {currentPage} of {totalPages} ({sortedTrades.length} trades)
              </div>
              
              <button
                onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
                className="pagination-button"
              >
                Next
                <ChevronRight size={18} />
              </button>
            </div>
          )}
        </div>
      </Card>

      {/* Trade Detail Modal */}
      {selectedTrade && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Trade Details</h2>
              <button onClick={closeModal} className="modal-close">
                <X size={24} />
              </button>
            </div>
            
            <div className="modal-body">
              <div className="detail-row">
                <span className="detail-label">Trade ID:</span>
                <span className="detail-value">{selectedTrade.id}</span>
              </div>
              
              <div className="detail-row">
                <span className="detail-label">Status:</span>
                <span className={`status-badge ${selectedTrade.status}`}>
                  {selectedTrade.status === 'success' ? '✅ Success' : '❌ Failed'}
                </span>
              </div>
              
              <div className="detail-section">
                <h3>Trade Information</h3>
                <div className="detail-row">
                  <span className="detail-label">From:</span>
                  <span className="detail-value">
                    {selectedTrade.fromAmount} {selectedTrade.fromCurrency}
                  </span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">To:</span>
                  <span className="detail-value">
                    {selectedTrade.toAmount} {selectedTrade.toCurrency}
                  </span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">USD Value:</span>
                  <span className="detail-value">
                    ${parseFloat(selectedTrade.usdValue).toLocaleString()}
                  </span>
                </div>
              </div>
              
              <div className="detail-section">
                <h3>Transaction Details</h3>
                <div className="detail-row">
                  <span className="detail-label">Date & Time:</span>
                  <span className="detail-value">
                    {new Date(selectedTrade.date).toLocaleString()}
                  </span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Transaction Hash:</span>
                  <span className="detail-value hash">
                    {selectedTrade.txHash.slice(0, 10)}...{selectedTrade.txHash.slice(-8)}
                  </span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Gas Used:</span>
                  <span className="detail-value">{selectedTrade.gasUsed}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Gas Fee:</span>
                  <span className="detail-value">{selectedTrade.gasFee} ETH</span>
                </div>
              </div>
            </div>
            
            <div className="modal-footer">
              <Button onClick={closeModal}>Close</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Trades
