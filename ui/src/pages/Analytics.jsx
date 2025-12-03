import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../contexts/AuthContext'
import Card from '../components/common/Card'
import Table from '../components/common/Table'
import accountService from '../services/accountService'
import './Analytics.css'

const Analytics = () => {
  const { t } = useTranslation('pages')
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
      label: t('analytics.columns.address'),
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
            <span className="copy-tooltip">{t('analytics.copyAddress')}</span>
            {copiedAddress === value && (
              <span className="copied-message">{t('analytics.addressCopied')}</span>
            )}
          </div>
        </div>
      )
    },
    {
      key: 'balance',
      label: t('analytics.columns.balance'),
      render: (value) => (
        <span className="balance-cell">
          {parseFloat(value).toFixed(6)} {t('analytics.balanceCurrency')}
        </span>
      )
    },
    {
      key: 'is_imported',
      label: t('analytics.columns.type'),
      render: (value) => (
        <span className={`type-badge ${value ? 'imported' : 'created'}`}>
          {value ? t('analytics.type.imported') : t('analytics.type.created')}
        </span>
      )
    },
    {
      key: 'created_at',
      label: t('analytics.columns.created'),
      render: (value) => {
        if (!value) return t('analytics.notAvailable')
        const date = new Date(value)
        return date.toLocaleDateString()
      }
    }
  ]

  return (
    <div className="analytics-page">
      <div className="page-header">
        <h1>{t('analytics.title')}</h1>
        <p className="page-subtitle">{t('analytics.subtitle')}</p>
      </div>

      <div className="analytics-summary">
        <Card title={t('analytics.totalBalance')}>
          <div className="total-balance">
            <span className="balance-amount">{totalBalance}</span>
            <span className="balance-currency">{t('analytics.balanceCurrency')}</span>
          </div>
          <div className="balance-info">
            <span className="account-count">{t('analytics.accountCount', { count: accounts.length })}</span>
          </div>
        </Card>
      </div>

      <Card title={t('analytics.yourAccounts')}>
        {loading ? (
          <div className="loading-state">
            <p>{t('analytics.loadingAccounts')}</p>
          </div>
        ) : error ? (
          <div className="error-state">
            <p className="error-message">{error}</p>
            <button onClick={fetchAccountsWithBalances} className="retry-button">
              {t('analytics.retry')}
            </button>
          </div>
        ) : accounts.length === 0 ? (
          <div className="empty-state">
            <p>{t('analytics.noAccounts')}</p>
            <p className="empty-hint">{t('analytics.noAccountsHint')}</p>
          </div>
        ) : (
          <Table columns={columns} data={accounts} />
        )}
      </Card>
    </div>
  )
}

export default Analytics
