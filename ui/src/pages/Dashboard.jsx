import { useTranslation } from 'react-i18next'
import Card from '../components/common/Card'
import './Dashboard.css'

const Dashboard = () => {
  const { t } = useTranslation('pages')

  return (
    <div className="dashboard">
      <div className="stats-grid">
        <Card title={t('dashboard.totalProfit')}>
          <div className="stat-value">145</div>
          <div className="stat-label">{t('dashboard.usDollar')}</div>
        </Card>
        
        <Card title={t('dashboard.totalTrades')}>
          <div className="stat-value">32</div>
          <div className="stat-label">{t('dashboard.tradesExecuted')}</div>
        </Card>
        
        <Card title={t('dashboard.totalBalance')}>
          <div className="stat-value">861</div>
          <div className="stat-label">{t('dashboard.usDollar')}</div>
        </Card>
        
        <Card title={t('dashboard.totalVolume')}>
          <div className="stat-value">1675</div>
          <div className="stat-label">{t('dashboard.usDollar')}</div>
        </Card>
      </div>
      
      <div className="dashboard-content">
        <Card title={t('dashboard.recentActivity')}>
          <div className="activity-list">
            <div className="activity-item">
              <div className="activity-icon success">↑</div>
              <div className="activity-details">
                <div className="activity-title">{t('dashboard.buyOrderExecuted')}</div>
                <div className="activity-meta">BTC/USDT • 2 hours ago</div>
              </div>
              <div className="activity-amount success">+$127.50</div>
            </div>
            
            <div className="activity-item">
              <div className="activity-icon success">↑</div>
              <div className="activity-details">
                <div className="activity-title">{t('dashboard.sellOrderCompleted')}</div>
                <div className="activity-meta">ETH/USDT • 5 hours ago</div>
              </div>
              <div className="activity-amount success">+$89.20</div>
            </div>
            
            <div className="activity-item">
              <div className="activity-icon error">↓</div>
              <div className="activity-details">
                <div className="activity-title">{t('dashboard.stopLossTriggered')}</div>
                <div className="activity-meta">SOL/USDT • 8 hours ago</div>
              </div>
              <div className="activity-amount error">-$45.30</div>
            </div>
            
            <div className="activity-item">
              <div className="activity-icon success">↑</div>
              <div className="activity-details">
                <div className="activity-title">{t('dashboard.buyOrderExecuted')}</div>
                <div className="activity-meta">MATIC/USDT • 1 day ago</div>
              </div>
              <div className="activity-amount success">+$63.15</div>
            </div>
            
            <div className="activity-item">
              <div className="activity-icon success">↑</div>
              <div className="activity-details">
                <div className="activity-title">{t('dashboard.sellOrderCompleted')}</div>
                <div className="activity-meta">ADA/USDT • 1 day ago</div>
              </div>
              <div className="activity-amount success">+$52.80</div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}

export default Dashboard
