import { useState } from 'react'
import Card from '../components/common/Card'
import Button from '../components/common/Button'
import './Settings.css'

const Settings = () => {
  const [selectedStrategy, setSelectedStrategy] = useState('conservative')
  const [applying, setApplying] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  const [exporting, setExporting] = useState(false)
  const [exportMessage, setExportMessage] = useState('')

  const strategies = [
    { 
      id: 'conservative', 
      name: 'Conservative', 
      description: 'Low risk, steady gains with minimal volatility exposure'
    },
    { 
      id: 'balanced', 
      name: 'Balanced', 
      description: 'Moderate risk with balanced approach to growth and stability'
    },
    { 
      id: 'aggressive', 
      name: 'Aggressive', 
      description: 'High risk, high reward strategy for maximum profit potential'
    },
    { 
      id: 'scalping', 
      name: 'Scalping', 
      description: 'Quick trades with small profits, high frequency trading'
    },
    { 
      id: 'swing', 
      name: 'Swing Trading', 
      description: 'Medium-term trades capturing price swings over days or weeks'
    },
    { 
      id: 'arbitrage', 
      name: 'Arbitrage', 
      description: 'Exploit price differences across different exchanges'
    }
  ]

  const handleApplyStrategy = () => {
    setApplying(true)
    setSuccessMessage('')

    // Simulate API call
    setTimeout(() => {
      setApplying(false)
      const strategyName = strategies.find(s => s.id === selectedStrategy)?.name
      setSuccessMessage(`${strategyName} strategy applied successfully!`)
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage('')
      }, 3000)
    }, 800)
  }

  const handleExport = (format) => {
    setExporting(true)
    setExportMessage('')

    // Simulate export process
    setTimeout(() => {
      setExporting(false)
      setExportMessage(`Account data exported successfully as ${format.toUpperCase()}!`)
      
      // Clear export message after 3 seconds
      setTimeout(() => {
        setExportMessage('')
      }, 3000)
    }, 1000)
  }

  return (
    <div className="settings-page">
      <div className="page-header">
        <h1>Settings</h1>
      </div>
      
      <div className="settings-grid">
        <Card title="AI Strategy">
          <div className="setting-item">
            <label>Select Trading Strategy</label>
            <select 
              value={selectedStrategy} 
              onChange={(e) => setSelectedStrategy(e.target.value)}
              className="strategy-select"
            >
              {strategies.map(strategy => (
                <option key={strategy.id} value={strategy.id}>
                  {strategy.name}
                </option>
              ))}
            </select>
            <p className="strategy-description">
              {strategies.find(s => s.id === selectedStrategy)?.description}
            </p>
          </div>
          {successMessage && (
            <div className="success-message">
              {successMessage}
            </div>
          )}
          <Button onClick={handleApplyStrategy} disabled={applying}>
            {applying ? 'Applying...' : 'Apply Strategy'}
          </Button>
        </Card>

        <Card title="Export Data">
          <div className="setting-item">
            <label>Export your account data</label>
            <p className="export-description">
              Download your trading history, account balances, and transaction records in your preferred format.
            </p>
          </div>
          {exportMessage && (
            <div className="success-message">
              {exportMessage}
            </div>
          )}
          <div className="export-buttons">
            <Button 
              onClick={() => handleExport('json')} 
              disabled={exporting}
              variant="secondary"
            >
              {exporting ? 'Exporting...' : 'Export as JSON'}
            </Button>
            <Button 
              onClick={() => handleExport('csv')} 
              disabled={exporting}
              variant="secondary"
            >
              {exporting ? 'Exporting...' : 'Export as CSV'}
            </Button>
          </div>
        </Card>
      </div>
    </div>
  )
}

export default Settings
