import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import Card from '../components/common/Card'
import Table from '../components/common/Table'
import accountService from '../services/accountService'
import './Analytics.css'

const Analytics = () => {
  const { user } = useAuth()
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [totalBalance, setTotalBalance] = useState('0')
  const [copiedAddress, setCopiedAddress] = useState(null)

  useEffect(() => {
    if (user?.id) {
      fetchAccountsWithBalances()
    }
  }, [user])

  const fetchAccountsWithBalances = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch user accounts
      const accountsData = await accountService.getUserAccounts(user.id)
      const accountsList = accountsData.accounts || []

      // Fetch balance for each account
      const accountsWithBalances = await Promise.all(
        accountsList.map(async (account) => {
          try {
            const balanceData = await accountService.getBalance(account.address)
            return {
              ...account,
              balance: balanceData.balance_eth || '0',
              balance_wei: balanceData.balance_wei || '0'
            }
          } catch (err) {
            console.error(`Error fetching balance for ${account.address}:`, err)
            return {
              ...account,
              balance: '0',
              balance_wei: '0'
            }
          }
        })
      )

      setAccounts(accountsWithBalances)

      // Calculate total balance
      const total = accountsWithBalances.reduce((sum, account) => {
        return sum + parseFloat(account.balance || 0)
      }, 0)
      setTotalBalance(total.toFixed(6))

    } catch (err) {
      console.error('Error fetching accounts:', err)
      setError(err.response?.data?.detail || 'Failed to load accounts')
    } finally {
      setLoading(false)
    }
  }

  const copyAddress = (address) => {
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
      label: 'Address',
      render: (value) => (
        <div className="address-cell-wrapper">
          <span className="address-cell" title={value}>
            {value.slice(0, 6)}...{value.slice(-4)}
          </span>
          <div className="copy-button-wrapper">
            <button 
              className="copy-button" 
              onClick={() => copyAddress(value)}
            >
              📋
            </button>
            <span className="copy-tooltip">Copy address</span>
            {copiedAddress === value && (
              <span className="copied-message">Address copied!</span>
            )}
          </div>
        </div>
      )
    },
    {
      key: 'balance',
      label: 'Balance (SOMI)',
      render: (value) => (
        <span className="balance-cell">
          {parseFloat(value).toFixed(6)} SOMI
        </span>
      )
    },
    {
      key: 'is_imported',
      label: 'Type',
      render: (value) => (
        <span className={`type-badge ${value ? 'imported' : 'created'}`}>
          {value ? 'Imported' : 'Created'}
        </span>
      )
    },
    {
      key: 'created_at',
      label: 'Created',
      render: (value) => {
        if (!value) return 'N/A'
        const date = new Date(value)
        return date.toLocaleDateString()
      }
    }
  ]

  return (
    <div className="analytics-page">
      <div className="page-header">
        <h1>Account Analytics</h1>
        <p className="page-subtitle">View your accounts and balances</p>
      </div>

      <div className="analytics-summary">
        <Card title="Total Balance">
          <div className="total-balance">
            <span className="balance-amount">{totalBalance}</span>
            <span className="balance-currency">SOMI</span>
          </div>
          <div className="balance-info">
            <span className="account-count">{accounts.length} account{accounts.length !== 1 ? 's' : ''}</span>
          </div>
        </Card>
      </div>

      <Card title="Your Accounts">
        {loading ? (
          <div className="loading-state">
            <p>Loading accounts...</p>
          </div>
        ) : error ? (
          <div className="error-state">
            <p className="error-message">{error}</p>
            <button onClick={fetchAccountsWithBalances} className="retry-button">
              Retry
            </button>
          </div>
        ) : accounts.length === 0 ? (
          <div className="empty-state">
            <p>No accounts found</p>
            <p className="empty-hint">Create an account to get started</p>
          </div>
        ) : (
          <Table columns={columns} data={accounts} />
        )}
      </Card>
    </div>
  )
}

export default Analytics
