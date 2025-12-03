import { useState, useEffect } from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../contexts/AuthContext'
import Card from '../components/common/Card'
import Table from '../components/common/Table'
import Button from '../components/common/Button'
import accountService from '../services/accountService'
import './Portfolio.css'

const Portfolio = () => {
  const { t } = useTranslation('pages')
  const { t: tCommon } = useTranslation('common')
  const { t: tErrors } = useTranslation('errors')
  const { user } = useAuth()
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState(null)
  const [copiedAddress, setCopiedAddress] = useState(null)
  const [showConfirmDialog, setShowConfirmDialog] = useState(false)

  useEffect(() => {
    if (user?.id) {
      fetchAccounts()
    }
  }, [user])

  const fetchAccounts = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await accountService.getUserAccounts(user.id)
      setAccounts(data.accounts || [])
    } catch (err) {
      console.error('Error fetching accounts:', err)
      setError(err.response?.data?.detail || tErrors('account.loadFailed'))
    } finally {
      setLoading(false)
    }
  }

  const handleAddAccountClick = () => {
    setShowConfirmDialog(true)
  }

  const handleConfirmAddAccount = async () => {
    setShowConfirmDialog(false)
    
    try {
      setCreating(true)
      setError(null)

      // Create new account for the logged-in user
      const accountData = {
        user_id: user.id,
        chain_id: 50312 // Somnia testnet
      }

      const response = await accountService.createAccount(accountData)
      
      console.log('Account created:', response)
      
      // Refresh the accounts list
      await fetchAccounts()
      
    } catch (err) {
      console.error('Error creating account:', err)
      setError(err.response?.data?.detail || tErrors('account.createFailed'))
    } finally {
      setCreating(false)
    }
  }

  const handleCancelAddAccount = () => {
    setShowConfirmDialog(false)
  }

  // Sample token distribution data
  // TODO: Replace with API call in the future
  const tokenDistribution = [
    { name: 'USDT', value: 1500, color: '#26A17B' },
    { name: 'SOMI', value: 2300, color: '#667eea' },
    { name: 'PEPE', value: 450, color: '#48BB78' },
    { name: 'ETH', value: 3200, color: '#627EEA' },
    { name: 'WBTC', value: 1800, color: '#F7931A' }
  ]

  const totalValue = tokenDistribution.reduce((sum, token) => sum + token.value, 0)

  // Generate address distribution data with mock balances
  const addressDistribution = accounts.map((account, index) => {
    // Mock balance values for now
    const mockBalance = Math.floor(Math.random() * 5000) + 500
    const colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#fee140']
    
    return {
      name: `${account.address.slice(0, 6)}...${account.address.slice(-4)}`,
      fullAddress: account.address,
      value: mockBalance,
      color: colors[index % colors.length]
    }
  })

  const totalAddressValue = addressDistribution.reduce((sum, addr) => sum + addr.value, 0)

  const handleCopyAddress = (address) => {
    navigator.clipboard.writeText(address)
      .then(() => {
        setCopiedAddress(address)
        setTimeout(() => setCopiedAddress(null), 2000)
      })
      .catch(err => {
        console.error('Failed to copy address:', err)
      })
  }

  const columns = [
    {
      key: 'address',
      label: t('portfolio.columns.address'),
      render: (value) => (
        <span className="address-cell" title={value}>
          {value.slice(0, 10)}...{value.slice(-8)}
        </span>
      )
    },
    {
      key: 'is_imported',
      label: t('portfolio.columns.type'),
      render: (value) => (
        <span className={`type-badge ${value ? 'imported' : 'created'}`}>
          {value ? t('portfolio.type.imported') : t('portfolio.type.created')}
        </span>
      )
    },
    {
      key: 'created_at',
      label: t('portfolio.columns.created'),
      render: (value) => {
        if (!value) return 'N/A'
        const date = new Date(value)
        return date.toLocaleString()
      }
    },
    {
      key: 'actions',
      label: t('portfolio.columns.actions'),
      render: (value, row) => (
        <div className="action-buttons">
          <div className="copy-button-container">
            <Button
              size="small"
              onClick={() => handleCopyAddress(row.address)}
            >
              {t('portfolio.copyAddress')}
            </Button>
            {copiedAddress === row.address && (
              <span className="copied-notification">{t('portfolio.addressCopied')}</span>
            )}
          </div>
        </div>
      )
    }
  ]

  return (
    <div className="portfolio-page">
      <div className="page-header">
        <div>
          <h1>{t('portfolio.title')}</h1>
          <p className="page-subtitle">{t('portfolio.subtitle')}</p>
        </div>
        <Button onClick={handleAddAccountClick} disabled={creating}>
          {creating ? t('portfolio.creating') : t('portfolio.addAccount')}
        </Button>
      </div>

      {showConfirmDialog && (
        <div className="confirm-dialog-overlay">
          <div className="confirm-dialog">
            <h3>{t('portfolio.confirmTitle')}</h3>
            <p>{t('portfolio.confirmMessage')}</p>
            <div className="confirm-dialog-buttons">
              <Button onClick={handleConfirmAddAccount} disabled={creating}>
                {tCommon('actions.yes')}
              </Button>
              <Button onClick={handleCancelAddAccount} variant="secondary">
                {tCommon('actions.no')}
              </Button>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="error-banner">
          <p>{error}</p>
          <button onClick={() => setError(null)} className="close-button">×</button>
        </div>
      )}

      <Card>
        {loading ? (
          <div className="loading-state">
            <p>{t('portfolio.loadingAccounts')}</p>
          </div>
        ) : accounts.length > 0 ? (
          <>
            <div className="accounts-summary">
              <p className="account-count">
                {t('portfolio.accountCount', { count: accounts.length })}
              </p>
            </div>
            <Table columns={columns} data={accounts} />
          </>
        ) : (
          <div className="empty-state">
            <p>{t('portfolio.noAccounts')}</p>
            <p className="empty-hint">{t('portfolio.noAccountsHint')}</p>
          </div>
        )}
      </Card>

      {/* Charts Section */}
      <div className="portfolio-charts">
        <Card title={t('portfolio.tokenDistribution')}>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={350}>
              <PieChart>
                <Pie
                  data={tokenDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {tokenDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '2px solid #667eea',
                    borderRadius: '8px',
                    color: '#1a202c',
                    padding: '12px',
                    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                    fontWeight: '500'
                  }}
                  labelStyle={{
                    color: '#1a202c',
                    fontWeight: '600',
                    marginBottom: '4px'
                  }}
                  itemStyle={{
                    color: '#1a202c'
                  }}
                  formatter={(value) => [`$${value.toLocaleString()}`, t('portfolio.chartValue')]}
                />
                <Legend
                  verticalAlign="bottom"
                  height={36}
                  formatter={(value, entry) => {
                    const percentage = ((entry.payload.value / totalValue) * 100).toFixed(1)
                    return `${value}: $${entry.payload.value.toLocaleString()} (${percentage}%)`
                  }}
                  wrapperStyle={{ color: 'var(--text-primary)', fontSize: '0.875rem' }}
                />
              </PieChart>
            </ResponsiveContainer>
            
            <div className="token-summary">
              <div className="total-value">
                <span className="label">{t('portfolio.totalPortfolioValue')}</span>
                <span className="value">${totalValue.toLocaleString()}</span>
              </div>
            </div>
          </div>
        </Card>

        <Card title={t('portfolio.addressDistribution')}>
          <div className="chart-container">
            {addressDistribution.length > 0 ? (
              <>
                <ResponsiveContainer width="100%" height={350}>
                  <PieChart>
                    <Pie
                      data={addressDistribution}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {addressDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#ffffff',
                        border: '2px solid #667eea',
                        borderRadius: '8px',
                        color: '#1a202c',
                        padding: '12px',
                        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                        fontWeight: '500'
                      }}
                      labelStyle={{
                        color: '#1a202c',
                        fontWeight: '600',
                        marginBottom: '4px'
                      }}
                      itemStyle={{
                        color: '#1a202c'
                      }}
                      formatter={(value, name, props) => [
                        `$${value.toLocaleString()}`,
                        props.payload.fullAddress
                      ]}
                    />
                    <Legend
                      verticalAlign="bottom"
                      height={36}
                      formatter={(value, entry) => {
                        const percentage = ((entry.payload.value / totalAddressValue) * 100).toFixed(1)
                        return `${value}: $${entry.payload.value.toLocaleString()} (${percentage}%)`
                      }}
                      wrapperStyle={{ color: 'var(--text-primary)', fontSize: '0.875rem' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
                
                <div className="token-summary">
                  <div className="total-value">
                    <span className="label">{t('portfolio.totalBalanceAcrossAddresses')}</span>
                    <span className="value">${totalAddressValue.toLocaleString()}</span>
                  </div>
                </div>
              </>
            ) : (
              <div className="empty-chart-state">
                <p>{t('portfolio.noAccountsToDisplay')}</p>
                <p className="empty-hint">{t('portfolio.addAccountToSeeDistribution')}</p>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  )
}

export default Portfolio
