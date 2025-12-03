import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../contexts/AuthContext'
import TelegramLoginButton from '../components/auth/TelegramLoginButton'
import './Login.css'

const Login = () => {
  const { t } = useTranslation('pages')
  const { t: tCommon } = useTranslation('common')
  const { isAuthenticated, loading } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (isAuthenticated && !loading) {
      navigate('/')
    }
  }, [isAuthenticated, loading, navigate])

  if (loading) {
    return (
      <div className="login-page">
        <div className="login-container">
          <div className="loading">{tCommon('status.loading')}</div>
        </div>
      </div>
    )
  }

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-card">
          <div className="login-header">
            <h1>{t('login.title')}</h1>
            <p>{t('login.subtitle')}</p>
          </div>
          
          <div className="login-content">
            <h2>{t('login.welcomeBack')}</h2>
            <p className="login-description">
              {t('login.description')}
            </p>
            
            <div className="login-widget">
              <TelegramLoginButton 
                botName={import.meta.env.VITE_TELEGRAM_BOT_NAME || 'autosomnia_bot'}
                buttonSize="large"
                requestAccess="write"
              />
            </div>
            
            <div className="login-info">
              <p>
                <strong>{t('login.note')}</strong> {t('login.noteText')}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
