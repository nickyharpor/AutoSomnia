import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import Card from '../components/common/Card'
import Button from '../components/common/Button'
import './Settings.css'

const Settings = () => {
  const { t } = useTranslation('pages')
  const [selectedStrategy, setSelectedStrategy] = useState('conservative')
  const [applying, setApplying] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')
  const [exporting, setExporting] = useState(false)
  const [exportMessage, setExportMessage] = useState('')

  const strategies = [
    { 
      id: 'conservative', 
      name: t('settings.aiStrategy.strategies.conservative.name'),
      description: t('settings.aiStrategy.strategies.conservative.description')
    },
    { 
      id: 'balanced', 
      name: t('settings.aiStrategy.strategies.balanced.name'),
      description: t('settings.aiStrategy.strategies.balanced.description')
    },
    { 
      id: 'aggressive', 
      name: t('settings.aiStrategy.strategies.aggressive.name'),
      description: t('settings.aiStrategy.strategies.aggressive.description')
    },
    { 
      id: 'scalping', 
      name: t('settings.aiStrategy.strategies.scalping.name'),
      description: t('settings.aiStrategy.strategies.scalping.description')
    },
    { 
      id: 'swing', 
      name: t('settings.aiStrategy.strategies.swing.name'),
      description: t('settings.aiStrategy.strategies.swing.description')
    },
    { 
      id: 'arbitrage', 
      name: t('settings.aiStrategy.strategies.arbitrage.name'),
      description: t('settings.aiStrategy.strategies.arbitrage.description')
    }
  ]

  const handleApplyStrategy = () => {
    setApplying(true)
    setSuccessMessage('')

    // Simulate API call
    setTimeout(() => {
      setApplying(false)
      const strategyName = strategies.find(s => s.id === selectedStrategy)?.name
      setSuccessMessage(t('settings.aiStrategy.successMessage', { strategy: strategyName }))
      
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
      setExportMessage(t('settings.exportData.successMessage', { format: format.toUpperCase() }))
      
      // Clear export message after 3 seconds
      setTimeout(() => {
        setExportMessage('')
      }, 3000)
    }, 1000)
  }

  return (
    <div className="settings-page">
      <div className="page-header">
        <h1>{t('settings.title')}</h1>
      </div>
      
      <div className="settings-grid">
        <Card title={t('settings.aiStrategy.title')}>
          <div className="setting-item">
            <label>{t('settings.aiStrategy.label')}</label>
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
            {applying ? t('settings.aiStrategy.applying') : t('settings.aiStrategy.applyStrategy')}
          </Button>
        </Card>

        <Card title={t('settings.exportData.title')}>
          <div className="setting-item">
            <label>{t('settings.exportData.label')}</label>
            <p className="export-description">
              {t('settings.exportData.description')}
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
              {exporting ? t('settings.exportData.exporting') : t('settings.exportData.exportJson')}
            </Button>
            <Button 
              onClick={() => handleExport('csv')} 
              disabled={exporting}
              variant="secondary"
            >
              {exporting ? t('settings.exportData.exporting') : t('settings.exportData.exportCsv')}
            </Button>
          </div>
        </Card>
      </div>
    </div>
  )
}

export default Settings
