import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import TelegramLoginButton from '../components/auth/TelegramLoginButton'
import './Login.css'

const Login = () => {
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
          <div className="loading">Loading...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-card">
          <div className="login-header">
            <h1>AutoSomnia</h1>
            <p>Trading Bot Dashboard</p>
          </div>
          
          <div className="login-content">
            <h2>Welcome Back</h2>
            <p className="login-description">
              Sign in with your Telegram account to access the dashboard
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
                <strong>Note:</strong> You need to have a Telegram account to sign in.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
