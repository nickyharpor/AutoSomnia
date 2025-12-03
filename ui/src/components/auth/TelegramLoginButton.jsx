import { useEffect, useRef } from 'react'
import { useAuth } from '../../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import './TelegramLoginButton.css'

const TelegramLoginButton = ({ botName, buttonSize = 'large', requestAccess = 'write' }) => {
  const containerRef = useRef(null)
  const { login } = useAuth()
  const navigate = useNavigate()
  const { t } = useTranslation('errors')

  useEffect(() => {
    // Define the callback function globally
    window.onTelegramAuth = async (user) => {
      console.log('Telegram auth received:', user)
      
      // Call the login function from AuthContext
      const result = await login(user)
      
      if (result.success) {
        console.log('Login successful')
        navigate('/')
      } else {
        console.error('Login failed:', result.error)
        alert(t('auth.loginFailed', { error: result.error }))
      }
    }

    // Create script element
    const script = document.createElement('script')
    script.src = 'https://telegram.org/js/telegram-widget.js?22'
    script.setAttribute('data-telegram-login', botName)
    script.setAttribute('data-size', buttonSize)
    script.setAttribute('data-onauth', 'onTelegramAuth(user)')
    script.setAttribute('data-request-access', requestAccess)
    script.async = true

    // Append script to container
    if (containerRef.current) {
      containerRef.current.appendChild(script)
    }

    // Cleanup
    return () => {
      if (containerRef.current && script.parentNode) {
        containerRef.current.removeChild(script)
      }
      delete window.onTelegramAuth
    }
  }, [botName, buttonSize, requestAccess, login, navigate])

  return (
    <div className="telegram-login-container">
      <div ref={containerRef} className="telegram-login-widget"></div>
    </div>
  )
}

export default TelegramLoginButton
