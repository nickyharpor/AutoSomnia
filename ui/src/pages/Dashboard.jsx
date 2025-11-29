import Card from '../components/common/Card'
import './Dashboard.css'

const Dashboard = () => {
  return (
    <div className="dashboard">
      <div className="stats-grid">
        <Card title="Total Profit">
          <div className="stat-value">145</div>
          <div className="stat-label">US Dollar</div>
        </Card>
        
        <Card title="Total Trades">
          <div className="stat-value">32</div>
          <div className="stat-label">Trades Executed</div>
        </Card>
        
        <Card title="Total Balance">
          <div className="stat-value">861</div>
          <div className="stat-label">US Dollar</div>
        </Card>
        
        <Card title="Total Volume">
          <div className="stat-value">1675</div>
          <div className="stat-label">US Dollar</div>
        </Card>
      </div>
      
      <div className="dashboard-content">
        <Card title="Recent Activity">
          <div className="activity-list">
            <div className="activity-item">
              <div className="activity-icon success">↑</div>
              <div className="activity-details">
                <div className="activity-title">Buy Order Executed</div>
                <div className="activity-meta">BTC/USDT • 2 hours ago</div>
              </div>
              <div className="activity-amount success">+$127.50</div>
            </div>
            
            <div className="activity-item">
              <div className="activity-icon success">↑</div>
              <div className="activity-details">
                <div className="activity-title">Sell Order Completed</div>
                <div className="activity-meta">ETH/USDT • 5 hours ago</div>
              </div>
              <div className="activity-amount success">+$89.20</div>
            </div>
            
            <div className="activity-item">
              <div className="activity-icon error">↓</div>
              <div className="activity-details">
                <div className="activity-title">Stop Loss Triggered</div>
                <div className="activity-meta">SOL/USDT • 8 hours ago</div>
              </div>
              <div className="activity-amount error">-$45.30</div>
            </div>
            
            <div className="activity-item">
              <div className="activity-icon success">↑</div>
              <div className="activity-details">
                <div className="activity-title">Buy Order Executed</div>
                <div className="activity-meta">MATIC/USDT • 1 day ago</div>
              </div>
              <div className="activity-amount success">+$63.15</div>
            </div>
            
            <div className="activity-item">
              <div className="activity-icon success">↑</div>
              <div className="activity-details">
                <div className="activity-title">Sell Order Completed</div>
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
